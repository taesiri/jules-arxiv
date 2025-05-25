function displayPapers(papers, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = ''; // Clear existing content

    if (!papers || papers.length === 0) {
        container.innerHTML = '<p>No papers found.</p>';
        return;
    }

    papers.forEach(paper => {
        const paperDiv = document.createElement('div');
        paperDiv.classList.add('paper-item'); // Optional: for styling

        const title = document.createElement('h3');
        title.textContent = paper.title;

        const authors = document.createElement('p');
        authors.textContent = `Authors: ${paper.authors.map(author => author.name).join(', ')}`;

        const summary = document.createElement('p');
        summary.textContent = paper.summary;

        paperDiv.appendChild(title);
        paperDiv.appendChild(authors);
        paperDiv.appendChild(summary);

        if (paper.pdf_url) {
            const link = document.createElement('a');
            link.href = paper.pdf_url;
            link.textContent = 'Read Paper';
            link.target = '_blank'; // Open in new tab
            paperDiv.appendChild(link);
        } else {
            const noLinkMsg = document.createElement('p');
            noLinkMsg.textContent = 'PDF not available';
            noLinkMsg.style.color = '#666';
            noLinkMsg.style.fontStyle = 'italic';
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
        container.innerHTML = '<p>Error loading papers. Please try again later.</p>';
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
    if (container) container.innerHTML = '<p>Searching for papers...</p>';

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
    } catch (error) {
        console.error('Error searching papers:', error);
        if (container) {
            container.innerHTML = '<p class="error-message">Error searching papers. Please try again later.</p>';
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
