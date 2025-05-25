# ArXiv-Daily-Papers-Feed

## ArXiv Paper Viewer API

This is the backend API for the ArXiv Paper Viewer application, built with FastAPI.

### Prerequisites

*   Python 3.8+
*   pip (Python package installer)

### Setup

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository-url>
    # cd <repository-directory>
    ```

2.  **Create a virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    Install all the required packages from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To run the FastAPI application, use Uvicorn (which was installed as a dependency):

```bash
uvicorn main:app --reload
```

*   `main:app` refers to the `app` instance in the `main.py` file.
*   `--reload` enables auto-reloading when code changes are detected, which is useful for development.

The application will typically be available at `http://127.0.0.1:8000`.

### API Documentation

Once the application is running, you can access the interactive API documentation (provided by Swagger UI) at:
`http://120.0.0.1:8000/docs`

And the alternative API documentation (ReDoc) at:
`http://127.0.0.1:8000/redoc`
