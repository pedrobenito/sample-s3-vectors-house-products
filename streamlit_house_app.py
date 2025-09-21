import streamlit as st
import pandas as pd
import boto3
import time
import os
from dotenv import load_dotenv
from utils import *

load_dotenv()
S3_VECTOR_BUCKET_NAME = os.environ.get("S3_VECTOR_BUCKET_NAME", "house-rooms-bucket")
S3_VECTOR_INDEX_NAME = os.environ.get("S3_VECTOR_INDEX_NAME", "house-rooms-index")

session = boto3.session.Session()
s3vectors = session.client("s3vectors", region_name=session.region_name)

st.set_page_config(page_title="House Room Search", page_icon="🏠", layout="wide")

st.title("🏠 House Room Image Search")
st.markdown("Search for similar house room images using text descriptions or upload your own room image!")

# Sidebar for search options
st.sidebar.header("Search Options")
search_type = st.sidebar.radio("Search Type:", ["Text Search", "Image Search"])
num_results = st.sidebar.slider("Number of Results:", 1, 20, 5)

def search_vectors(query_embedding, k=5):
    try:
        start_time = time.time()
        response = s3vectors.query_vectors(
            vectorBucketName=S3_VECTOR_BUCKET_NAME,
            indexName=S3_VECTOR_INDEX_NAME,
            queryVector={"float32": query_embedding},
            topK=k,
            returnMetadata=True,
            returnDistance=True
        )
        query_time = time.time() - start_time
        return response, query_time
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return None, 0

def display_results(response, query_time):
    if not response or 'vectors' not in response:
        st.warning("No results found")
        return
    
    st.success(f"Found {len(response['vectors'])} results in {query_time:.3f} seconds")
    
    # Display results in columns
    cols = st.columns(min(3, len(response['vectors'])))
    
    for idx, result in enumerate(response['vectors']):
        col_idx = idx % 3
        with cols[col_idx]:
            metadata = result.get('metadata', {})
            
            # Build image path from metadata
            room_type = metadata.get('room_type', 'Unknown')
            filename = metadata.get('filename', 'Unknown')
            
            if room_type != 'Unknown' and filename != 'Unknown':
                img_path = f"/home/ubuntu/.cache/kagglehub/datasets/robinreni/house-rooms-image-dataset/versions/1/House_Room_Dataset/{room_type}/{filename}"
                
                if os.path.exists(img_path):
                    st.image(img_path, width=319)
                else:
                    st.write("🖼️ Image not available")
            else:
                st.write("🖼️ Image not available")
            
            st.write(f"**Room:** {room_type}")
            st.write(f"**File:** {filename}")
            st.write(f"**Similarity:** {result.get('score', 0):.3f}")
            st.divider()

# Text Search
if search_type == "Text Search":
    st.header("🔍 Text Search")
    text_query = st.text_input("Describe the room you're looking for:", 
                              placeholder="e.g., modern kitchen, cozy bedroom, spacious living room")
    
    if st.button("Search") and text_query:
        with st.spinner("Searching..."):
            try:
                embedding_result = get_titan_multimodal_embedding(description=text_query, dimension=1024)
                query_embedding = embedding_result["embedding"]
                
                response, query_time = search_vectors(query_embedding, num_results)
                display_results(response, query_time)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Image Search
elif search_type == "Image Search":
    st.header("📸 Image Search")
    uploaded_file = st.file_uploader("Upload a room image:", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file and st.button("Search"):
        with st.spinner("Processing image and searching..."):
            try:
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Show uploaded image
                st.image(temp_path, caption="Uploaded Image", width=336)
                
                # Generate embedding
                embedding_result = get_titan_multimodal_embedding(image_path=temp_path, dimension=1024)
                query_embedding = embedding_result["embedding"]
                
                # Search
                response, query_time = search_vectors(query_embedding, num_results)
                display_results(response, query_time)
                
                # Clean up
                os.remove(temp_path)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Note about model
st.sidebar.markdown("---")
st.sidebar.markdown("### Model")
st.sidebar.markdown("Using Cohere Embed Multilingual v3 - supports text and images")

# Dataset info in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Dataset Info")
st.sidebar.markdown("""
- **Bathroom**: 606 images
- **Bedroom**: 1,248 images  
- **Dinning**: 1,158 images
- **Kitchen**: 965 images
- **Livingroom**: 1,273 images
- **Total**: 5,250 images
""")