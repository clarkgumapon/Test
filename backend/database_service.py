from tinydb import TinyDB, Query
from datetime import datetime
import os
import re
import json

class DatabaseService:
    def __init__(self, db_path="images_db.json"):
        """Initialize the non-relational database"""
        self.db_path = db_path
        
        # Remove corrupted database file if it exists
        if os.path.exists(db_path):
            try:
                # Try to open and read the file
                with open(db_path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                # If corrupted, delete the file
                print("Corrupted database found, removing...")
                os.remove(db_path)
                print("Removed corrupted database file")
        
        # Create new database
        self.db = TinyDB(db_path)
        
        # Create collections
        self.images = self.db.table('images')
        self.categories = self.db.table('categories')
        self.search_history = self.db.table('search_history')

    def clean_string(self, s):
        """Clean string to make it JSON-safe"""
        if not isinstance(s, str):
            return str(s)
        # Remove control characters and non-ASCII characters
        return ''.join(char for char in s if ord(char) >= 32 and ord(char) < 127)

    def index_images(self, base_dir):
        """Index all images from the directory into the database"""
        try:
            # Clear existing data
            self.images.truncate()
            self.categories.truncate()
            
            print(f"Starting indexing from: {base_dir}")
            
            # Index all categories and images
            for folder in os.listdir(base_dir):
                try:
                    if '.' in folder:
                        display_name = folder.split('.', 1)[1].strip()
                    else:
                        display_name = folder.strip()
                    
                    # Clean the strings
                    folder = self.clean_string(folder)
                    display_name = self.clean_string(display_name)
                    
                    print(f"Processing category: {display_name}")
                    
                    # Store category
                    category_doc = {
                        'folder_name': folder,
                        'display_name': display_name,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Store images for this category
                    folder_path = os.path.join(base_dir, folder)
                    if os.path.isdir(folder_path):
                        images = []
                        for img_file in os.listdir(folder_path):
                            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                                # Clean the filename
                                clean_filename = self.clean_string(img_file)
                                images.append({
                                    'filename': clean_filename,
                                    'category': display_name,
                                    'folder': folder,
                                    'file_path': os.path.join(folder, clean_filename),
                                    'created_at': datetime.now().isoformat()
                                })
                        
                        # Batch insert images
                        if images:
                            # Insert in smaller batches to avoid memory issues
                            batch_size = 100
                            for i in range(0, len(images), batch_size):
                                batch = images[i:i + batch_size]
                                self.images.insert_multiple(batch)
                    
                    # Store category after confirming it has images
                    if images:
                        category_doc['image_count'] = len(images)
                        self.categories.insert(category_doc)
                        print(f"Indexed {len(images)} images for category: {display_name}")
                
                except Exception as e:
                    print(f"Error indexing {folder}: {e}")
                    continue
            
            print("Indexing completed successfully")
            
        except Exception as e:
            print(f"Error during indexing: {e}")
            # Create empty tables if error occurs
            self.images.truncate()
            self.categories.truncate()

    def search_images(self, query, limit=6):
        """Search for images matching the query"""
        query = self.clean_string(query.lower())
        Image = Query()
        
        # Log the search
        search_log = {
            'query': query,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Find matching images
            results = self.images.search(
                Image.category.test(lambda x: query in x.lower())
            )
            
            # Randomly select up to 'limit' images
            import random
            if len(results) > limit:
                results = random.sample(results, limit)
            
            # Update search log with results count
            search_log['results_count'] = len(results)
            self.search_history.insert(search_log)
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_search_history(self, limit=10):
        """Get recent search history"""
        try:
            history = self.search_history.all()
            # Sort by timestamp (descending) and limit results
            history.sort(key=lambda x: x['timestamp'], reverse=True)
            return history[:limit]
        except Exception as e:
            print(f"Error getting search history: {e}")
            return []

    def get_all_categories(self):
        """Get all categories"""
        try:
            categories = self.categories.all()
            return [cat['display_name'] for cat in categories]
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    def get_category_stats(self):
        """Get statistics about categories"""
        try:
            categories = self.categories.all()
            return {
                'total_categories': len(categories),
                'total_images': sum(cat.get('image_count', 0) for cat in categories),
                'categories': [
                    {
                        'name': cat['display_name'],
                        'image_count': cat.get('image_count', 0)
                    }
                    for cat in categories
                ]
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_categories': 0,
                'total_images': 0,
                'categories': []
            } 