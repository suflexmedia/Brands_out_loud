import os
from motor.motor_asyncio import AsyncIOMotorClient

class DatabaseHandler:
    """Handles the connection pooling for MongoDB."""
    
    client: AsyncIOMotorClient = None

    @classmethod
    def connect(cls):
        """Initializes the database connection pool."""
        mongo_url = os.getenv("mongo_public_url")
        if not mongo_url:
            raise ValueError("mongo_public_url environment variable is not set.")
        
        # Motor handles connection pooling automatically under the hood
        cls.client = AsyncIOMotorClient(mongo_url)
        print("Connected to MongoDB successfully.")

    @classmethod
    def disconnect(cls):
        """Closes the database connections."""
        if cls.client:
            cls.client.close()
            print("Disconnected from MongoDB.")

    @classmethod
    def get_db(cls, db_name: str = "brands-out-loud"):
        """Returns a reference to the specific database."""
        if not cls.client:
            raise ConnectionError("Database connection has not been initialized.")
        return cls.client[db_name]

db_handler = DatabaseHandler
