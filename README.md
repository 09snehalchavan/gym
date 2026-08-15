# 🏋️ FitTrack Fitness Portal

FitTrack Fitness Portal is a web-based fitness and gym management system developed using **Python Flask**. The system helps manage gym members, fitness-related activities, and administrative operations through separate **Admin and Member** functionalities.

## 🚀 Features

### 👨‍💼 Admin

* Admin Login
* Manage gym members
* Add, update and delete member information
* View member details
* Manage fitness-related records
* Admin dashboard

### 🧑‍🤝‍🧑 Member

* Member Login
* View personal information
* Access fitness-related information
* View available gym services
* Member dashboard

## 🛠️ Technologies Used

* **Backend:** Python, Flask
* **Frontend:** HTML5, CSS3, Bootstrap
* **Database:** MySQL
* **Templating:** Jinja2
* **Tools:** VS Code, Git, GitHub

## 📂 Project Structure

```text
FitTrack-Fitness-Portal/
│
├── static/
├── templates/
├── app.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/09snehalchavan/gym.git
```

### 2. Navigate to the Project Folder

```bash
cd gym
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the Database

Create the required MySQL database and update the database configuration in the Flask application according to your local MySQL credentials.

### 7. Run the Application

```bash
python app.py
```

Then open the application in your browser:

```text
http://127.0.0.1:5000/
```

## 🔐 Login

The application provides separate login functionality for:

* **Admin**
* **Member**

> For security reasons, actual usernames and passwords are not included in this public repository. Use the credentials configured in the application/database.

## 🎯 Project Objective

The main objective of FitTrack Fitness Portal is to provide a simple and efficient web-based platform for managing gym operations and member information while demonstrating practical implementation of **Flask, MySQL, CRUD operations, authentication, templates, and responsive web design**.

## 🔮 Future Enhancements

* Online membership registration
* Workout plan management
* Diet plan management
* Payment and subscription tracking
* Attendance management
* Email notifications
* Fitness progress tracking
* Deployment with a cloud platform

## 👩‍💻 Developer

**Snehal Chavan**

GitHub: https://github.com/09snehalchavan

---

⭐ If you find this project useful, feel free to star the repository!

## 🔐 Demo Credentials

### Admin Login

* 📧 **Email:** `admin@gym.com`
* 🔑 **Password:** `admin@123`

> These credentials are provided for demonstration purposes only.

### 👤 Member Login

Use the member credentials configured in the application for accessing the Member Dashboard.

## 🌐 Live Demo

👉 [https://lnkd.in/ddg-TrVN](https://fittrack-fitness-portal.onrender.com/)
