# ArXiv-Daily-Papers-Feed

## Frontend API Consumption

The frontend application (`script.js`) is designed to fetch and display a list of ArXiv papers. It currently uses mock data but is structured to consume a backend API endpoint.

### API Endpoint

The frontend expects to fetch data from an API endpoint like:

`/api/papers`

### Data Structure

The API should return a JSON object containing a single key, `"papers"`, whose value is an array of paper objects. Each paper object in the array should have the following structure:

```json
[
  {
    "id": "string_or_integer_identifier",
    "title": "Paper Title",
    "abstract": "A summary of the paper...",
    "pdfUrl": "https://arxiv.pdf/xxxx.xxxxx.pdf"
  }
  // ... more paper objects
]
```

**Field Descriptions:**

*   `id`: (String or Integer) A unique identifier for the paper.
*   `title`: (String) The title of the paper.
*   `abstract`: (String) The abstract or summary of the paper.
*   `pdfUrl`: (String) A direct link to the PDF version of the paper (e.g., from `arxiv.org/pdf/...`).

The `script.js` file uses these fields to populate the paper list and display the details for a selected paper, including embedding the PDF via an `<iframe>`.

