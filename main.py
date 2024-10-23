import os
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, flash
from roboflow import Roboflow
import pygame
import threading
import time
import os
from dotenv import load_dotenv
import sqlite3
from flask import send_file, abort

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Database setup: create database if not exists
DATABASE = 'contact.db'

# Initialize Pygame for sound
pygame.mixer.init()

# Roboflow API Setup (Replace with your API key and project version)
rf = Roboflow(api_key=os.getenv("MY_API_KEY"))  # Replace with your API key
project = rf.workspace().project("curency-qkufr")  # Replace with your project
model = project.version(1).model  # Replace with the actual version

# Define sound directory
sound_dir = os.path.join(os.path.dirname(__file__), 'static', 'sounds')

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
# Function to capture frame and make prediction
def capture_and_predict(frame):
    # Path to save the captured image in "captured_images" folder
    image_path = "captured_images/current_frame.jpg"
    cv2.imwrite(image_path, frame)

    start_time = time.time()

    try:
        # Make prediction using the Roboflow model
        prediction = model.predict(image_path).json()

        # Check if there are any predictions
        if 'predictions' in prediction and len(prediction['predictions']) > 0:
            predictions = prediction['predictions'][0]['predictions']
            predicted_class = max(predictions, key=lambda x: predictions[x]['confidence'])
            confidence_score = predictions[predicted_class]['confidence']

            # Set a confidence threshold (e.g., 70%)
            if confidence_score >= 0.7:
                # Annotate and save the image with predictions in the downloads folder
                save_annotated_image(frame, predicted_class, confidence_score)

                # Play the sound for the predicted class in a separate thread
                threading.Thread(target=play_sound, args=(predicted_class,)).start()

                return predicted_class, confidence_score
        return "No Note", 0.0
    except Exception as e:
        print(f"Error during prediction: {e}")
        return "No Note", 0.0


# Function to save the annotated image
# Function to save the annotated image with a white background
def save_annotated_image(frame, predicted_class, confidence_score):
    # Ensure the "downloads" folder exists
    downloads_folder = os.path.join(os.getcwd(), 'downloads')
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)

    # Create a white background image of the same size as the frame
    height, width, _ = frame.shape
    white_background = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Annotate the image with class and confidence score using OpenCV
    cv2.putText(white_background, f"Class: {predicted_class}, Confidence: {confidence_score:.2f}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)  # Black text

    # Overlay the original frame on the white background
    # You can choose to blend or simply place the frame on the white background
    # For this case, we will use a simple overlay
    white_background[0:height, 0:width] = frame

    # Path to save the annotated image in the downloads folder
    output_image_path = os.path.join(downloads_folder, f"{predicted_class}_{int(time.time())}.jpg")
    cv2.imwrite(output_image_path, white_background)

    print(f"Annotated image saved to: {output_image_path}")




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

# Initialize the database if it doesn't exist
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS contacts
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           email TEXT NOT NULL,
                           subject TEXT NOT NULL,
                           message TEXT NOT NULL)''')
        conn.commit()
        conn.close()

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




@app.route('/latest_image')
def latest_image():
    downloads_folder = os.path.join(os.getcwd(), 'downloads')  # Make sure the path is absolute
    try:
        # Ensure the directory exists
        if not os.path.exists(downloads_folder):
            return "Downloads folder does not exist", 404

        # Get the latest image file
        files = [f for f in os.listdir(downloads_folder) if f.endswith('.jpg') or f.endswith('.png')]
        if not files:
            return "No image found", 404

        # Sort files by creation time and get the latest one
        latest_file = max([os.path.join(downloads_folder, f) for f in files], key=os.path.getctime)

        # Send the latest image file with correct MIME type
        return send_file(latest_file, as_attachment=True)  # Forces download

    except Exception as e:
        print(f"Error fetching latest image: {e}")
        abort(500, description="Error fetching image")


# Initialize the database
init_db()

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route to handle form submission
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    # Insert the form data into SQLite database
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (name, email, subject, message) VALUES (?, ?, ?, ?)",
                       (name, email, subject, message))
        conn.commit()
        conn.close()

        flash('Your message has been sent successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')

    return redirect(url_for('contact'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    if not os.path.exists('captured_images'):
        os.makedirs('captured_images')
    app.run(debug=True)
