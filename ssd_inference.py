# -*- coding: utf-8 -*-
"""SSD_inference_evaluation

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Uh9Go4rlcObviDm7ho0NjCCygD9D-uNJ
"""

!pip install torch torchvision
import pandas as pd
import torch
import torchvision
from torchvision import transforms as T
import time
from PIL import Image
import cv2
import os
import json
from google.colab.patches import cv2_imshow
resolution=440

coco_names = ["person" , "bicycle" , "car" , "motorcycle" , "airplane" , "bus" , "train" , "truck" , "boat" , "traffic light" , "fire hydrant" , "street sign" , "stop sign" , "parking meter" , "bench" , "bird" , "cat" , "dog" , "horse" , "sheep" , "cow" , "elephant" , "bear" , "zebra" , "giraffe" , "hat" , "backpack" , "umbrella" , "shoe" , "eye glasses" , "handbag" , "tie" , "suitcase" ,
"frisbee" , "skis" , "snowboard" , "sports ball" , "kite" , "baseball bat" ,
"baseball glove" , "skateboard" , "surfboard" , "tennis racket" , "bottle" ,
"plate" , "wine glass" , "cup" , "fork" , "knife" , "spoon" , "bowl" ,
"banana" , "apple" , "sandwich" , "orange" , "broccoli" , "carrot" , "hot dog" ,
"pizza" , "donut" , "cake" , "chair" , "couch" , "potted plant" , "bed" ,
"mirror" , "dining table" , "window" , "desk" , "toilet" , "door" , "tv" ,
"laptop" , "mouse" , "remote" , "keyboard" , "cell phone" , "microwave" ,
"oven" , "toaster" , "sink" , "refrigerator" , "blender" , "book" ,
"clock" , "vase" , "scissors" , "teddy bear" , "hair drier" , "toothbrush" , "hair brush"]

import torchvision.models.detection as detection

# Load the pre-trained Faster R-CNN model
model = detection.ssd300_vgg16(pretrained=True)
if torch.cuda.is_available():
    model.cuda()  # Move model to GPU
if torch.cuda.is_available():
    print("GPU is available!")
else:
    print("GPU is not available.")

model.eval()

# Replace 'your_file.json' with the path to your actual JSON file
file_path = '/content/drive/MyDrive/files and others for ee/imagesvalidationids.json'

with open(file_path, 'r') as file:
    data = json.load(file)
file_name_to_id = {item['file_name']: item['id'] for item in data}

print(file_name_to_id)

file_path = '/content/drive/MyDrive/files and others for ee/categoriesvalidation.json'
with open(file_path, 'r') as file:
    data = json.load(file)
categoryid_to_name = {item['id']: item['name'] for item in data}

print(categoryid_to_name)

#Accessing validation images from mydrive

obj=[]
times=[]
scrs=[]
boxes=[]
image_names = []
image_id_perdetection=[]
from os import listdir
directory="/content/drive/MyDrive/valid"
for image in os.listdir(directory):
  image_path = "/content/drive/MyDrive/valid/"+image
  #print(image_path) works, every path accessed
  ig = Image.open(image_path)
  new_size = (resolution, resolution)
  ig_resized = ig.resize(new_size)

  # Convert the resized image to tensor
  transform = T.ToTensor()
  img = transform(ig_resized)



  start_time = time.time()

  with torch.no_grad():
    pred = model([img])

  end_time_model = time.time()  # Time after model prediction

  # Apply confidence threshold
  bboxes, labels, scores = pred[0]["boxes"], pred[0]["labels"], pred[0]["scores"]
  keep = scores > 0.5
  bboxes = bboxes[keep]
  labels = labels[keep]
  scores = scores[keep]

  end_time_filtering = time.time()  # Time after filtering

  elapsed_time_model = end_time_model - start_time
  elapsed_time_filtering = end_time_filtering - end_time_model
  elapsed_time_approx = elapsed_time_model + elapsed_time_filtering
  times.append(elapsed_time_approx)

  #print(f"Time taken for model inference: {elapsed_time_model:.3f} seconds")
  #print(f"Time taken for filtering: {elapsed_time_filtering:.3f} seconds")
  #print(f"Approximate inference time for high-confidence objects: {elapsed_time_approx:.3f} seconds")

  num = len(bboxes)  # Update number of detections

  # ... (rest of the code for drawing bounding boxes, etc.)
  #loop for each pred, all preds should be in an array

  image_id = file_name_to_id[image]
  for i in range(num):

    class_name = coco_names[labels.numpy()[i] - 1]

    scores_text = f"{class_name} {scores[i].item():.2f}"  # Corrected here
    int_bbox = bboxes[i].numpy().astype(int)
    boxes.append(int_bbox)
    obj.append(class_name)
    scrs.append(scores[i].item())
    image_id_perdetection.append(image_id)
    #comment this out if you plan to display the images by uncommentingb the cell below

