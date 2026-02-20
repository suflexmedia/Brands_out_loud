# Step 04: API Routers

## Objective
Migrate all endpoints that return JSON data from the monolithic `app.py` into separate router modules under `api_routers/`.

## Prerequisites
- Step 02 (Database Handler) and Step 03 (Bucket Handler) completed.

## Implementation Details
1. **Directory Structure**: Inside `api_routers/`, create grouped modules (e.g., `upload.py`, `admin.py`, `blogs.py`, `ads.py`).
2. **FastAPI APIRouter**: In each module, create a `router = APIRouter(prefix="/api/...")`.
3. **Endpoint Migration Example**:
    - Move `/upload_file`, `/delete_file` into `api_routers/upload.py`.
    - Move `/user_register`, `/user_auth`, `/admin_auth` into `api_routers/auth.py`.
    - Move `/admin_save_blog`, `/delete_blog` into `api_routers/admin.py`.
    - Move `/api/organizations`, `/api/ads` into `api_routers/ads.py`.
4. **Pydantic Models**: Replace `request.json` parsing with Pydantic BaseModel definitions to enforce schema typing and validation on requests.
5. **Async DB Calls**: Use the functions created in Step 02 to talk to MongoDB and await their results.

## Research Areas
- **Pydantic Validation**: Look at how the payloads are structured currently in `admin_save_blog` to create an appropriate Pydantic schema.

## Expected Outcome
- The JSON endpoints are available conceptually, validated using Pydantic, and interface functionally with the MongoDB dataset.

## Estimated Effort
2 Days

## Dependencies
- Depends on: Step 02, Step 03
- Depended on by: Step 06
