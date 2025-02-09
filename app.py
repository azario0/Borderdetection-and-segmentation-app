import streamlit as st
import cv2
import mediapipe as mp
import tempfile
import os
import subprocess

# Initialize MediaPipe body segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

def process_segmentation(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)  # Reduce the size by half
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)  # Reduce the size by half
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image to get the segmentation mask
        result = mp_selfie_segmentation.process(rgb_frame)

        # Extract segmentation mask
        mask = result.segmentation_mask
        condition = mask > 0.1

        # Apply the mask to the frame
        segmented_frame = cv2.bitwise_and(frame, frame, mask=condition.astype('uint8') * 255)

        # Resize the frame
        resized_frame = cv2.resize(segmented_frame, (width, height))

        # Write the frame to the output video
        out.write(resized_frame)

    cap.release()
    out.release()

def process_edges(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)  # Reduce the size by half
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)  # Reduce the size by half
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame
        resized_frame = cv2.resize(frame, (width, height))

        # Convert to grayscale
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        # Apply Canny edge detection
        edges = cv2.Canny(gray_frame, 100, 200)

        # Convert edges to BGR
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # Write the frame to the output video
        out.write(edges_bgr)

    cap.release()
    out.release()

def convert_to_h264(input_path, output_path):
    command = f"ffmpeg -i {input_path} -vcodec libx264 {output_path}"
    subprocess.run(command, shell=True)

st.title("Video Processing with Body Segmentation and Edge Detection")

st.write("""
    This application allows you to upload a video file and processes it in two stages:
    1. **Body Segmentation**: Detects the human body and segments it from the background.
    2. **Canny Edge Detection**: Applies edge detection on the segmented body.
    
    You can then download the processed videos.
""")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "MOV"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') 
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    st.video(video_path, format="video/mp4", start_time=0)

    st.write("Processing video...")

    # Create unique temporary file paths for processed videos
    temp_dir = tempfile.mkdtemp()
    output_segmentation_path = os.path.join(temp_dir, "segmentation_video.mp4")
    output_edges_path = os.path.join(temp_dir, "edges_video.mp4")
    output_segmentation_h264_path = os.path.join(temp_dir, "segmentation_video_h264.mp4")
    output_edges_h264_path = os.path.join(temp_dir, "edges_video_h264.mp4")

    # Process segmentation
    process_segmentation(video_path, output_segmentation_path)
    # Convert segmentation to H264
    convert_to_h264(output_segmentation_path, output_segmentation_h264_path)
    # Process edges
    process_edges(output_segmentation_h264_path, output_edges_path)
    # Convert edges to H264
    convert_to_h264(output_edges_path, output_edges_h264_path)

    st.write("### Body Segmentation Video")
    if os.path.exists(output_segmentation_h264_path):
        st.video(output_segmentation_h264_path, format="video/mp4", start_time=0)
        with open(output_segmentation_h264_path, 'rb') as file:
            st.download_button('Download Body Segmentation Video', file, file_name="segmentation_video_h264.mp4")
    else:
        st.write("Segmentation video processing failed.")

    st.write("### Canny Edge Detection Video")
    if os.path.exists(output_edges_h264_path):
        st.video(output_edges_h264_path, format="video/mp4", start_time=0)
        with open(output_edges_h264_path, 'rb') as file:
            st.download_button('Download Canny Edge Detection Video', file, file_name="edges_video_h264.mp4")
    else:
        st.write("Edge detection video processing failed.")
