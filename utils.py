import os
import boto3
import time
from pathlib import Path
import json
import base64
from PIL import Image
from io import BytesIO
from typing import List, Union 
from sagemaker.s3 import S3Downloader as s3down
import requests

session = boto3.session.Session()
region = session.region_name

# Define bedrock client
bedrock_client = boto3.client(
    "bedrock-runtime", 
    region, 
    endpoint_url=f"https://bedrock-runtime.{region}.amazonaws.com"
)

s3vectors = boto3.client("s3vectors", region_name=region)

# Select Cohere Embed Multilingual v3 as Embedding model
embed_model = 'cohere.embed-multilingual-v3'

"""Function to generate Embeddings from text or image using Cohere"""
def get_cohere_embedding(
    text:str=None,
    image_path:str=None,
    input_type:str="search_document",
    model_id:str=embed_model
):
    def encode_image_to_data_uri(path):
        if path.startswith('s3'):
            s3 = boto3.client('s3')
            bucket_name, key = path.replace("s3://", "").split("/", 1)
            obj = s3.get_object(Bucket=bucket_name, Key=key)
            image_data = base64.b64encode(obj['Body'].read()).decode('utf-8')
            return f"data:image/jpeg;base64,{image_data}"
        elif path.startswith(('http://', 'https://')):
            response = requests.get(path, stream=True)
            response.raise_for_status()
            image_data = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/jpeg;base64,{image_data}"
        else:   
            with open(path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
                # Detect image format
                if path.lower().endswith('.png'):
                    return f"data:image/png;base64,{image_data}"
                else:
                    return f"data:image/jpeg;base64,{image_data}"
    
    if image_path:
        # Image only - use input_type "image" and only images field
        payload_body = {
            "input_type": "image",
            "images": [encode_image_to_data_uri(image_path)]
        }
    elif text:
        # Text only
        payload_body = {
            "input_type": input_type,
            "texts": [text]
        }
    else:
        raise Exception("Please provide either text or image")

    response = bedrock_client.invoke_model(
        body=json.dumps(payload_body), 
        modelId=model_id,
        accept="application/json", 
        contentType="application/json"
    )

    result = json.loads(response.get("body").read())
    return {"embedding": result["embeddings"][0]}

# Keep backward compatibility with existing function name
def get_titan_multimodal_embedding(
    image_path:str=None,
    description:str=None,
    dimension:int=1024
):
    return get_cohere_embedding(text=description, image_path=image_path, input_type="search_document")

def get_image_from_s3(image_full_path):
    """Download and return image from S3 path"""
    if image_full_path.startswith('s3'):
        try:
            # Create local directory if it doesn't exist
            local_data_root = './data/images'
            os.makedirs(local_data_root, exist_ok=True)
            
            # Download image from S3
            local_file_name = image_full_path.split('/')[-1]
            local_image_path = f"{local_data_root}/{local_file_name}"
            
            # Only download if file doesn't exist locally
            if not os.path.exists(local_image_path):
                s3down.download(image_full_path, local_data_root)
            
            # Open and return image
            img = Image.open(local_image_path)
            return img
        except Exception as e:
            print(f"Error downloading image from S3: {e}")
            return None
    return None

def search_similar_items_from_text(query_prompt, k, vector_bucket_name, index_name):
    """Search for similar items using text query"""
    
    # Get embedding for the query using Cohere
    query_emb = get_cohere_embedding(text=query_prompt, input_type="search_query")["embedding"]
    
    # Measure only the s3vectors.query_vectors API call time
    start_time = time.time()
    response = s3vectors.query_vectors(
        vectorBucketName=vector_bucket_name,
        indexName=index_name,
        queryVector={"float32": query_emb}, 
        topK=k, 
        returnDistance=True,
        returnMetadata=True
    )
    end_time = time.time()
    query_time_ms = (end_time - start_time) * 1000
    
    return response["vectors"], query_time_ms

def search_similar_items_from_image(image_path, k, vector_bucket_name, index_name):
    """Search for similar items using image query"""
    
    # Get embedding for the query image using Cohere
    query_emb = get_cohere_embedding(image_path=image_path, input_type="search_query")["embedding"]
    
    # Measure only the s3vectors.query_vectors API call time
    start_time = time.time()
    response = s3vectors.query_vectors(
        vectorBucketName=vector_bucket_name,
        indexName=index_name,
        queryVector={"float32": query_emb}, 
        topK=k, 
        returnDistance=True,
        returnMetadata=True
    )
    end_time = time.time()
    query_time_ms = (end_time - start_time) * 1000
    
    return response["vectors"], query_time_ms