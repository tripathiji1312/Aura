<div align="center">
  <br />
  <h1>✨ Aura</h1>
  <p><b>An AI-Powered Companion for Intelligent Diabetes Management</b></p>
  <p>Aura reduces the daily mental burden of living with diabetes by turning complex health data into clear, proactive, and personalized insights.</p>
  
  <img src="https://i.imgur.com/your-dashboard-screenshot.png" alt="Aura Dashboard Screenshot" width="800"/>
  <p><i>(Image: The main Aura dashboard showing the glucose chart, health score, and AI chat.)</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python" alt="Python Version">
    <img src="https://img.shields.io/badge/Flask-2.2-black?logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/Keras-TensorFlow-red?logo=keras" alt="Keras">
    <img src="https://img.shields.io/badge/PostgreSQL-14-blue?logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  </p>

</div>

---

## 📖 Table of Contents

-   [The Problem & The Solution](#-the-problem--the-solution)
-   [🚀 Core Features](#-core-features)
-   [🛠️ Technology Stack](#️-technology-stack)
-   [🏗️ System Architecture](#️-system-architecture)
-   [⚙️ Getting Started (Local Setup)](#️-getting-started-local-setup)
-   [📁 Project Structure](#-project-structure)
-   [🔌 API Endpoints](#-api-endpoints)
-   [🔮 Future Vision](#-future-vision)

---

## 🎯 The Problem & The Solution

Living with diabetes is a relentless, 24/7 job. It involves constant data logging, carbohydrate counting, insulin calculations, and the persistent anxiety of managing blood sugar levels. Existing tools are often clunky, requiring users to navigate complex forms, which leads to poor adherence and incomplete data.

**Aura transforms this experience.**

It acts as an intelligent companion that understands you. By leveraging modern AI, Aura makes data logging as simple as sending a text message, predicts future glucose trends to prevent problems before they happen, and provides personalized recommendations that adapt to your unique body. Our goal is to empower individuals with diabetes, giving them the confidence and clarity to manage their health effectively.

---

## 🚀 Core Features

Aura is built on a foundation of powerful, interconnected features designed to simplify daily life.

| Feature                      | Description                                                                                                                                                                                                                                                                      |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 💬 **Natural Language AI Chat** | Log meals, exercise, and feelings using plain English. Simply type "**I had a sandwich and an apple for lunch**" and Aura's NLP engine will automatically parse the foods, estimate the carbs, and log the meal. This removes the single biggest barrier to consistent data tracking. |
| 📈 **Predictive Glucose Forecasting** | Aura uses a personalized LSTM neural network to forecast your glucose levels for the next hour. This "weather forecast for your body" helps you proactively manage potential high or low blood sugar events.                                                                         |
| 🤖 **Personalized AI Calibration** | Every person's body is different. With a single click, Aura can fine-tune its prediction model using your unique historical data. This creates a hyper-personalized AI that understands your specific insulin sensitivity and response to food.                                     |
| 💡 **Smart Insulin Recommendations** | Get safe, context-aware insulin dose suggestions. The system combines standard medical formulas with an AI model that factors in your current glucose, carb intake, and recent exercise to provide a reliable recommendation.                                                |
| 💯 **Daily Health Score**         | Instead of just raw numbers, Aura provides a simple, daily "Health Score" from 0-100. This score is based on key metrics like **Time-in-Range** and low-glucose events, giving you an immediate, understandable snapshot of your overall control.                                     |
| 📄 **One-Click PDF Medical Reports** | Instantly generate a clean, professional PDF summary of your recent health data, including glucose charts, meal logs, and key statistics. Perfect for sharing with your doctor to make appointments more efficient and data-driven.                                        |
| 📊 **Interactive Dashboard**       | A beautiful, modern single-page application that visualizes all your key health data in one place. It's fully responsive and includes a dark mode for comfortable viewing anytime.                                                                                               |

---

## 🛠️ Technology Stack

Aura is built with a modern, robust, and scalable technology stack.

-   **Backend:**
    -   **Framework:** Flask
    -   **Database:** PostgreSQL
    -   **Authentication:** Werkzeug for password hashing
-   **Frontend:**
    -   **Languages:** HTML5, CSS3, JavaScript (ES6)
    -   **UI:** Tailwind CSS (via CDN) for a clean, modern design
    -   **Charting:** Chart.js for beautiful and interactive data visualizations
-   **Artificial Intelligence & Machine Learning:**
    -   **Time-Series Prediction:** Keras (with TensorFlow backend) using an LSTM Neural Network
    -   **Natural Language Processing (NLP):** Custom regex and pattern-matching engine (`natural_language_processor.py`)
    -   **Recommendation Engine:** Stable-Baselines3 (DQN Reinforcement Learning model) for insulin dose suggestions
-   **Data & Reporting:**
    -   **Data Generation:** Matplotlib for creating charts for PDF reports
    -   **PDF Generation:** FPDF for creating the downloadable medical reports

---

## 🏗️ System Architecture

The application follows a simple yet powerful client-server architecture.

1.  **Frontend (`combined.html`)**: The user interacts with the single-page application. All actions (logging in, sending a chat message) are sent as API requests to the backend.
2.  **Flask Backend (`app.py`)**: This is the central hub. It handles user authentication, manages API routes, and coordinates with the other services.
3.  **Intelligent Core (`intelligent_core.py`)**: When a user sends a chat message, the backend passes it here. This core service uses the **NLP Processor** to understand the text and then calls the **Prediction Service** and **Recommendation Service** to get AI insights.
4.  **Database (`database.py` & PostgreSQL)**: All user data, glucose readings, meals, and user profiles are stored securely in a PostgreSQL database. The backend services read from and write to this database.
5.  **AI Services (Prediction, NLP, etc.)**: These specialized Python modules handle the heavy lifting of machine learning and data processing, keeping the main `app.py` file clean and focused on API logic.

```
+------------------+      (API Calls)      +-----------------+      (Python Calls)      +------------------------+
|   Frontend       | -------------------> |  Flask Backend  | ---------------------->  |   Intelligent Core     |
| (combined.html)  | <------------------- |    (app.py)     | <----------------------  | (intelligent_core.py)  |
+------------------+      (JSON Data)      +-------+---------+                          +-----------+------------+
                                                   |                                                |
                                                   | (Read/Write)                                   | (Calls NLP, Prediction, Reco)
                                                   v                                                v
                                           +-------+---------+      +--------------------+   +---------------------+   +-----------------------+
                                           |  PostgreSQL DB  |      | NLP Processor      |   | Prediction Service  |   | Recommendation Service|
                                           +-----------------+      +--------------------+   +---------------------+   +-----------------------+
```

---

## ⚙️ Getting Started (Local Setup)

Follow these steps to get Aura running on your local machine.

### Prerequisites

-   Python 3.9 or higher
-   PostgreSQL server installed and running.
-   A Python virtual environment tool (like `venv` or `conda`).

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/aura-project.git
cd aura-project
```

### 2. Set Up a Virtual Environment

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

All required packages are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Configure the Database

1.  Create a new PostgreSQL database (e.g., named `aura_db`).
2.  Open the `config.py` file.
3.  Update the `DATABASE_URL` string with your PostgreSQL username, password, and database name.

    ```python
    # Example for config.py
    DATABASE_URL = "postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/aura_db"
    ```

### 5. Initialize the Database

Run the `database.py` script directly. This will create all the necessary tables.

```bash
python database.py
```

### 6. Run the Backend Server

Start the Flask application. It will run on `http://127.0.0.1:5001` by default.

```bash
python app.py
```

### 7. Launch the Frontend

Open the `combined.html` file in your web browser. You can do this by right-clicking it and selecting "Open with Browser".

You are all set! You can now register a new user, log in, and start using Aura.

---

## 📁 Project Structure

The project is organized into logical modules to ensure clarity and maintainability.

```
.
├── app.py                  # Main Flask application: API routes, user auth.
├── config.py               # Database connection configuration.
├── database.py             # Database schema, queries, and initialization logic.
├── intelligent_core.py     # Central AI module that coordinates NLP and predictions.
├── model_trainer.py        # Logic for fine-tuning the AI model for a specific user.
├── natural_language_processor.py # Parses user chat messages to extract meals/activities.
├── prediction_service.py   # Handles loading models and generating glucose forecasts.
├── recommendation_service.py # Provides insulin dose recommendations.
├── report_generator.py     # Creates the downloadable PDF health reports.
├── simulator.py            # Generates realistic demo data for a user.
│
├── combined.html           # The complete single-page frontend application.
├── requirements.txt        # All Python dependencies for the project.
│
├── *.h5                    # Saved Keras model files (e.g., glucose_predictor.h5).
├── *.gz                    # Saved Scaler files for data normalization.
├── *.zip                   # Saved Reinforcement Learning model file.
└── temp_reports/           # Temporary directory for generated charts and PDFs.
```

---

## 🔌 API Endpoints

Here are the primary API endpoints exposed by the Flask backend.

| Method | Endpoint                    | Description                                         |
| :----- | :-------------------------- | :-------------------------------------------------- |
| `POST` | `/register`                 | Creates a new user account.                         |
| `POST` | `/login`                    | Authenticates a user and returns a user ID.         |
| `POST` | `/api/chat`                 | The core AI endpoint. Processes a user's message.   |
| `GET`  | `/api/dashboard`            | Fetches all data needed for the dashboard display.  |
| `POST` | `/api/ai/calibrate`         | Starts the AI personalization process for a user.   |
| `POST` | `/api/user/report`          | Generates and returns a downloadable PDF report.    |
| `POST` | `/api/dev/simulate-data`    | Populates a user's account with sample demo data.   |

---

## 🔮 Future Vision

Aura is a powerful proof-of-concept with enormous potential for growth. Future enhancements could include:

-   **Real-time CGM Integration:** Connect directly to Continuous Glucose Monitor (CGM) devices (like Dexcom or Libre) for automatic, real-time data streaming.
-   **Doctor-Facing Portal:** A separate dashboard for healthcare providers to monitor their patients' progress and communicate with them securely.
-   **Mobile Applications:** Native iOS and Android apps for an even more seamless user experience.
-   **Advanced Meal Recognition:** Integrate a computer vision model to allow users to log meals by simply taking a photo of their food.
-   **Expanded Health Tracking:** Incorporate other health data streams, such as sleep, stress (from wearables), and medication adherence, for a truly holistic health model.