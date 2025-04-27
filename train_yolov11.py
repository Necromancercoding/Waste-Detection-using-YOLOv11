from ultralytics import YOLO

if __name__ == "__main__":
    # Load a pretrained small YOLOv11 model
    model = YOLO("yolo11s.pt")

    # Train the model
    results = model.train(
        data="C:/waste-detection.v10i.yolov11/data.yaml",  # update path as needed
        epochs=30,
        imgsz=512,          # Try 512 if you get OOM errors
        batch=0.92,           # Autobatch: uses the max batch size your GPU can handle
        workers=8,          # 2-4 is optimal for most laptops
        device=0,           # Use GPU 0
        cache='ram',
        amp=True,           # Use mixed precision for speed/memory savings
        save=True,
        verbose=True
    )
