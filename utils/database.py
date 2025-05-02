from pymongo import MongoClient, errors

class MongoDBManager:
    
    def __init__(self, db_name="DocumentVerification"):
        try:
            self.client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            # Check connection
            self.client.server_info()
        except errors.ServerSelectionTimeoutError as e:
            raise ConnectionError("Could not connect to MongoDB. Make sure MongoDB is running.") from e
        except Exception as e:
            raise RuntimeError(f"MongoDB connection error: {str(e)}") from e


    def insert_document(self, collection_name, data):
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        try:
            collection = self.db[collection_name]
            collection.insert_one(data)
            return "Data successfully added to the database."
        
        except errors.PyMongoError as e:
            raise RuntimeError(f"Error inserting document into '{collection_name}': {str(e)}") from e

