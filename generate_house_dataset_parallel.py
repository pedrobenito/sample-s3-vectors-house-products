import os
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from dotenv import load_dotenv
from utils import *
import glob

load_dotenv()
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 50))

# Path to the house room dataset
HOUSE_DATASET_PATH = "/home/ubuntu/.cache/kagglehub/datasets/robinreni/house-rooms-image-dataset/versions/1/House_Room_Dataset"

def process_single_image(args):
    idx, image_path, room_type = args
    try:
        result = get_titan_multimodal_embedding(image_path=image_path, dimension=1024)
        embedding = result["embedding"]
    except Exception as e:
        print(f"Error processing image {idx}: {image_path} - {str(e)}")
        embedding = None
    return idx, embedding

# Create dataset from house room images
def create_house_dataset():
    data = []
    
    # Get all room categories
    room_categories = ['Bathroom', 'Bedroom', 'Dinning', 'Kitchen', 'Livingroom']
    
    for room_type in room_categories:
        room_path = os.path.join(HOUSE_DATASET_PATH, room_type)
        image_files = glob.glob(os.path.join(room_path, "*.jpg"))
        
        for image_file in image_files:
            filename = os.path.basename(image_file)
            image_id = filename.replace('.jpg', '')
            
            data.append({
                'id': image_id,
                'room_type': room_type,
                'filename': filename,
                'img_full_path': image_file
            })
    
    return pd.DataFrame(data)

# Create the dataset
print("Creating house room dataset...")
dataset = create_house_dataset()

print(f"Dataset created with {len(dataset)} images")
print("Room distribution:")
print(dataset['room_type'].value_counts())

# Create a list of arguments for each task
tasks = [(idx, row['img_full_path'], row['room_type']) for idx, row in dataset.iterrows()]
multimodal_embeddings_img = [None] * len(tasks)

print("Generating embeddings...")
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_to_idx = {executor.submit(process_single_image, task): task[0] for task in tasks}

    for future in tqdm(concurrent.futures.as_completed(future_to_idx), 
                      total=len(tasks), 
                      desc="Processing images"):
        idx, embedding = future.result()
        multimodal_embeddings_img[idx] = embedding

dataset = dataset.assign(embedding_img=multimodal_embeddings_img)

# Store dataset
dataset.to_csv('house_dataset.csv', index=False)
print("Dataset saved to house_dataset.csv")