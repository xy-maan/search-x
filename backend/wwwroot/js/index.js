// index.js for search form on home page
// Handles search form submission and displays results on the home page (if needed)
document.getElementById('searchForm')?.addEventListener('submit', function (e) {
	e.preventDefault();
	const query = document.getElementById('searchInput').value.trim();
	const relevance = document.getElementById('relevanceToggle')?.checked ? '1' : '0';
	if (!query) return;
	window.location = `/Home/Results?q=${encodeURIComponent(query)}&relevance=${relevance}`;
});
