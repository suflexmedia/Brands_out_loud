# Requirements Document

## User's Vision
The user wants to migrate an existing Flask web application ("Brands_out_loud") to FastAPI to improve performance and code maintainability. Along with the framework migration, the backend infrastructure will also be completely overhauled to use self-hosted solutions, moving away from managed services like Supabase.

## Project Scope
1. **Framework Migration**: Migrate the existing backend router system from Flask to FastAPI.
2. **Database Migration**: Swap the current Supabase database layer with a self-hosted MongoDB instance.
3. **Storage Migration**: Swap the current Supabase storage bucket implementation with a self-hosted MinIO instance.

## Application Architecture Constraints
The user has mandated a specific project directory structure to enforce separation of concerns:
- **`app.py`**: The main entry point in the parent directory, initializing the FastAPI application.
- **`api_routers/`**: A folder containing multiple files for JSON-based API endpoints (e.g., retrieving lists, saving data, etc.).
- **`page_serving_routers/`**: A folder containing routes that return HTML templates. This folder must also house static assets (CSS, JavaScript, and some smaller images) and HTML templates (Jinja2).
- **`database_handler/` (or file)**: An abstraction layer to handle operations with the self-hosted MongoDB database.
- **`bucket_handler/` (or file)**: An abstraction layer to handle file uploads/downloads with the self-hosted MinIO service.
- **Existing Config Files**: `railway.json`, `.gitignore`, `requirements.txt` should be kept at the root level and updated as necessary.

## Expected Outcomes
A high-performance, asynchronous FastAPI backend that structurally mirrors the intended architecture, seamlessly interacting with the self-hosted MongoDB and MinIO services.

## Unidentified / To Be Confirmed
- Authentication logic: How is the authentication currently handled, and how should it map to FastAPI (e.g., JWT tokens)?
- The existing Jinja2 templates currently use Flask's `render_template`. We will need to route these through FastAPI's `Jinja2Templates`.
