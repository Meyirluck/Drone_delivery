from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from app.models import User, Product, Restaurant, MenuItem, CartItem, Order, OrderItem
from app.forms import LoginForm, RegistrationForm, ProductForm, CartItemForm, UpdateCartItemForm, OrderForm
from app import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    products = Product.query.filter_by(available=True).all()
    return render_template('home.html', products=products)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.home'))
    users = User.query.all()
    products = Product.query.all()
    return render_template('admin.html', title='Admin Panel', users=users, products=products)

@main.route('/market')
@login_required
def market():
    products = Product.query.filter_by(available=True).all()
    return render_template('market.html', title='Market', products=products)

@main.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.market'))
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            owner=current_user
        )
        db.session.add(product)
        db.session.commit()
        flash('Product has been added!', 'success')
        return redirect(url_for('main.market'))
    return render_template('add_product.html', title='Add Product', form=form)

@main.route('/delete_product/<int:product_id>')
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.market'))
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect(url_for('main.admin'))

@main.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.home'))
    
    if current_user.id == user_id:
        flash('Cannot delete your own admin account!', 'danger')
        return redirect(url_for('main.admin'))
    
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete other admin accounts!', 'danger')
        return redirect(url_for('main.admin'))
    
    # Delete all products owned by the user
    Product.query.filter_by(owner_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('User and their products have been deleted!', 'success')
    return redirect(url_for('main.admin'))

@main.route('/buy/<int:product_id>')
@login_required
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.owner == current_user:
        flash("You can't buy your own product!", 'danger')
    elif not product.available:
        flash('This product is no longer available.', 'danger')
    elif current_user.budget < product.price:
        flash('Not enough money to buy this product!', 'danger')
    else:
        current_user.budget -= product.price
        product.owner.budget += product.price
        product.owner = current_user
        db.session.commit()
        flash('Successfully purchased product!', 'success')
        return redirect(url_for('main.observe'))
    return redirect(url_for('main.market'))

@main.route('/observe')
def observe():
    return render_template('observe.html')

@main.route('/submit_order', methods=['POST'])
def submit_order():
    # Тут можно сохранить заказ, например в базу или лог
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    phone_number = request.form.get('phoneNumber')
    restaurant = request.form.get('restaurant')
    print(f"Order from {first_name} {last_name} ({phone_number}) for {restaurant}")

    return jsonify({'redirect_url': url_for('main.observe')})

@main.route('/get_positions')
def get_positions():
    # Это пример. Ты можешь получать данные из модели, БД или модуля.
    drone_data = [{
        "id": "DRONE_001",
        "battery": 85,
        "weather": "Ясно",
        "temp": 22,
        "humidity": 40,
        "wind_speed": 3,
        "gps": [43.1965135, 76.6309754]
    }]
    return jsonify(drone_data)

@main.route('/calculate_eta', methods=['POST'])
def calculate_eta():
    try:
        lat = float(request.form.get('lat'))
        lon = float(request.form.get('lon'))
        # Сюда добавь реальную логику расчета
        eta = 5.3  # в минутах
        return jsonify({"eta": eta})
    except Exception as e:
        return jsonify({"error": "Ошибка при расчете ETA"}), 400

@main.route('/start_drone', methods=['POST'])
def start_drone():
    lat = float(request.form.get('lat'))
    lon = float(request.form.get('lon'))
    # Тут можешь проверить батарею, стартовать дрон и т.п.
    battery_level = 85
    if battery_level < 20:
        return jsonify({"error": "Батарея слишком низкая"}), 400
    return jsonify({"status": "ok"})

@main.route('/restaurants')
def restaurants():
    restaurants = Restaurant.query.all()
    return render_template('restaurants.html', title='Restaurants', restaurants=restaurants)

@main.route('/restaurant/<int:restaurant_id>')
def restaurant_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    form = CartItemForm()
    return render_template('restaurant_menu.html', 
                         title=f'{restaurant.name} Menu',
                         restaurant=restaurant,
                         menu_items=menu_items,
                         form=form)

@main.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.menu_item.price * item.quantity for item in cart_items)
    update_form = UpdateCartItemForm()
    return render_template('cart.html',
                         title='Shopping Cart',
                         cart_items=cart_items,
                         total=total,
                         update_form=update_form)

@main.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    form = CartItemForm()
    if form.validate_on_submit():
        menu_item = MenuItem.query.get_or_404(form.menu_item_id.data)
        existing_item = CartItem.query.filter_by(
            user_id=current_user.id,
            menu_item_id=menu_item.id
        ).first()
        
        if existing_item:
            existing_item.quantity += form.quantity.data
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                menu_item_id=menu_item.id,
                quantity=form.quantity.data
            )
            db.session.add(cart_item)
        
        db.session.commit()
        flash('Item added to cart!', 'success')
    return redirect(url_for('main.cart'))

@main.route('/update_cart/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart(cart_item_id):
    form = UpdateCartItemForm()
    if form.validate_on_submit():
        cart_item = CartItem.query.get_or_404(cart_item_id)
        if cart_item.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('main.cart'))
        
        cart_item.quantity = form.quantity.data
        db.session.commit()
        flash('Cart updated!', 'success')
    return redirect(url_for('main.cart'))

@main.route('/remove_from_cart/<int:cart_item_id>')
@login_required
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    if cart_item.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart!', 'success')
    return redirect(url_for('main.cart'))

@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('main.cart'))
    
    # Calculate total
    total = sum(item.menu_item.price * item.quantity for item in cart_items)
    
    form = OrderForm()
    if form.validate_on_submit():
        # Create order
        restaurant = cart_items[0].menu_item.restaurant
        
        order = Order(
            user_id=current_user.id,
            restaurant_id=restaurant.id,
            total_price=total,
            delivery_latitude=form.delivery_latitude.data,
            delivery_longitude=form.delivery_longitude.data
        )
        db.session.add(order)
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                menu_item_id=cart_item.menu_item_id,
                quantity=cart_item.quantity,
                price_at_time=cart_item.menu_item.price
            )
            db.session.add(order_item)
        
        # Clear cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('main.order_confirmation', order_id=order.id))
    
    return render_template('checkout.html',
                         title='Checkout',
                         form=form,
                         cart_items=cart_items,
                         total=total)

@main.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    return render_template('order_confirmation.html',
                         title='Order Confirmation',
                         order=order)

@main.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html',
                         title='My Orders',
                         orders=user_orders)
