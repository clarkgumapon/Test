import os
from database_service import DatabaseService

class ImageService:
    def __init__(self, base_dir):
        """Initialize the image service with the dataset directory"""
        self.base_dir = base_dir
        self.db = DatabaseService()
        # Index images on startup
        print("Indexing images...")
        self.db.index_images(base_dir)
        print("Indexing complete!")

    def search_images(self, query):
        """Search for images matching the query"""
        return self.db.search_images(query)

    def get_image_path(self, category, filename):
        """Get the full path for an image"""
        return os.path.join(self.base_dir, category, filename)

    def get_all_categories(self):
        """Get list of all available categories"""
        return self.db.get_all_categories()

    def get_search_history(self):
        """Get recent search history"""
        return self.db.get_search_history()

    def get_stats(self):
        """Get database statistics"""
        return self.db.get_category_stats() 