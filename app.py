from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_ordering.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==================== DATABASE MODELS ====================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    
    security_question = db.Column(db.String(200))
    security_answer = db.Column(db.String(200))

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    opening_hours = db.Column(db.String(100))
    cuisine = db.Column(db.String(50))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.String(200))
    is_available = db.Column(db.Boolean, default=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    total_amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    delivery_address = db.Column(db.String(200))
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    quantity = db.Column(db.Integer)
    price_at_time = db.Column(db.Float)
    menu_item = db.relationship('MenuItem', backref='order_items')

# ==================== DEMAND PREDICTOR ====================

class DemandPredictor:
    def __init__(self):
        self.model = None
        self.model_path = 'demand_model.pkl'
    
    def train(self, orders_df):
        if orders_df is None or len(orders_df) < 5:
            return None
        try:
            orders_df_copy = orders_df.copy()
            orders_df_copy['order_time'] = pd.to_datetime(orders_df_copy['order_time'])
            orders_df_copy['day'] = orders_df_copy['order_time'].dt.day
            orders_df_copy['month'] = orders_df_copy['order_time'].dt.month
            
            daily_demand = orders_df_copy.groupby(['day', 'month', 'menu_item_id'])['quantity'].sum().reset_index()
            if len(daily_demand) < 3:
                return None
            
            X = daily_demand[['day', 'month', 'menu_item_id']].values
            y = daily_demand['quantity'].values
            
            self.model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.model.fit(X, y)
            joblib.dump(self.model, self.model_path)
            return self.model
        except Exception as e:
            print(f"Training error: {e}")
            return None
    
    def predict(self, menu_item_id, days=7):
        if self.model is None and os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        if self.model is None:
            return [0] * days
        
        try:
            predictions = []
            current_date = datetime.now()
            for i in range(days):
                future_date = current_date + timedelta(days=i+1)
                features = [[future_date.day, future_date.month, menu_item_id]]
                pred = self.model.predict(features)[0]
                predictions.append(max(0, int(round(pred))))
            return predictions
        except Exception as e:
            print(f"Prediction error: {e}")
            return [0] * days
    
    def get_insights(self, orders_df):
        if orders_df is None or len(orders_df) == 0:
            return {'peak_hours': [], 'total_orders': 0}
        try:
            orders_df_copy = orders_df.copy()
            orders_df_copy['order_time'] = pd.to_datetime(orders_df_copy['order_time'])
            orders_df_copy['hour'] = orders_df_copy['order_time'].dt.hour
            peak_hours = orders_df_copy.groupby('hour').size().nlargest(3).index.tolist()
            return {'peak_hours': peak_hours, 'total_orders': len(orders_df_copy)}
        except Exception as e:
            print(f"Insights error: {e}")
            return {'peak_hours': [], 'total_orders': 0}

predictor = DemandPredictor()

# ==================== HELPER FUNCTIONS ====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        # Check credentials
        if user and user.password == password:
            # Successful login
            login_user(user)
            session['user_id'] = user.id
            flash(f'Welcome back, {username}!', 'success')
            
            if user.user_type == 'customer':
                return redirect(url_for('customer_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            # Failed login - Show invalid credentials message
            flash('❌ Invalid username or password. Please try again.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        security_question = request.form.get('security_question')
        security_answer = request.form.get('security_answer')
        
        # PASSWORD VALIDATION - ADD THIS BLOCK
        if len(password) < 6:
            flash('❌ Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Please choose a different username.', 'error')
            return render_template('register.html')
        
        # Check if email exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered! Please use a different email.', 'error')
            return render_template('register.html')
        
        # Validate security fields
        if not security_question or not security_answer:
            flash('Please select a security question and provide an answer.', 'error')
            return render_template('register.html')
        
        # Create user
        user = User(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            security_question=security_question,
            security_answer=security_answer.lower().strip()
        )
        db.session.add(user)
        db.session.commit()
        
        # If restaurant owner, create restaurant
        if user_type == 'restaurant_admin':
            restaurant_name = request.form.get('restaurant_name')
            address = request.form.get('address')
            phone = request.form.get('phone')
            cuisine = request.form.get('cuisine')
            opening_hours = request.form.get('opening_hours', '')
            
            if not restaurant_name or not address or not phone:
                flash('❌ Restaurant Name, Address, and Phone are required!', 'error')
                db.session.delete(user)
                db.session.commit()
                return render_template('register.html')
            
            if not cuisine:
                flash('❌ Please select a cuisine type!', 'error')
                db.session.delete(user)
                db.session.commit()
                return render_template('register.html')
            
            if Restaurant.query.filter_by(name=restaurant_name).first():
                flash('❌ Restaurant name already exists!', 'error')
                db.session.delete(user)
                db.session.commit()
                return render_template('register.html')
            
            restaurant = Restaurant(
                name=restaurant_name,
                address=address,
                phone=phone,
                cuisine=cuisine,
                opening_hours=opening_hours,
                admin_id=user.id
            )
            db.session.add(restaurant)
            db.session.commit()
            flash('✅ Restaurant registered successfully!', 'success')
        
        flash('✅ Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/admin/edit-restaurant', methods=['GET', 'POST'])
@login_required
def edit_restaurant():
    if current_user.user_type != 'restaurant_admin':
        return redirect(url_for('customer_dashboard'))
    
    restaurant = Restaurant.query.filter_by(admin_id=current_user.id).first()
    if not restaurant:
        flash('Restaurant not found!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        cuisine = request.form.get('cuisine')
        opening_hours = request.form.get('opening_hours')
        
        # Validate required fields
        if not name or not address or not phone:
            flash('❌ Restaurant Name, Address, and Phone are required!', 'error')
            return render_template('restaurant/edit_restaurant.html', restaurant=restaurant)
        
        # Update restaurant details
        restaurant.name = name
        restaurant.address = address
        restaurant.phone = phone
        restaurant.cuisine = cuisine
        restaurant.opening_hours = opening_hours
        
        db.session.commit()
        flash('✅ Restaurant details updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('restaurant/edit_restaurant.html', restaurant=restaurant)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    # Don't flash anything here - it confuses users
    return redirect(url_for('login'))

# ==================== CUSTOMER ROUTES ====================

@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.user_type != 'customer':
        return redirect(url_for('admin_dashboard'))
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.order_time.desc()).all()
    return render_template('customer/dashboard.html', orders=orders)

@app.route('/restaurants')
@login_required
def view_restaurants():
    restaurants = Restaurant.query.all()
    return render_template('customer/restaurants.html', restaurants=restaurants)

@app.route('/restaurant/<int:restaurant_id>/menu')
@login_required
def view_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id, is_available=True).all()
    return render_template('customer/menu.html', restaurant=restaurant, menu_items=menu_items)

@app.route('/add-to-cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + quantity
    session['cart'] = cart
    flash('Item added to cart!', 'success')
    return redirect(request.referrer)

@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for item_id, quantity in cart.items():
        item = MenuItem.query.get(int(item_id))
        if item:
            cart_items.append({'item': item, 'quantity': quantity, 'subtotal': item.price * quantity})
            total += item.price * quantity
    return render_template('customer/cart.html', cart_items=cart_items, total=total)

@app.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart = session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        session['cart'] = cart
        flash('Item removed from cart!', 'success')
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Cart is empty!', 'warning')
        return redirect(url_for('view_cart'))
    
    total = 0
    restaurant_id = None
    for item_id, quantity in cart.items():
        item = MenuItem.query.get(int(item_id))
        if item:
            restaurant_id = item.restaurant_id
            total += item.price * quantity
    
    order = Order(
        order_number=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        customer_id=current_user.id,
        restaurant_id=restaurant_id,
        total_amount=total,
        delivery_address=request.form.get('delivery_address', '')
    )
    db.session.add(order)
    db.session.flush()
    
    for item_id, quantity in cart.items():
        item = MenuItem.query.get(int(item_id))
        order_item = OrderItem(order_id=order.id, menu_item_id=item.id, quantity=quantity, price_at_time=item.price)
        db.session.add(order_item)
    
    db.session.commit()
    session.pop('cart', None)
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order_history'))

@app.route('/order-history')
@login_required
def order_history():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    
    # For each order, get the items
    for order in orders:
        order.items_list = OrderItem.query.filter_by(order_id=order.id).all()
    
    return render_template('customer/order_history.html', orders=orders)

# ==================== RESTAURANT ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.user_type != 'restaurant_admin':
        return redirect(url_for('customer_dashboard'))
    
    restaurant = Restaurant.query.filter_by(admin_id=current_user.id).first()
    if not restaurant:
        flash('Restaurant not found. Please contact support.', 'error')
        return redirect(url_for('logout'))
    
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).all()
    orders = Order.query.filter_by(restaurant_id=restaurant.id).order_by(Order.order_time.desc()).all()
    pending_orders = Order.query.filter_by(restaurant_id=restaurant.id, status='pending').count()
    
    return render_template('restaurant/admin_dashboard.html',
                         restaurant=restaurant,
                         menu_items=menu_items,
                         orders=orders,
                         pending_orders=pending_orders)

@app.route('/admin/menu/add', methods=['POST'])
@login_required
def add_menu_item():
    restaurant = Restaurant.query.filter_by(admin_id=current_user.id).first()
    if not restaurant:
        flash('Restaurant not found!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    item = MenuItem(
        name=request.form['name'],
        price=float(request.form['price']),
        category=request.form.get('category', ''),
        description=request.form.get('description', ''),
        restaurant_id=restaurant.id
    )
    db.session.add(item)
    db.session.commit()
    flash('Menu item added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/menu/delete/<int:item_id>')
@login_required
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Menu item deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/order/<int:order_id>/update', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    flash(f'Order status updated to {order.status}!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/demand-prediction')
@login_required
def demand_prediction():
    if current_user.user_type != 'restaurant_admin':
        return redirect(url_for('customer_dashboard'))
    
    restaurant = Restaurant.query.filter_by(admin_id=current_user.id).first()
    if not restaurant:
        flash('Restaurant not found!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    orders = Order.query.filter_by(restaurant_id=restaurant.id).all()
    
    # Prepare data for prediction
    order_data = []
    for order in orders:
        for item in order.items:
            order_data.append({
                'order_time': order.order_time,
                'menu_item_id': item.menu_item_id,
                'quantity': item.quantity
            })
    
    orders_df = pd.DataFrame(order_data) if order_data else None
    predictions = []
    insights = None
    training_result = None
    
    if orders_df is not None and len(orders_df) >= 3:
        training_result = predictor.train(orders_df)
        if training_result:
            menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).all()
            for item in menu_items:
                pred_7day = predictor.predict(item.id, 7)
                pred_tomorrow = pred_7day[0] if pred_7day else 0
                predictions.append({
                    'item': item,
                    'predicted_tomorrow': pred_tomorrow,
                    'predicted_week': sum(pred_7day)
                })
            predictions.sort(key=lambda x: x['predicted_tomorrow'], reverse=True)
            insights = predictor.get_insights(orders_df)
    
    return render_template('restaurant/demand_prediction.html',
                         predictions=predictions[:10],
                         training_result=training_result,
                         insights=insights,
                         orders=orders)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        
        if user and user.security_question:
            # Store username in session
            session['reset_username'] = username
            # Show security question form
            return render_template('verify_security.html', 
                                 security_question=user.security_question,
                                 username=username)
        else:
            flash('Username not found or no security question set.', 'error')
            return render_template('forgot_password.html')
    
    return render_template('forgot_password.html')


@app.route('/verify-security', methods=['POST'])
def verify_security():
    username = request.form.get('username')
    answer = request.form.get('answer', '').lower().strip()
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.security_answer and user.security_answer.lower() == answer:
        # Correct answer - redirect to reset password page
        flash('✅ Security answer correct! Please enter your new password.', 'success')
        return redirect(url_for('reset_password', username=username))
    else:
        flash('❌ Incorrect answer. Please try again.', 'error')
        return redirect(url_for('forgot_password'))


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    username = request.args.get('username') or request.form.get('username')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('reset_password.html', username=username)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return render_template('reset_password.html', username=username)
        
        user = User.query.filter_by(username=username).first()
        if user:
            user.password = password
            db.session.commit()
            flash('✅ Password reset successfully! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('reset_password.html', username=username)

@app.route('/forgot-username', methods=['GET', 'POST'])
def forgot_username():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user and user.security_question:
            # Store email in session
            session['recover_email'] = email
            return render_template('verify_username_security.html', 
                                 security_question=user.security_question,
                                 email=email)
        else:
            flash('No account found with that email address or security question not set.', 'error')
            return render_template('forgot_username.html')
    
    return render_template('forgot_username.html')


@app.route('/verify-username-security', methods=['POST'])
def verify_username_security():
    email = request.form.get('email')
    answer = request.form.get('answer', '').lower().strip()
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.security_answer and user.security_answer.lower() == answer:
        # Answer correct - show username
        flash(f'✅ Your username is: <strong>{user.username}</strong>', 'success')
        return render_template('forgot_username.html')
    else:
        flash('❌ Incorrect answer. Please try again.', 'error')
        return redirect(url_for('forgot_username'))

# ==================== CREATE DATABASE ====================

with app.app_context():
    db.create_all()
    print("=" * 50)
    print("✅ Database ready!")
    
    # Count existing users
    user_count = User.query.count()
    print(f"✅ Total users in database: {user_count}")
    
    if user_count == 0:
        print("ℹ️ No users found. Please register a Restaurant Owner to get started.")
    else:
        print("✅ System ready! Login with your registered account.")
    
    print("=" * 50)
    print("🚀 Server starting at http://localhost:5000")
    print("=" * 50)

# ==================== RUN APP ====================

if __name__ == '__main__':
    app.run(debug=True)