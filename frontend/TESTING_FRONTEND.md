# Manual Testing Steps for ArXiv Paper Viewer Frontend

## Prerequisites

1.  Ensure the backend FastAPI application is running. You can typically start it with:
    ```bash
    uvicorn main:app --reload
    ```
    (Ensure you are in the root directory of the project where `main.py` is located).
2.  Open your web browser.

## Testing Steps

### 1. Verify Application Loads and Latest Papers are Displayed

*   Navigate to `http://127.0.0.1:8000/` in your web browser.
*   **Expected:**
    *   The page title "ArXiv Paper Viewer" should be visible.
    *   The "Latest Papers" section should be populated with a list of papers.
    *   Each paper should display a title, authors, a summary, and a "Read Paper" link.
    *   If there's an issue fetching papers, an appropriate error message should be shown in the "Latest Papers" section.

### 2. Verify Paper Search Functionality

*   In the "Search Papers" section, enter a keyword (e.g., "quantum computing", "black holes") into the input field.
*   Click the "Search" button.
*   **Expected:**
    *   The "Search Results" section should be populated with papers matching the keyword.
    *   Each paper should display a title, authors, a summary, and a "Read Paper" link.
    *   If no papers are found for the keyword, a "No papers found." message should be displayed in the "Search Results" section.
    *   If the search keyword is empty and the search button is clicked, an alert or message should prompt the user to enter a keyword.
    *   If there's an issue during the search (e.g., backend error), an appropriate error message should be shown in the "Search Results" section.

### 3. Verify "Read Paper" Links

*   For any paper displayed (either in "Latest Papers" or "Search Results"), click the "Read Paper" link.
*   **Expected:**
    *   A new tab or window should open, navigating to the arXiv PDF URL for that paper.

### 4. Error Handling (Simulated)

*   **Backend Down:**
    *   Stop the backend FastAPI application.
    *   Refresh the page or try searching.
    *   **Expected:** The frontend should display an error message in both the "Latest Papers" and "Search Results" sections, indicating that it couldn't connect to the backend or fetch data.
*   **Backend Returns Error (Conceptual - harder to manually simulate without code changes):**
    *   If the backend were to return a 500 error for a valid request, the frontend should gracefully handle this by showing an error message rather than crashing.

## Reporting Issues

*   If any of the above steps do not produce the expected results, please note down the step, the actual result, and any error messages displayed in the browser console (usually accessible via F12 > Console).
