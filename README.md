🍕 Food Ordering System with AI Demand Prediction
==================================================

A full-featured web-based food ordering system with integrated machine learning for demand prediction. Built with Flask, SQLite, and Scikit-learn.


📋 Features
-----------

User Authentication:
- Secure user registration and login system
- Role-based access (Customer / Restaurant Admin)
- Password hashing with Werkzeug
- Forgot Password & Forgot Username with security questions
- CSRF protection on all forms

Customer Features:
- Browse restaurants and food items
- Add items to cart with quantity selection
- Remove items from cart
- Place orders with delivery address
- View order history with expandable order details

Restaurant Admin Features:
- Add, edit, and delete menu items
- Update order status (Pending → Preparing → Delivered)
- View all incoming orders
- Edit restaurant details (name, address, phone, cuisine, opening hours)
- Export orders to CSV

AI Demand Prediction:
- Train machine learning model using historical order data
- Predict future demand for specific food items (next 7 days)
- Identify peak ordering hours
- Display predictions with inventory recommendations
- Business insights dashboard

Analytics & Reporting:
- Most ordered items visualization
- Peak order times detection
- Daily and monthly order trends
- CSV export for order data

Mobile Responsive:
- Fully responsive design
- Optimized for all screen sizes (mobile, tablet, desktop)
- Touch-friendly buttons and forms


🛠️ Technologies Used
--------------------

Backend:
- Python 3.11+
- Flask 2.3.0
- Flask-SQLAlchemy 3.0.5
- Flask-Login 0.6.2
- Flask-WTF 1.1.1

Database:
- SQLite 3.x

Machine Learning:
- Scikit-learn 1.8.0
- Pandas 2.0.1
- NumPy 1.24.3

Frontend:
- HTML5, CSS3, JavaScript
- Bootstrap 5.x

Version Control:
- Git / GitHub


📦 Installation
---------------

Prerequisites:
- Python 3.11 or higher
- Git (optional)
- Virtual environment (recommended)

Step 1: Clone the Repository
-----------------------------
git clone https://github.com/Afaq1267/Online-Food-Ordering-System-with-AI.git
cd Online-Food-Ordering-System-with-AI

Step 2: Create and Activate Virtual Environment
-----------------------------------------------
Windows:
python -m venv venv
venv\Scripts\activate

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies
-----------------------------
pip install -r requirements.txt

Step 4: Set Environment Variables
----------------------------------
Create a .env file in the root directory:

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

Step 5: Run the Application
----------------------------
python app.py

Step 6: Open in Browser
------------------------
Navigate to: http://localhost:5000


🚀 Usage
--------

Register as a User:
1. Go to Register page
2. Choose account type: Customer or Restaurant Owner
3. Fill in the required fields
4. Set a security question and answer (for password recovery)
5. Click Register

Login:
1. Go to Login page
2. Enter your username and password
3. Click Login

As a Customer:
1. Browse restaurants
2. View restaurant menus
3. Add items to cart with desired quantity
4. View cart and update quantities
5. Place order with delivery address
6. View order history

As a Restaurant Admin:
1. Add menu items with name, price, category, and description
2. View incoming orders
3. Update order status
4. Edit restaurant details
5. View AI demand predictions
6. Export orders to CSV

AI Demand Prediction:
1. Place at least 5-10 orders
2. Go to Admin Dashboard
3. Click "AI Demand Prediction"
4. View predictions for next 7 days
5. Get inventory recommendations


📁 Project Structure
--------------------

food-ordering-system/
│
├── app.py                      # Main application file
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
│
├── templates/                   # HTML templates
│   ├── index.html               # Homepage
│   ├── login.html               # Login page
│   ├── register.html            # Registration page
│   ├── forgot_password.html     # Forgot password page
│   ├── forgot_username.html     # Forgot username page
│   ├── reset_password.html      # Reset password page
│   ├── verify_security.html     # Verify security question
│   ├── verify_username_security.html
│   │
│   ├── customer/                # Customer templates
│   │   ├── dashboard.html
│   │   ├── restaurants.html
│   │   ├── menu.html
│   │   ├── cart.html
│   │   └── order_history.html
│   │
│   └── restaurant/              # Restaurant admin templates
│       ├── admin_dashboard.html
│       ├── demand_prediction.html
│       └── edit_restaurant.html
│
├── static/                      # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── backups/                     # Database backups
│
└── venv/                        # Virtual environment (gitignored)


🗄️ Database Schema
------------------

Tables:
- users: User accounts (customers and restaurant admins)
- restaurants: Restaurant information
- menu_items: Food items for each restaurant
- orders: Customer orders
- order_items: Items within each order

Relationships:
- users (1) ----< (M) orders
- users (1) ---- (1) restaurants
- restaurants (1) ----< (M) menu_items
- restaurants (1) ----< (M) orders
- orders (1) ----< (M) order_items
- menu_items (1) ----< (M) order_items


🤖 AI Demand Prediction
----------------------

The system uses Random Forest Regressor from Scikit-learn to predict food demand.

How it Works:
1. Data Collection: Historical order data is collected from the database
2. Feature Engineering: Date, day of week, month, and menu item ID are used as features
3. Model Training: Random Forest model is trained on historical data
4. Prediction: Model predicts demand for the next 7 days
5. Insights: Business insights like peak hours are generated


🔒 Security Features
-------------------

| Feature | Implementation |
|---------|----------------|
| Password Hashing | Werkzeug generate_password_hash() |
| CSRF Protection | Flask-WTF |
| Session Management | Flask-Login |
| SQL Injection Prevention | SQLAlchemy ORM |
| XSS Prevention | Flask escaping |
| Role-based Access | @login_required decorator |


📱 Mobile Responsiveness
------------------------

The application is fully responsive and works on:
- Mobile (320px - 480px)
- Tablet (768px - 1024px)
- Desktop (1024px+)


🧪 Test Summary
---------------

| Module | Test Cases | Passed | Pass Rate |
|--------|------------|--------|-----------|
| Registration | 3 | 3 | 100% |
| Login | 2 | 2 | 100% |
| Cart | 2 | 2 | 100% |
| Order | 2 | 2 | 100% |
| Menu (Admin) | 1 | 1 | 100% |
| AI Prediction | 2 | 2 | 100% |
| Forgot Password | 1 | 1 | 100% |
| Mobile | 1 | 1 | 100% |
| TOTAL | 14 | 14 | 100% |


👥 Contributors
---------------

| Role | Name |
|------|------|
| Project Lead & Developer | [Afaq Haider] |
| QA Tester | Loredana |


📄 License
----------

This project is developed for educational purposes as a university project. All rights reserved.


📞 Contact
----------

For any queries, please contact:
- Email: afaqhaider7861@gmail.com
- GitHub: Afaq1267

📊 Project Status
-----------------

| Status | ✅ Complete |
|--------|-------------|
| Version | 1.0 |
| Last Updated | July 2026 |


Made with ❤️ for Food Lovers and Smart Restaurants! 🍕🤖📊
