# **💸 Money Lens - Indian Currency Recognizer 💸**

Welcome to **Money Lens**, an open-source project designed to make Indian currency recognition seamless, accessible, and efficient. Using computer vision and machine learning, Money Lens can instantly identify denominations and deliver audio feedback, providing an ideal solution for users ranging from visually impaired individuals to retail workers and educators.

---

## 🚀 **Features**

- **Real-time Currency Detection**: Identify Indian banknotes (₹10, ₹20, ₹50, ₹100, ₹200, ₹500, and ₹2000) through your device camera.
- **Instant Feedback**: Audio feedback for recognized currency makes it accessible for visually impaired users.
- **Image Annotation**: Captured currency images are saved with labeled denominations and confidence scores.
- **Automatic Downloading**: Easily download the latest captured currency image for record-keeping.
- **Fully Open Source**: Built with community collaboration in mind, so anyone can contribute and improve the project.

---

## ⚙️ **Getting Started**

### **Installation**

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/money-lens.git
   cd money-lens


2. Install Dependencies

    Make sure you have Python 3.8+ installed. Then run:
```bash
pip install -r requirements.txt
```

3. Set Up Environment Variables

    Create a .env file in the root directory with the following variables:

       ```bash

    SECRET_KEY=<your-secret-key>
    MY_API_KEY=<your-roboflow-api-key>
```

4. Run the Application

   Start the Flask server:


   python app.py

## 🛠️ Usage
Open the application and allow access to your device’s camera.
Hold up a banknote to the camera and click Capture.
Money Lens will identify the denomination and provide audio feedback.
Download the annotated image of the currency with a single click.

## 🧑‍💻 Contributing
We welcome contributions! Here’s how you can help:

Fork the Repository: Click on the "Fork" button to make a personal copy of the repository.
Clone your Fork: Clone your forked repository to your local machine.
Create a Branch: Make a new branch for your feature or bug fix.
Submit a Pull Request: Push to your fork and submit a pull request describing your changes.
Code of Conduct
Please follow our Code of Conduct to maintain a welcoming and constructive community.

## 📜 License
This project is licensed under the MIT License. See the LICENSE file for more details.

## 🤝 Acknowledgments
Special thanks to:

Roboflow for API support
Open-source communities that inspire collaborative development
## 📢 Join Us!
Whether you’re an experienced developer or just starting out, your contributions make a difference. Let’s make Money Lens the best currency recognition tool together!



