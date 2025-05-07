// results.js for paginated search results page
function getQueryParam(name) {
	const url = new URL(window.location.href);
	return url.searchParams.get(name) || '';
}
const searchInput = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');
const paginationUl = document.getElementById('pagination');
const relevanceToggle = document.getElementById('relevanceToggle');
const RESULTS_PER_PAGE = 20;
let allResults = [];
let currentPage = 1;
const query = getQueryParam('q');
const relevance = getQueryParam('relevance') === '1';
if (searchInput) searchInput.value = query;
if (relevanceToggle) relevanceToggle.checked = relevance;
async function doSearch(q, rel) {
	if (!q) {
		resultsDiv.innerHTML = '';
		paginationUl.innerHTML = '';
		return;
	}
	resultsDiv.innerHTML = '<div class="text-center text-secondary">Searching...</div>';
	paginationUl.innerHTML = '';
	try {
		const res = await fetch(`/api/search?query=${encodeURIComponent(q)}&relevance=${rel ? '1' : '0'}`);
		const data = await res.json();
		allResults = data;
		currentPage = 1;
		renderResults();
	} catch (err) {
		resultsDiv.innerHTML = '<div class="text-center text-danger">Error fetching results.</div>';
		paginationUl.innerHTML = '';
	}
}
function renderResults() {
	if (!allResults || allResults.length === 0) {
		resultsDiv.innerHTML = '<div class="text-center text-danger">No results found.</div>';
		paginationUl.innerHTML = '';
		return;
	}
	const start = (currentPage - 1) * RESULTS_PER_PAGE;
	const end = start + RESULTS_PER_PAGE;
	const pageResults = allResults.slice(start, end);
	resultsDiv.innerHTML = pageResults.map(r => `
        <div class="card mb-3 p-3">
            <a class="result-link" href="${r.url}" target="_blank">${r.url}</a>
            <div class="result-snippet">${r.snippet || ''}</div>
        </div>
    `).join('');
	renderPagination();
}
function renderPagination() {
	const totalPages = Math.ceil(allResults.length / RESULTS_PER_PAGE);
	if (totalPages <= 1) {
		paginationUl.innerHTML = '';
		return;
	}
	let html = '';
	for (let i = 1; i <= totalPages; i++) {
		html += `<li class="page-item${i === currentPage ? ' active' : ''}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
	}
	paginationUl.innerHTML = html;
	Array.from(paginationUl.querySelectorAll('a.page-link')).forEach(link => {
		link.addEventListener('click', function (e) {
			e.preventDefault();
			const page = parseInt(this.getAttribute('data-page'));
			if (!isNaN(page)) {
				currentPage = page;
				renderResults();
				window.scrollTo({ top: 0, behavior: 'smooth' });
			}
		});
	});
}
if (query) doSearch(query, relevance);
document.getElementById('searchForm')?.addEventListener('submit', function (e) {
	e.preventDefault();
	const q = searchInput.value.trim();
	const rel = relevanceToggle?.checked;
	if (!q) return;
	window.location = `/Home/Results?q=${encodeURIComponent(q)}&relevance=${rel ? '1' : '0'}`;
});
relevanceToggle?.addEventListener('change', function () {
	const q = searchInput.value.trim();
	const rel = relevanceToggle.checked;
	if (!q) return;
	window.location = `/Home/Results?q=${encodeURIComponent(q)}&relevance=${rel ? '1' : '0'}`;
});
