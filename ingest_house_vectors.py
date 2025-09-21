import boto3
import pandas as pd
import ast
import time
import os
from dotenv import load_dotenv

load_dotenv()
S3_VECTOR_BUCKET_NAME = os.environ.get("S3_VECTOR_BUCKET_NAME", "house-rooms-bucket")
S3_VECTOR_INDEX_NAME = os.environ.get("S3_VECTOR_INDEX_NAME", "house-rooms-index")
dataset_filename = 'house_dataset.csv'
NUM_VECTORS_PER_PUT = 100
NUM_STATUS_PRINT = 200

session = boto3.session.Session()
region = session.region_name
s3vectors = session.client("s3vectors", region_name=region)

try:
    s3vectors.create_vector_bucket(vectorBucketName=S3_VECTOR_BUCKET_NAME)
    print(f"Created vector bucket: {S3_VECTOR_BUCKET_NAME}")
except s3vectors.exceptions.ConflictException:
    print(f"Vector bucket {S3_VECTOR_BUCKET_NAME} already exists")

try:
    s3vectors.create_index(
        vectorBucketName=S3_VECTOR_BUCKET_NAME,
        indexName=S3_VECTOR_INDEX_NAME,
        dataType='float32',
        dimension=1024,
        distanceMetric='cosine',
    )
    print(f"Created index: {S3_VECTOR_INDEX_NAME}")
except s3vectors.exceptions.ConflictException:
    print(f"Index {S3_VECTOR_INDEX_NAME} already exists")

# Read the dataset
dataset = pd.read_csv(dataset_filename)

start_time = time.time()
print("Starting ingestion...")

ingested_count = 0
total_rows = len(dataset)
batch_vectors = []

def create_vector_object(row):
    embedding = ast.literal_eval(row['embedding_img'])
    
    if embedding == 0 or embedding is None:
        return None

    return {
        "key": str(row['id']),
        "data": {"float32": embedding},
        "metadata": {
            "room_type": str(row['room_type']),
            "filename": str(row['filename']),
            "img_full_path": str(row['img_full_path'])
        }
    }

def process_batch(batch):
    global ingested_count
    
    if not batch:
        return

    try:
        s3vectors.put_vectors(
            vectorBucketName=S3_VECTOR_BUCKET_NAME,   
            indexName=S3_VECTOR_INDEX_NAME,
            vectors=batch
        )
        
        ingested_count += len(batch)
        
        if ingested_count % NUM_STATUS_PRINT < NUM_VECTORS_PER_PUT:
            elapsed_minutes = (time.time() - start_time) / 60
            progress = ingested_count / total_rows * 100
            print(f"Progress: {ingested_count} vectors ({progress:.2f}%) - {elapsed_minutes:.2f} minutes")

    except Exception as e:
        print(f"Batch failed: {str(e)}. Processing individually...")
        for vector in batch:
            try:
                s3vectors.put_vectors(
                    vectorBucketName=S3_VECTOR_BUCKET_NAME,   
                    indexName=S3_VECTOR_INDEX_NAME,
                    vectors=[vector]
                )
                ingested_count += 1
            except Exception as e:
                print(f"Error ingesting vector: {str(e)}")

# Process dataset in batches
for index, row in dataset.iterrows():
    vector_obj = create_vector_object(row)
    
    if vector_obj is None:
        print(f"Skipping row {index} - no embedding")
        continue
    
    batch_vectors.append(vector_obj)
    
    if len(batch_vectors) >= NUM_VECTORS_PER_PUT or index == total_rows - 1:
        process_batch(batch_vectors)
        batch_vectors = []

elapsed_minutes = (time.time() - start_time) / 60
print(f"Completed in {elapsed_minutes:.2f} minutes")
print(f"Total vectors ingested: {ingested_count}")