dict = {'image id': image_id_perdetection, 'name': obj, 'bounding box': boxes, 'confidence': scrs }

df = pd.DataFrame(dict)

pd.set_option('display.max_rows', None)  # This will allow all rows to be displayed
pd.set_option('display.max_columns', None)  # This will allow all columns to be displayed

df_sorted = df.sort_values(by='image id', ascending=True)

# If you want to modify the original DataFrame in-place, you can use:
# df.sort_values(by='image id', ascending=True, inplace=True)
df_sorted
#print("\n", elapsed_time_approx,"seconds") figure this out later

#getting data frame from anotated images
file_path = '/content/drive/MyDrive/files and others for ee/modified_data_with_boundingboxes_try2.json'
with open(file_path, 'r') as file:
    data = json.load(file)

extracted_data = []
for item in data:
    extracted_data.append({
        'image id': item['image_id'],
        'name': item['category_id'],
        'bounding box': item['bbox']
    })

df_annot = pd.DataFrame(extracted_data)
df_annot

#whats the main difference?
#why would we want to compare them
#what would be the optimal experimental set up
#whaat kind of data set would we input, the data set needs to be related to the pretraining, how did you get the data set
#ee proposal

# Assuming df_sorted and df_annot are your DataFrames

def calculate_iou(boxA, boxB):
    # Unpack the bounding box coordinates and calculate their areas
    xA, yA, wA, hA = boxA
    xB, yB, wB, hB = boxB
    areaA = wA * hA
    areaB = wB * hB

    # Convert to corner coordinates
    xAmin, yAmin, xAmax, yAmax = xA, yA, xA + wA, yA + hA
    xBmin, yBmin, xBmax, yBmax = xB, yB, xB + wB, yB + hB

    # Calculate intersection coordinates
    xImin = max(xAmin, xBmin)
    yImin = max(yAmin, yBmin)
    xImax = min(xAmax, xBmax)
    yImax = min(yAmax, yBmax)

    # Calculate intersection area
    interArea = max(xImax - xImin, 0) * max(yImax - yImin, 0)

    # Calculate IoU
    iou = interArea / float(areaA + areaB - interArea)
    return iou

# Prepare a list to hold match results
matches = []

# Iterate over each prediction
for index, row in df_sorted.iterrows():
    image_id = row['image id']
    class_name = row['name']
    pred_box = row['bounding box']

    # Filter ground truths for the same image ID and class name
    gt_filtered = df_annot[(df_annot['image id'] == image_id) & (df_annot['name'] == class_name)]

    best_iou = 0
    best_gt = None

    # Compare with each ground truth bounding box
    for _, gt_row in gt_filtered.iterrows():
        gt_box = gt_row['bounding box']
        iou = calculate_iou(pred_box, gt_box)

        if iou > best_iou:
            best_iou = iou
            best_gt = gt_box

    # If a match was found, append it to the matches list
    if best_iou > 0:  # You can set a threshold if needed
        matches.append({
            'image id': image_id,
            'class name': class_name,
            'pred box': pred_box,
            'gt box': best_gt,
            'iou': best_iou
        })

