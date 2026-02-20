# Technology Decisions & Stack

## Core Backend Framework
- **FastAPI**: Chosen for its high performance, native async support, and automatic OpenAPI generation. It directly replaces Flask.
- **Uvicorn**: ASGI web server implementation for Python. Required to run FastAPI.

## Database
- **MongoDB**: A NoSQL document database, chosen by the user to replace Supabase PostgreSQL.
- **Motor**: The official asynchronous Python driver for MongoDB. It integrates perfectly with FastAPI's async paradigms, offering non-blocking database queries without locking the event loop.

## Object Storage
- **MinIO**: High-performance, S3-compatible object storage, chosen to replace Supabase Storage.
- **MinIO Python Client (`minio`)**: The official SDK to interact with the MinIO server, supporting file uploads, downloads, and presigned URLs.

## Templating & Static Files
- **Jinja2**: The templating engine already used in the Flask project. FastAPI supports Jinja2 natively via `fastapi.templating.Jinja2Templates`.
- **Aiofiles**: Required by FastAPI for serving static files asynchronously using `StaticFiles`.

## Security & Validation
- **Pydantic**: Built into FastAPI. Used for data validation, parsing, and serialization. Replaces manual `request.json` parsing in Flask.
- **Passlib & Python-Jose**: For password hashing (replacing custom `sha256_hash` if moving to industry standard) and JWT token generation for user/admin authentication. (To be researched and mapped to existing login logic).

## Deployment & Configuration
- **python-dotenv**: For loading environment variables (MongoDB URI, MinIO credentials) from a `.env` file.
- **Railway**: The project has a `railway.json`. The start command will be updated from a generic python run (presumably) to `uvicorn app:app --host 0.0.0.0 --port $PORT`.

## Research Areas for the Team
- **Migration of Data**: If existing data in Supabase needs to be migrated, a separate ETL script will be required to fetch from Supabase PostgreSQL and insert into MongoDB.
- **Session Management**: If Flask `session` was used, mapping it to stateless JWTs or a MongoDB-backed session store in FastAPI needs to be strictly defined.
