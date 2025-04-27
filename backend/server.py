from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import numpy as np
import cv2

# Waste type to dustbin color mapping
DUSTBIN_MAP = {
    "food": "Brown",
    "organic": "Brown",
    "plastic": "Blue",
    "glass": "Green",
    "metal": "Blue",
    "paper": "Blue",
    "hazardous": "Red",
    "e-waste": "Red",
    "non-recyclable": "Black"
}

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
model = YOLO("runs/detect/train/weights/best.pt")

def get_dustbin_color(label):
    for key in DUSTBIN_MAP:
        if key in label.lower():
            return DUSTBIN_MAP[key]
    return "Black"

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    img_bytes = await file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    results = model(img)[0]
    predictions = []
    for box in results.boxes:
        label = model.names[int(box.cls)]
        color = get_dustbin_color(label)
        predictions.append({
            "label": label,
            "confidence": float(box.conf),
            "dustbin_color": color
        })
    return {"predictions": predictions}
