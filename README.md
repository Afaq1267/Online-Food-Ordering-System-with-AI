🍕 Food Ordering System with AI Demand Prediction
==================================================

A full-featured web-based food ordering system with integrated machine learning for demand prediction. Built with Flask, SQLite, and Scikit-learn.


📋 Features
-----------

User Authentication:
• Secure user registration and login system
• Role-based access (Customer / Restaurant Admin)
• Password hashing with Werkzeug
• Forgot Password & Forgot Username with security questions
• CSRF protection on all forms

Customer Features:
• Browse restaurants and food items
• Add items to cart with quantity selection
• Remove items from cart
• Place orders with delivery address
• View order history with expandable order details

Restaurant Admin Features:
• Add, edit, and delete menu items
• Update order status (Pending → Preparing → Delivered)
• View all incoming orders
• Edit restaurant details
• Export orders to CSV

AI Demand Prediction:
• Train machine learning model using historical order data
• Predict future demand for specific food items (next 7 days)
• Identify peak ordering hours
• Display predictions with inventory recommendations
• Business insights dashboard

Analytics & Reporting:
• Most ordered items visualization
• Peak order times detection
• Daily and monthly order trends
• CSV export for order data

Mobile Responsive:
• Fully responsive design
• Optimized for all screen sizes (mobile, tablet, desktop)


🛠️ Technologies Used
--------------------

Backend:          Python 3.11+, Flask 2.3.0, Flask-SQLAlchemy 3.0.5
                  Flask-Login 0.6.2, Flask-WTF 1.1.1

Database:         SQLite 3.x

Machine Learning: Scikit-learn 1.8.0, Pandas 2.0.1, NumPy 1.24.3

Frontend:         HTML5, CSS3, JavaScript, Bootstrap 5.x

Version Control:  Git / GitHub


📦 Installation
---------------

1. Clone the repository
   git clone https://github.com/Afaq1267/Online-Food-Ordering-System-with-AI.git 
   cd Online-Food-Ordering-System-with-AI

2. Create and activate virtual environment
   Windows:   python -m venv venv && venv\Scripts\activate
   Mac/Linux: python3 -m venv venv && source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

4. Run the application
   python app.py

5. Open in browser
   http://localhost:5000


📁 Project Structure
--------------------

food-ordering-system/
│
├── app.py
├── requirements.txt
├── .env
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   ├── forgot_username.html
│   ├── reset_password.html
│   ├── verify_security.html
│   ├── verify_username_security.html
│   │
│   ├── customer/
│   │   ├── dashboard.html
│   │   ├── restaurants.html
│   │   ├── menu.html
│   │   ├── cart.html
│   │   └── order_history.html
│   │
│   └── restaurant/
│       ├── admin_dashboard.html
│       ├── demand_prediction.html
│       └── edit_restaurant.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── backups/
│
└── venv/


🗄️ Database Schema
------------------

Tables:
• users           - User accounts (customers and restaurant admins)
• restaurants     - Restaurant information
• menu_items      - Food items for each restaurant
• orders          - Customer orders
• order_items     - Items within each order

Relationships:
users (1) ----< (M) orders
users (1) ---- (1) restaurants
restaurants (1) ----< (M) menu_items
restaurants (1) ----< (M) orders
orders (1) ----< (M) order_items
menu_items (1) ----< (M) order_items


🤖 AI Demand Prediction
----------------------

Algorithm: Random Forest Regressor (Scikit-learn)

Process:
1. Historical order data is collected from database
2. Features: Date, day of week, month, menu item ID
3. Model predicts demand for next 7 days
4. Business insights (peak hours) are generated


🔒 Security Features
-------------------

• Password Hashing       - Werkzeug generate_password_hash()
• CSRF Protection        - Flask-WTF
• Session Management     - Flask-Login
• SQL Injection Prevent  - SQLAlchemy ORM
• XSS Prevention         - Flask escaping
• Role-based Access      - @login_required decorator


📱 Mobile Responsiveness
------------------------

Works on:
• Mobile   - 320px to 480px
• Tablet   - 768px to 1024px
• Desktop  - 1024px and above


🧪 Test Summary
---------------

Registration    : 3/3 ✅ (100%)
Login           : 2/2 ✅ (100%)
Cart            : 2/2 ✅ (100%)
Order           : 2/2 ✅ (100%)
Menu (Admin)    : 1/1 ✅ (100%)
AI Prediction   : 2/2 ✅ (100%)
Forgot Password : 1/1 ✅ (100%)
Mobile          : 1/1 ✅ (100%)

TOTAL: 14/14 ✅ (100%)


👥 Contributors
---------------

Project Lead & Developer : Afaq Haider
QA Tester                : Loredana


📄 License
----------

This project is developed for educational purposes as a university project. All rights reserved.


📞 Contact
----------

Email  : afaqhaider7861@gmail.com
GitHub : Afaq1267


📊 Project Status
-----------------

Status        : ✅ Complete
Version       : 1.0
Last Updated  : July 2026


Made with ❤️ for Food Lovers and Smart Restaurants! 🍕🤖📊
