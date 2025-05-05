using Microsoft.AspNetCore.Mvc;
using Backend.Models;
using System.Collections.Generic;

namespace Backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SearchController : ControllerBase
    {
        [HttpGet]
        public ActionResult<IEnumerable<SearchResult>> Get([FromQuery] string query)
        {
            // TODO: Connect to SQL Server and return search results
            return Ok(new List<SearchResult>
            {
                new SearchResult { Url = "https://example.com", Snippet = "Example result for '" + query + "'" }
            });
        }
    }
}