# Convert matches to DataFrame for easier analysis
df_matches = pd.DataFrame(matches)

df_matches

print("number of wrong/duplicate detections: "+ str(len(df_sorted)-len(df_matches)))
print("number of missed detections: "+ str(len(df_annot)-len(df_matches)))

ious = df_matches['iou']
average_iou = sum(ious) / len(ious)
average_time=sum(times) / len(times)
TP = sum(iou > 0.5 for iou in ious)
FP = len(df_sorted) - TP
FN = len(df_annot) - TP


precision = TP / (TP + FP)
recall = TP / (TP + FN)
f1_score = 2 * (precision * recall) / (precision + recall)

print(f"Precision: {precision:.2f} \nRecall: {recall:.2f} \nF1 Score: {f1_score:.2f} \nAverage iou: {average_iou:.2f}\nCorrect Predictions(TP): {TP:.2f} \nMispredictions/duplicate detections(FP): {FP:.2f} \nMissed detections(FN): {FN:.2f} \nAverage time: {average_time:.2f}")

resolution=str(resolution)
data = {
    "Model": ["SSD"],
    "Image resolution": [resolution+" x "+resolution],
    "TP": [TP],
    "FP": [FP],
    "FN": [FN],
    "Precision": [precision],
    "Recall": [recall],
    "F1 Score": [f1_score],
    "Average IoU": [average_iou],
    "Average Time": [average_time]
    }

# Create the DataFrame
df_results = pd.DataFrame(data)
df_results

import numpy as np

# Assuming df_sorted, df_annot, and df_matches are already defined as per your description

# Filter df_matches for IoU >= 0.5
df_matches_filtered = df_matches[df_matches['iou'] >= 0.5]

# Define a function to calculate Average Precision (AP) for a class
def calculate_AP(precision_recall_points):
    # Sort by recall
    precision_recall_points.sort(key=lambda x: x[0])
    # Add a point for recall = 0 with precision = 1
    precision_recall_points.insert(0, (0, 1))
    # Add a point for recall = 1 with the last precision
    precision_recall_points.append((1, precision_recall_points[-1][1]))

    # Calculate the area under the curve using the trapezoidal rule
    ap = 0
    for i in range(1, len(precision_recall_points)):
        recall_diff = precision_recall_points[i][0] - precision_recall_points[i-1][0]
        precision_avg = (precision_recall_points[i][1] + precision_recall_points[i-1][1]) / 2
        ap += recall_diff * precision_avg
    return ap

# Get unique classes
unique_classes = df_sorted['name'].unique()
APs = {}

for class_name in unique_classes:
    class_preds = df_sorted[df_sorted['name'] == class_name]
    class_gts = df_annot[df_annot['name'] == class_name].shape[0]

    TP = FP = 0
    precision_recall_points = []

    for _, pred in class_preds.iterrows():
        # Convert 'pred box' to a tuple for comparison
        pred_box_tuple = tuple(pred['bounding box'])

        # Adjusted .apply() to compare 'pred box' tuples
        match = df_matches_filtered.apply(lambda x: x['class name'] == class_name and tuple(x['pred box']) == pred_box_tuple, axis=1)

        if match.any():
            TP += 1
        else:
            FP += 1

        precision = TP / (TP + FP) if TP + FP > 0 else 0
        recall = TP / class_gts if class_gts > 0 else 0
        precision_recall_points.append((recall, precision))

    # Calculate AP for this class, using your calculate_AP function
    APs[class_name] = calculate_AP(precision_recall_points)

# Calculate mAP by averaging APs
mAP = np.mean(list(APs.values()))
print(f"mAP (IoU >= 0.5): {mAP:.4f}")

df_results["mAP"]=[mAP]
df_results

file_path_csv = '/content/drive/MyDrive/files and others for ee/model_evaluation_empty.csv'  # Replace with your actual file path

# Append the DataFrame to the existing CSV without including the header
df_results.to_csv(file_path_csv, mode='a', index=False, header=False)

print(resolution)

