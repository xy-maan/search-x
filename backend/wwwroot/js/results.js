// results.js for paginated search results page
function getQueryParam(name) {
	const url = new URL(window.location.href);
	return url.searchParams.get(name) || '';
}
const searchInput = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');
const paginationDropdown = document.getElementById('paginationDropdown');
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
		paginationDropdown.style.display = 'none';
		return;
	}
	resultsDiv.innerHTML = '<div class="text-center text-secondary">Searching...</div>';
	paginationDropdown.style.display = 'none';
	try {
		const res = await fetch(`/api/search?query=${encodeURIComponent(q)}&relevance=${rel ? '1' : '0'}`);
		const data = await res.json();
		allResults = data;
		currentPage = 1;
		renderResults();
	} catch (err) {
		resultsDiv.innerHTML = '<div class="text-center text-danger">Error fetching results.</div>';
		paginationDropdown.style.display = 'none';
	}
}
function renderResults() {
	if (!allResults || allResults.length === 0) {
		resultsDiv.innerHTML = '<div class="text-center text-danger">No results found.</div>';
		paginationDropdown.style.display = 'none';
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
	const dropdown = document.getElementById('paginationDropdown');
	const display = document.getElementById('paginationDropdownText');
	if (!dropdown || !display) return;
	dropdown.innerHTML = '';
	if (totalPages <= 1) {
		dropdown.style.display = 'none';
		display.textContent = '';
		return;
	}
	dropdown.style.display = '';
	for (let i = 1; i <= totalPages; i++) {
		const option = document.createElement('option');
		option.value = i;
		option.textContent = `Page ${i}`;
		if (i === currentPage) option.selected = true;
		dropdown.appendChild(option);
	}
	display.textContent = `Page ${currentPage}`;
	dropdown.onchange = function () {
		const page = parseInt(this.value);
		if (!isNaN(page)) {
			currentPage = page;
			display.textContent = `Page ${currentPage}`;
			renderResults();
			window.scrollTo({ top: 0, behavior: 'smooth' });
		}
	};
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
