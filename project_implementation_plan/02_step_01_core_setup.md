# Step 01: Core Setup & Configuration

## Objective
Set up the raw structure for the FastAPI project, define dependencies, and configure environment variables.

## Prerequisites
- A working Python environment (preferably standard `venv` or `poetry`).
- Basic `.env` file containing MongoDB strings, MinIO credentials, and JWT secrets.

## Implementation Details
1. **Initialize Directory Structure**: Create `api_routers`, `page_serving_routers`, `database_handler`, and `bucket_handler` directories.
2. **Move Static Asset**s: Move existing `static` and `templates` into `page_serving_routers/`.
3. **Update `requirements.txt`**: Keep generic dependencies but replace `Flask`, `supabase` with `fastapi`, `uvicorn`, `motor`, `minio`, `pydantic`, `python-dotenv`, `python-multipart`, `aiofiles`, `Jinja2`.
4. **Update `railway.json`**: Change run commands to `uvicorn app:app --host 0.0.0.0 --port $PORT`.
5. **Base `app.py`**: Create a barebones FastAPI app instance.

## Research Areas
- Check how the current `.env` loading is handled natively vs deploying on Railway.
- Check exactly which third-party packages in `requirements.txt` can be stripped (e.g., Flask-specific extensions).

## Expected Outcome
- The new project directory is structurally ready.
- `pip install -r requirements.txt` succeeds.
- Running `uvicorn app:app` starts a blank FastAPI server successfully on localhost.

## Estimated Effort
0.5 Days

## Dependencies
- None. This is the first step.
