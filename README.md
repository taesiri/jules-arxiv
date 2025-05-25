# ArXiv-Daily-Papers-Feed

## ArXiv Paper Viewer API

This is the backend API for the ArXiv Paper Viewer application, built with FastAPI.

### Prerequisites

*   Python 3.8+
*   uv (Python package and project manager)

### Setup

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository-url>
    # cd <repository-directory>
    ```

2.  **Install uv (if not already installed):**
    ```bash
    # On macOS and Linux:
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Or via pip:
    # pip install uv
    ```

3.  **Install dependencies:**
    uv will automatically manage the virtual environment and install dependencies:
    ```bash
    uv sync
    ```

### Running the Application

To run the FastAPI application using uv:

```bash
uv run uvicorn main:app --reload
```

*   `main:app` refers to the `app` instance in the `main.py` file.
*   `--reload` enables auto-reloading when code changes are detected, which is useful for development.

The application will typically be available at `http://127.0.0.1:8000`.

### API Documentation

Once the application is running, you can access the interactive API documentation (provided by Swagger UI) at:
`http://127.0.0.1:8000/docs`

And the alternative API documentation (ReDoc) at:
`http://127.0.0.1:8000/redoc`
