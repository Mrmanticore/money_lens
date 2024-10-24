# image_cleaner.py
import os
import time

# Define the downloads folder
downloads_folder = os.path.join(os.getcwd(), 'downloads')
time_limit = 5 * 60  # 5 minutes in seconds

def delete_old_images():
    current_time = time.time()
    if os.path.exists(downloads_folder):
        for filename in os.listdir(downloads_folder):
            file_path = os.path.join(downloads_folder, filename)
            if filename.endswith(('.jpg', '.png', '.jpeg')):
                file_modified_time = os.path.getmtime(file_path)
                if current_time - file_modified_time > time_limit:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
    else:
        print("The downloads folder does not exist.")

def run_cleanup():
    """Run the cleanup task continuously."""
    while True:
        delete_old_images()
        time.sleep(60)  # Check every minute
