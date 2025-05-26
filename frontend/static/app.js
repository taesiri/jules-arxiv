function displayPapers(papers, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = ''; // Clear existing content

    if (!papers || papers.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="mt-2">No papers found.</p>
            </div>
        `;
        return;
    }

    papers.forEach(paper => {
        const paperDiv = document.createElement('div');
        paperDiv.className = 'bg-gray-50 rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow';

        const title = document.createElement('h4');
        title.className = 'text-lg font-semibold text-gray-900 mb-3 leading-tight';
        title.textContent = paper.title;

        const authors = document.createElement('p');
        authors.className = 'text-sm text-gray-600 mb-3';
        authors.innerHTML = `<span class="font-medium">Authors:</span> ${paper.authors.map(author => author.name).join(', ')}`;

        const summary = document.createElement('p');
        summary.className = 'text-gray-700 text-sm leading-relaxed mb-4';
        summary.textContent = paper.summary;

        paperDiv.appendChild(title);
        paperDiv.appendChild(authors);
        paperDiv.appendChild(summary);

        if (paper.pdf_url) {
            const linkContainer = document.createElement('div');
            linkContainer.className = 'flex items-center justify-between';

            const link = document.createElement('a');
            link.href = paper.pdf_url;
            link.className = 'inline-flex items-center px-4 py-2 bg-arxiv-blue text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors';
            link.innerHTML = `
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Read Paper
            `;
            link.target = '_blank';

            linkContainer.appendChild(link);
            paperDiv.appendChild(linkContainer);
        } else {
            const noLinkMsg = document.createElement('p');
            noLinkMsg.className = 'text-gray-500 text-sm italic';
            noLinkMsg.textContent = 'PDF not available';
            paperDiv.appendChild(noLinkMsg);
        }

        container.appendChild(paperDiv);
    });
}

async function fetchLatestPapers() {
    const containerId = 'latest-papers-list';
    try {
        const response = await fetch('/papers/latest');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const papers = await response.json();
        displayPapers(papers, containerId);
    } catch (error) {
        console.error('Error fetching latest papers:', error);
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <div class="text-center py-8 text-red-500">
                <svg class="mx-auto h-12 w-12 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="mt-2">Error loading papers. Please try again later.</p>
            </div>
        `;
    }
}

async function searchPapers() {
    console.log('searchPapers function called'); // Debug log

    const keywordInput = document.getElementById('search-keyword');
    const searchButton = document.getElementById('search-button');
    const container = document.getElementById('search-results-list');

    if (!keywordInput) {
        console.error('Search keyword input not found!');
        return;
    }

    const keyword = keywordInput.value.trim();

    console.log('Search keyword:', keyword); // Debug log

    if (!keyword) {
        alert('Please enter a search keyword.');
        return;
    }

    // Show loading state
    if (searchButton) searchButton.disabled = true;
    if (searchButton) searchButton.textContent = 'Searching...';
    if (container) container.innerHTML = `
        <div class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-arxiv-blue"></div>
            <span class="ml-3 text-gray-600">Searching for papers...</span>
        </div>
    `;

    try {
        console.log('Making fetch request to:', `/papers/search?keyword=${encodeURIComponent(keyword)}`); // Debug log
        const response = await fetch(`/papers/search?keyword=${encodeURIComponent(keyword)}`);
        console.log('Response status:', response.status); // Debug log

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const papers = await response.json();
        console.log('Received papers:', papers.length); // Debug log
        displayPapers(papers, 'search-results-list');
        // Switch to search results tab
        if (typeof switchTab === 'function') {
            switchTab('search');
        }
    } catch (error) {
        console.error('Error searching papers:', error);
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <svg class="mx-auto h-12 w-12 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p class="mt-2">Error searching papers. Please try again later.</p>
                </div>
            `;
        }
    } finally {
        // Reset button state
        if (searchButton) {
            searchButton.disabled = false;
            searchButton.textContent = 'Search';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM content loaded'); // Debug log
    fetchLatestPapers();

    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-keyword');

    if (searchButton) {
        console.log('Search button found, adding click listener'); // Debug log
        searchButton.addEventListener('click', searchPapers);
    } else {
        console.error('Search button not found!');
    }

    if (searchInput) {
        console.log('Search input found, adding Enter key listener'); // Debug log
        searchInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                console.log('Enter key pressed in search input'); // Debug log
                searchPapers();
            }
        });
    } else {
        console.error('Search input not found!');
    }
});
