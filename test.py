import cv2
import requests
import matplotlib.pyplot as plt
from PIL import Image
import pygame
import os
from roboflow import Roboflow

# Initialize Pygame for sound
pygame.mixer.init()

# Function to play sound based on predicted class
sound_dir = os.path.join(os.path.dirname(__file__), 'sounds')

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
        print(f"Trying to play sound: {full_path}")
        
        try:
            # Check if the file exists before attempting to load it
            if os.path.exists(full_path):
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.play()
                print(f"Playing sound: {full_path}")
            else:
                print(f"Sound file not found: {full_path}")
        except pygame.error as e:
            print(f"Error playing sound: {e}")
    else:
        print("No sound file found for the predicted class.")

# Initialize the Roboflow client
rf = Roboflow(api_key="TCCK6CI1iPvBwCoJmIjO")  # Replace with your actual API key
project = rf.workspace().project("curency-qkufr")  # Replace with your actual project name
model = project.version(1).model  # Specify the model version you are using

# Start video capture from the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Display the resulting frame
    cv2.imshow("Camera Feed", frame)

    # Wait for key press
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('c'):  # Press 'c' to capture image
        # Save the captured frame
        image_path = "current_frame.jpg"
        cv2.imwrite(image_path, frame)
        print("Image captured!")

        # Make prediction on the captured image
        prediction = model.predict(image_path).json()  # Make prediction
        print("Prediction Result:", prediction)

        # Check if predictions exist
        if prediction and 'predictions' in prediction:
            predictions_list = prediction['predictions']
            if predictions_list:
                # Get the predictions dict from the first element
                predictions_dict = predictions_list[0]['predictions']

                # Find the class with the highest confidence
                predicted_class = max(predictions_dict.items(), key=lambda x: x[1]['confidence'])[0]
                confidence_score = predictions_dict[predicted_class]['confidence']

                # Print the top prediction and confidence
                print(f"Predicted class: {predicted_class}, Confidence: {confidence_score}")

                # Play the corresponding sound for the predicted class
                play_sound(predicted_class)

                # Load the original image for visualization
                original_image = Image.open(image_path)

                # Create a figure to show the image and prediction
                plt.imshow(original_image)
                plt.axis('off')  # Turn off axis numbers and ticks

                # Add title with prediction result
                plt.title(f"Predicted class: {predicted_class}, Confidence: {confidence_score:.2f}")

                # Save the new image with the prediction text
                plt.savefig("prediction.jpg", bbox_inches='tight', pad_inches=0)
                plt.show()
            else:
                print("No predictions available.")
        else:
            print("Error: No predictions received or prediction failed.")

    elif key == ord('q'):  # Press 'q' to quit
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
