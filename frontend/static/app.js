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

        const link = document.createElement('a');
        link.href = paper.pdf_url;
        link.textContent = 'Read Paper';
        link.target = '_blank'; // Open in new tab

        paperDiv.appendChild(title);
        paperDiv.appendChild(authors);
        paperDiv.appendChild(summary);
        paperDiv.appendChild(link);

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
    const keywordInput = document.getElementById('search-keyword');
    const keyword = keywordInput.value.trim();
    const containerId = 'search-results-list';

    if (!keyword) {
        alert('Please enter a search keyword.');
        // Or display message in the container:
        // const container = document.getElementById(containerId);
        // container.innerHTML = '<p>Please enter a keyword to search.</p>';
        return;
    }

    try {
        const response = await fetch(`/papers/search?keyword=${encodeURIComponent(keyword)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const papers = await response.json();
        displayPapers(papers, containerId);
    } catch (error) {
        console.error('Error searching papers:', error);
        const container = document.getElementById(containerId);
        container.innerHTML = '<p>Error searching papers. Please try again later.</p>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchLatestPapers();

    const searchButton = document.getElementById('search-button');
    if (searchButton) {
        searchButton.addEventListener('click', searchPapers);
    }
});
