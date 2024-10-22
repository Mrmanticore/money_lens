import os
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify
from roboflow import Roboflow
import pygame
import threading
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Pygame for sound
pygame.mixer.init()


# Roboflow API Setup (Replace with your API key and project version)
rf = Roboflow(api_key = os.getenv("MY_API_KEY"))  # Replace with your API key
project = rf.workspace().project("curency-qkufr")  # Replace with your project
model = project.version(1).model  # Replace with the actual version

# Define sound directory
sound_dir = os.path.join(os.path.dirname(__file__), 'statics', 'sounds')

# Function to play sound based on predicted class (non-blocking)
def play_sound(predicted_class):
    sound_file_mapping = {
        'class10': '10.mp3',
        'class20': '20.mp3',
        'class50': '50.mp3',
        'class100': '100.mp3',
        'class200': '200.mp3',
        'class500': '500.mp3',
        'class2000': '2000.mp3'
    }

    sound_file = sound_file_mapping.get(predicted_class, None)
    if sound_file:
        full_path = os.path.join(sound_dir, sound_file)
        if os.path.exists(full_path):
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.play()

# Function to capture frame and make prediction
def capture_and_predict(frame):
    image_path = "captured_images/current_frame.jpg"
    cv2.imwrite(image_path, frame)

    start_time = time.time()

    # Make prediction using the Roboflow model
    prediction = model.predict(image_path).json()

    # Timeout handling (e.g., 5 seconds timeout)
    if time.time() - start_time > 5:
        return "No Note", 0.0

    # Check if there are any predictions
    if len(prediction['predictions']) > 0:
        predictions = prediction['predictions'][0]['predictions']
        predicted_class = max(predictions, key=lambda x: predictions[x]['confidence'])
        confidence_score = predictions[predicted_class]['confidence']

        # Set a confidence threshold (e.g., 90%)
        if confidence_score >= 0.9:
            # Play the sound for the predicted class in a separate thread
            threading.Thread(target=play_sound, args=(predicted_class,)).start()
            return predicted_class, confidence_score
        else:
            return "No Note", 0.0
    else:
        return "No Note", 0.0

# Generate live camera feed with reduced resolution (640x480)
def gen_frames():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Yield the frame to be displayed
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture_image():
    # Capture and process the current frame
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ret, frame = cap.read()
    if not ret:
        return jsonify({'error': 'Failed to capture image'}), 500

    # Predict class and confidence
    predicted_class, confidence_score = capture_and_predict(frame)

    cap.release()
    return jsonify({
        'predicted_class': predicted_class,
        'confidence_score': confidence_score
    })

if __name__ == '__main__':
    if not os.path.exists('captured_images'):
        os.makedirs('captured_images')
    app.run(debug=True)
