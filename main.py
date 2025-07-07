import os
import logging
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    logger.info(f"Health check from {request.remote_addr}")
    return jsonify({
        "status": "healthy",
        "service": "pokemon-webhook-v2",
        "environment": os.getenv('RAILWAY_ENVIRONMENT', 'development')
    })

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Unhandled error: {error}", exc_info=True)
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
