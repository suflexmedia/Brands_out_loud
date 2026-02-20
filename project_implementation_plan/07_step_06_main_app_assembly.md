# Step 06: Main App Assembly

## Objective
Tie together the modular components (routers, handlers, templates) into the main `app.py` executable.

## Prerequisites
- All previous steps completed.

## Implementation Details
1. **Initialize FastAPI**: Create the root `app = FastAPI(title="Brands Out Loud")` inside the top-level `app.py`.
2. **Include Routers**:
    ```python
    from api_routers import auth, admin, blogs, ads
    from page_serving_routers import pages
    
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(pages.router)
    ```
3. **Mount Static Files**:
    ```python
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="page_serving_routers/static"), name="static")
    ```
4. **Middleware (Optional)**: If CORS is needed for the frontend (or if running headless API), add `CORSMiddleware`.
5. **Startup/Shutdown Events**: Wire up the MongoDB connection pool and MinIO client health checks on app startup.
6. **Error Handlers**: Add custom exception handlers for 404s (serving a template instead of JSON) as is present currently in Flask.

## Expected Outcome
- Running `uvicorn app:app --reload` gives a fully functional application mirroring the old Flask app but using FastAPI, MongoDB, and MinIO.

## Estimated Effort
1 Day

## Dependencies
- Depends on: Step 04, Step 05
