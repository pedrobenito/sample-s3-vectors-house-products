# House Products Vector Search

A Streamlit application for semantic search of house room images using AWS S3 Vectors.

## Features
- Text-based semantic search for room images
- Image similarity search using uploaded images
- AWS S3 Vectors integration for fast vector search
- Interactive web interface with Streamlit
- Support for 5,250+ house room images across 5 categories

## Dataset
The application uses a house rooms dataset with:
- **Bathroom**: 606 images
- **Bedroom**: 1,248 images  
- **Dining**: 1,158 images
- **Kitchen**: 965 images
- **Living room**: 1,273 images
- **Total**: 5,250 images

## Technology Stack
- **Frontend**: Streamlit
- **Vector Search**: AWS S3 Vectors
- **Embeddings**: Cohere Embed Multilingual v3 (via Amazon Bedrock)
- **Image Processing**: PIL (Pillow)
- **AWS Services**: Bedrock, S3 Vectors

## Setup

### Prerequisites
- AWS account with access to Bedrock and S3 Vectors
- Python 3.8+
- AWS credentials configured

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/pedrobenito/sample-s3-vectors-house-products.git
   cd sample-s3-vectors-house-products
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS configuration
   ```

4. Run the application:
   ```bash
   streamlit run streamlit_house_app.py
   ```

## Usage

### Text Search
1. Select "Text Search" in the sidebar
2. Enter a description of the room you're looking for (e.g., "modern kitchen", "cozy bedroom")
3. Adjust the number of results using the slider
4. Click "Search" to find similar rooms

### Image Search
1. Select "Image Search" in the sidebar
2. Upload an image of a room (PNG, JPG, JPEG)
3. Adjust the number of results using the slider
4. Click "Search" to find visually similar rooms

## Architecture
The application uses:
- **Cohere Embed Multilingual v3** for generating embeddings from text and images
- **AWS S3 Vectors** for storing and querying vector embeddings
- **Streamlit** for the web interface
- **Amazon Bedrock** for accessing the embedding model

## Files
- `streamlit_house_app.py` - Main Streamlit application
- `utils.py` - Utility functions for embeddings and search
- `ingest_house_vectors.py` - Script to ingest images and create vector index
- `generate_house_dataset_parallel.py` - Script to generate dataset with embeddings
- `requirements.txt` - Python dependencies

## License
This project is open source and available under the MIT License.