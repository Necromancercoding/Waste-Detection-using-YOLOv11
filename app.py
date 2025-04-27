import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import time
import pandas as pd
from io import BytesIO

# --- Set page config FIRST ---
st.set_page_config(page_title="Smart Waste Detector", layout="centered")

# --- Waste type to dustbin color mapping ---
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

def get_dustbin_color(label):
    for key in DUSTBIN_MAP:
        if key in label.lower():
            return DUSTBIN_MAP[key]
    return "Black"

# --- Load YOLOv11 Model ---
@st.cache_resource
def load_model():
    return YOLO("best.pt")  # Use your weights file

model = load_model()

# --- Session state for logging ---
if "log" not in st.session_state:
    st.session_state["log"] = []

st.title("♻️ Smart Waste Detector (YOLOv11 + Streamlit)")
st.markdown(
    "Upload an image or use your webcam to detect waste type and get the recommended dustbin color. Powered by YOLOv11."
)

# --- Sidebar Settings ---
st.sidebar.header("Settings")
conf = st.sidebar.slider("Detection Confidence", 0.1, 1.0, 0.5, 0.01)
iou = st.sidebar.slider("IoU Threshold", 0.1, 1.0, 0.5, 0.01)

# --- Custom class filtering ---
all_classes = list(model.names.values())
selected_classes = st.sidebar.multiselect(
    "Select classes to detect", options=all_classes, default=all_classes
)

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs(["📷 Webcam", "🖼️ Image Upload", "📊 Session Log & Dashboard"])

# --- Webcam Real-Time Inference ---
with tab1:
    st.subheader("Webcam Real-Time Detection")
    run_webcam = st.checkbox("Enable Webcam", key="webcam_checkbox")
    FRAME_WINDOW = st.empty()
    detected_info = st.empty()

    if run_webcam:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.warning("Webcam not found or not accessible.")
        else:
            while st.session_state.get("webcam_checkbox", False):
                ret, frame = cap.read()
                if not ret:
                    st.warning("Failed to read from webcam.")
                    break
                # YOLO expects BGR or RGB - ultralytics handles both
                results = model.predict(frame, conf=conf, iou=iou, classes=[all_classes.index(cls) for cls in selected_classes if cls in all_classes])
                annotated_frame = results[0].plot()
                FRAME_WINDOW.image(annotated_frame, channels="BGR", use_container_width=True)
                labels = [model.names[int(box.cls)] for box in results[0].boxes]
                if labels:
                    detected_text = "**Detected Waste:**\n"
                    for box in results[0].boxes:
                        label = model.names[int(box.cls)]
                        color = get_dustbin_color(label)
                        detected_text += f"- <b>{label}</b> ({color} dustbin)<br>"
                        # Log detection
                        st.session_state["log"].append({
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "source": "Webcam",
                            "label": label,
                            "confidence": float(box.conf),
                            "dustbin_color": color
                        })
                    detected_info.markdown(detected_text, unsafe_allow_html=True)
                else:
                    detected_info.markdown("")
                # Add a small delay to avoid high CPU usage
                time.sleep(0.15)
            cap.release()
            FRAME_WINDOW.empty()
            detected_info.empty()

# --- Image Upload Inference ---
with tab2:
    st.subheader("Upload an Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        # Convert PIL Image to numpy array
        img_array = np.array(image.convert("RGB"))
        # YOLO expects BGR
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        results = model.predict(img_bgr, conf=conf, iou=iou, classes=[all_classes.index(cls) for cls in selected_classes if cls in all_classes])
        annotated_img = results[0].plot()
        st.image(annotated_img, caption="Detection Result", use_container_width=True)
        # Download annotated image button
        buf = BytesIO()
        Image.fromarray(annotated_img[..., ::-1]).save(buf, format="PNG")
        st.download_button(
            label="Download Annotated Image",
            data=buf.getvalue(),
            file_name="annotated.png",
            mime="image/png"
        )
        # Show detected types and dustbin color
        labels = [model.names[int(box.cls)] for box in results[0].boxes]
        if labels:
            detected_text = "**Detected Waste:**\n"
            for box in results[0].boxes:
                label = model.names[int(box.cls)]
                color = get_dustbin_color(label)
                detected_text += f"- <b>{label}</b> ({color} dustbin)<br>"
                # Log detection
                st.session_state["log"].append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "Image Upload",
                    "label": label,
                    "confidence": float(box.conf),
                    "dustbin_color": color
                })
            st.markdown(detected_text, unsafe_allow_html=True)

# --- Session Log & Dashboard ---
with tab3:
    st.subheader("Session Log & Waste Dashboard")
    log_df = pd.DataFrame(st.session_state["log"])
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True)
        # Waste counting dashboard
        st.markdown("#### Waste Type Count")
        count_df = log_df["label"].value_counts().rename_axis("Waste Type").reset_index(name="Count")
        st.bar_chart(count_df.set_index("Waste Type"))
        # Download log as CSV
        csv = log_df.to_csv(index=False).encode()
        st.download_button(
            label="Download Session Log as CSV",
            data=csv,
            file_name="waste_session_log.csv",
            mime="text/csv"
        )
    else:
        st.info("No detections yet. Use the webcam or upload an image to get started.")

# --- Style ---
st.markdown("""
<style>
    .stButton>button {
        color: white;
        background: #388e3c;
        border-radius: 8px;
        font-size: 1.1rem;
        padding: 0.5rem 1.5rem;
    }
    .stButton>button:hover {
        background: #2e7d32;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
