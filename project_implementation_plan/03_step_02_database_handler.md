# Step 02: Database Handler (MongoDB)

## Objective
Migrate all Supabase PostgreSQL database logic into a self-hosted MongoDB wrapper using the `motor` async library.

## Prerequisites
- Step 01 completed.
- Access to a running MongoDB instance.

## Implementation Details
1. **Create `database_handler.py`** (or `database_handler/` package if complex).
2. **Connection Logic**: Setup a singleton or connection pool to MongoDB on `startup` event using `motor.motor_asyncio.AsyncIOMotorClient`.
3. **Data Model Porting**: Currently the app has functions like `save_blogs_to_db`, `get_category_page` DB queries, etc. We must rebuild these as Python `async def` functions querying Mongo collections (`blogs`, `pages`, `users`, `ads`, `organizations`).
4. **Auth Porting**: Convert Supabase's user authentication (e.g. `user_login_db_check`) into a MongoDB lookup combined with hashed password checks (`passlib`).

## Research Areas
- **Supabase Auto-incrementing IDs**: MongoDB uses `ObjectId`. The team must decide whether to migrate to `ObjectId` string references entirely, or implement custom auto-incrementing integer IDs in Mongo (usually discouraged).
- **Data Migration**: How to export the existing Supabase Postgres data and load it into MongoDB collections.

## Expected Outcome
- A functional `database_handler` file with standalone async functional tests verifying connection and CRUD operations targeting the MongoDB instance.

## Estimated Effort
1 - 2 Days

## Dependencies
- Depends on: Step 01
- Depended on by: Step 04, Step 05
