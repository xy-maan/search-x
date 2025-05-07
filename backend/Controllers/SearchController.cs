using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Data.SqlClient;
using Microsoft.Extensions.Configuration;
using System.Linq;
using System.Threading.Tasks;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SearchController : ControllerBase
    {
        private readonly string _connectionString;
        public SearchController(IConfiguration configuration)
        {
            _connectionString = configuration.GetConnectionString("DefaultConnection")
                ?? configuration.GetConnectionString("MSSQL")
                ?? "Server=TOSHIBA-L50-C\\MSSQLSERVER19;Database=SearchX;Trusted_Connection=True;";
        }

        [HttpGet]
        public async Task<IActionResult> Get([FromQuery] string query, [FromQuery] string relevance = "1")
        {
            if (string.IsNullOrWhiteSpace(query))
                return Ok(new List<object>());

            var words = query.ToLower().Split(' ', '\t', '\n', '\r').Where(w => !string.IsNullOrWhiteSpace(w)).ToArray();
            if (words.Length == 0)
                return Ok(new List<object>());

            var results = new List<object>();
            using (var conn = new SqlConnection(_connectionString))
            {
                await conn.OpenAsync();
                // Get total number of pages for TF-IDF calculation
                double totalPages = 1;
                using (var countCmd = new SqlCommand("SELECT COUNT(*) FROM Pages", conn))
                {
                    totalPages = Convert.ToDouble(await countCmd.ExecuteScalarAsync());
                }
                string sql;
                if (words.Length == 1) // Single word
                {
                    if (relevance == "1")
                    {
                        sql = @"SELECT p.url, SUM(ii.tf * LOG(@totalPages / w.df)) AS score
                                FROM Pages p
                                INNER JOIN InvertedIndex ii ON p.id = ii.page_id
                                INNER JOIN Words w ON ii.word = w.word
                                WHERE ii.word = @w0
                                GROUP BY p.url
                                ORDER BY score DESC;";
                    }
                    else
                    {
                        sql = @"SELECT p.url
                                FROM Pages p
                                INNER JOIN InvertedIndex ii ON p.id = ii.page_id
                                WHERE ii.word = @w0
                                GROUP BY p.url;";
                    }
                }
                else // Multi-word
                {
                    if (relevance == "1")
                    {
                        sql = $@"SELECT p.url, SUM(ii.tf * LOG(@totalPages / w.df)) AS score
                                FROM Pages p
                                INNER JOIN InvertedIndex ii ON p.id = ii.page_id
                                INNER JOIN Words w ON ii.word = w.word
                                WHERE ii.word IN ({string.Join(",", words.Select((w, i) => "@w" + i))})
                                GROUP BY p.url
                                HAVING COUNT(DISTINCT ii.word) = @wordCount
                                ORDER BY score DESC;";
                    }
                    else
                    {
                        sql = $@"SELECT p.url
                                FROM Pages p
                                INNER JOIN InvertedIndex ii ON p.id = ii.page_id
                                WHERE ii.word IN ({string.Join(",", words.Select((w, i) => "@w" + i))})
                                GROUP BY p.url
                                HAVING COUNT(DISTINCT ii.word) = @wordCount;";
                    }
                }
                using (var cmd = new SqlCommand(sql, conn))
                {
                    for (int i = 0; i < words.Length; i++)
                        cmd.Parameters.AddWithValue("@w" + i, words[i]);
                    if (words.Length > 1)
                        cmd.Parameters.AddWithValue("@wordCount", words.Length);
                    if (relevance == "1")
                        cmd.Parameters.AddWithValue("@totalPages", totalPages);
                    cmd.CommandTimeout = 30;
                    using (var reader = await cmd.ExecuteReaderAsync())
                    {
                        while (await reader.ReadAsync())
                        {
                            string url = reader["url"].ToString();
                            double score = reader.FieldCount > 1 && reader["score"] != DBNull.Value ? Convert.ToDouble(reader["score"]) : 0;
                            results.Add(new { Url = url, Score = score });
                        }
                    }
                }
            }
            return Ok(results);
        }
    }
}
