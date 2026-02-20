# Step 03: Bucket Handler (MinIO)

## Objective
Implement file upload/download mechanisms mapping to MinIO instead of Supabase Storage.

## Prerequisites
- Step 01 completed.
- Credentials to a locally or self-hosted MinIO server.

## Implementation Details
1. **Create `bucket_handler.py`**.
2. **MinIO Client Initialization**: Use the `minio.Minio` python client using environment variables.
3. **Core Functions**:
    - `upload_file_to_storage`: Accept FastAPI `UploadFile`, read async via `aiofiles` or standard `.read()`, and upload to specific MinIO buckets (e.g., `blog-images`, `magazine-pdfs`, `organization-resources`).
    - `delete_file_from_storage`: Removes the specified file from a MinIO bucket.
    - Serve files either directly through presigned URLs, a public MinIO bucket, or proxy them via FastAPI.

## Research Areas
- **Bucket Public Access**: Identify if MinIO buckets should have public access policies configured so the frontend can retrieve images directly via URL (highly recommended for performance), bypassing the FastAPI server logic. This changes how the database stores URLs (stores direct MinIO public URLs).

## Expected Outcome
- The `bucket_handler.py` successfully uploads and returns retrieve URLs for sample images.

## Estimated Effort
0.5 Days

## Dependencies
- Depends on: Step 01
- Depended on by: Step 04
