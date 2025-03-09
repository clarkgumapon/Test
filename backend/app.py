from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from image_service import ImageService
import os

class SearchApp:
    def __init__(self):
        """Initialize the Flask application"""
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize image service
        self.image_service = ImageService(r"C:\Users\Administrator\Downloads\256_ObjectCategories")
        
        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register all application routes"""
        
        @self.app.route('/')
        def home():
            stats = self.image_service.get_stats()
            return jsonify({
                "status": "Server is running",
                "stats": stats
            })

        @self.app.route('/search')
        def search():
            query = request.args.get('q', '')
            results = self.image_service.search_images(query)
            return jsonify(results)

        @self.app.route('/search/history')
        def search_history():
            history = self.image_service.get_search_history()
            return jsonify(history)

        @self.app.route('/image/<category>/<filename>')
        def serve_image(category, filename):
            try:
                image_path = os.path.join(r"C:\Users\Administrator\Downloads\256_ObjectCategories", category, filename)
                print(f"Attempting to serve image: {image_path}")  # Debug log
                if os.path.exists(image_path):
                    return send_file(image_path, mimetype='image/jpeg')
                print(f"Image not found: {image_path}")  # Debug log
                return 'Image not found', 404
            except Exception as e:
                print(f"Error serving image: {e}")
                return str(e), 500

    def run(self, host='0.0.0.0', port=5000, debug=True):
        """Run the Flask application"""
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    search_app = SearchApp()
    search_app.run(debug=True) 