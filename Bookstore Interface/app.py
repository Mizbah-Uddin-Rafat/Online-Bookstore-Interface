import pymysql
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy import desc
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import time


# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy()
# create the app
app = Flask(__name__)
app.secret_key = '#'
username = 'root'
password = 'Fixit#123'
userpass = 'mysql+pymysql://' + username + ':' + password + '@'
# keep this as is for a hosted website
server = '127.0.0.1'
# CHANGE to YOUR database name, with a slash added as shown
dbname = '/bookstore'

# put them all together as a string that shows SQLAlchemy where the database is
app.config['SQLALCHEMY_DATABASE_URI'] = userpass + server + dbname

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)

# Define the models
class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    #name = db.Column(db.String(50), nullable=False)
    #email = db.Column(db.String(120), unique=True, nullable=False)


class Author(db.Model):
    __tablename__ = 'Author'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.Text, nullable=False)


class Publisher(db.Model):
    __tablename__ = 'Publisher'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)


class Inventory(db.Model):
    __tablename__ = 'Inventory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)


class Books(db.Model):
    __tablename__ = 'Books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('Author.id'), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('Publisher.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('Inventory.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)  # Add price field

    author = db.relationship('Author', backref='books')
    publisher = db.relationship('Publisher', backref='books')
    inventory = db.relationship('Inventory', backref='books')

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    user = db.relationship('User', backref='customer')
    orders = db.relationship('Order', backref='customer_relation', lazy=True)


class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    book_id = db.Column(db.Integer, db.ForeignKey('Books.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    priority_id = db.Column(db.Integer, db.ForeignKey('Priority.id'))

    book = db.relationship('Books', backref='orders')
    customer = db.relationship('Customer', backref='orders_relation')  # Renamed backref to 'orders'
    priority = db.relationship('Priority', backref='orders')

class Payment(db.Model):
    __tablename__ = 'Payment'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    amount = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.id'))

    order = db.relationship('Order', backref='payment')


class Invoice(db.Model):
    __tablename__ = 'Invoice'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    total = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))

    customer = db.relationship('Customer', backref='invoices')


class Priority(db.Model):
    __tablename__ = 'Priority'
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)  # Adjust the length if necessary

    def __repr__(self):
        return f"<Priority {self.level}>"



class SalesRecord(db.Model):
    __tablename__ = 'SalesRecord'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.id'), nullable=False)
    date = db.Column(db.Text, nullable=False)

    order = db.relationship('Order', backref='sales_record')


class ShoppingCart(db.Model):
    __tablename__ = 'ShoppingCart'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'), nullable=False)

    customer = db.relationship('Customer', backref='shopping_cart')


class CartItem(db.Model):
    __tablename__ = 'CartItem'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('ShoppingCart.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('Books.id'))
    quantity = db.Column(db.Integer)

    cart = db.relationship('ShoppingCart', backref='cart_items')

    book = db.relationship('Books', backref='cart_items')  # Define the relationship

    def __init__(self, cart_id, book_id, quantity):
        self.cart_id = cart_id
        self.book_id = book_id
        self.quantity = quantity
    


# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['user_id'] = user.id
            return redirect(url_for('main'))
        elif username != 'correct_username' or password != 'correct_password':
            error = 'Invalid username or password'
    return render_template('login.html', error=error)
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/main', methods=['GET', 'POST'])
def main():
    user_id = session['user_id']
    user = User.query.get(user_id)
    customer = Customer.query.filter_by(user_id=user_id).first()# Fetch user information. Adjust based on your actual logic.
    books = Books.query.all()
    orders = Order.query.all()

    if request.method == 'POST': 
        if 'sort_inventory' in request.form:
            sort_order = request.form['sort_inventory']
            books = sorted(books, key=lambda x: x.inventory.quantity, reverse=(sort_order == 'desc'))
        elif 'sort_orders' in request.form:
            orders = bubble_sort_orders(orders)  

    return render_template('main.html', user=user, sorted_inventory=books, sorted_orders=orders, customer=customer)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author_name = request.form['author_name']
        publisher_name = request.form['publisher_name']
        inventory_quantity = int(request.form['inventory_quantity'])
        price = float(request.form['price'])

        # Check if the author already exists, otherwise add the author
        author = Author.query.filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.commit()

        # Check if the publisher already exists, otherwise add the publisher
        publisher = Publisher.query.filter_by(name=publisher_name).first()
        if not publisher:
            publisher = Publisher(name=publisher_name)
            db.session.add(publisher)
            db.session.commit()

        # Add the inventory record
        inventory = Inventory(quantity=inventory_quantity)
        db.session.add(inventory)
        db.session.commit()

        # Add the book with references to the author, publisher, and inventory
        new_book = Books(
            title=title,
            author_id=author.id,
            publisher_id=publisher.id,
            inventory_id=inventory.id,
            price=price
        )
        db.session.add(new_book)
        db.session.commit()

        flash('Book added successfully!', 'success')
        #return redirect(url_for('main'))  # Redirect to order page or any other page

    return render_template('add_book.html')


@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    sort_order = request.args.get('sort_order', 'asc')
    books = Books.query.all()

    # Sort books using insertion sort
    books = insertion_sort_inventory(books, sort_order)

    if request.method == 'POST':
        book_id = request.form.get('book_id')
        restock_quantity = request.form.get('restock_quantity')
        
        if book_id and restock_quantity:
            book_id = int(book_id)
            restock_quantity = int(restock_quantity)
            
            book = Books.query.get(book_id)
            if book and book.inventory:
                book.inventory.quantity += restock_quantity
                db.session.commit()
            
            return redirect(url_for('inventory', sort_order=sort_order))
        else:
            # Handle case where book_id or restock_quantity is missing
            return "Missing book_id or restock_quantity", 400

    return render_template('inventory.html', books=books, sort_order=sort_order)

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Books.query.get_or_404(book_id)

    if request.method == 'POST':
        book.title = request.form['title']
        book.price = float(request.form['price'])

        author_name = request.form['author_name']
        author = Author.query.filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.commit()
        book.author_id = author.id

        publisher_name = request.form['publisher_name']
        publisher = Publisher.query.filter_by(name=publisher_name).first()
        if not publisher:
            publisher = Publisher(name=publisher_name)
            db.session.add(publisher)
            db.session.commit()
        book.publisher_id = publisher.id

        inventory_quantity = int(request.form['inventory_quantity'])
        book.inventory.quantity = inventory_quantity

        db.session.commit()
        flash('Book edited successfully!', 'success')
        return redirect(url_for('inventory'))

    return render_template('edit_book.html', book=book)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        
        # Create new user
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        
        # Create new customer
        customer = Customer(name=name, phone=phone, address=address, user_id=user.id)
        db.session.add(customer)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/order', methods=['GET', 'POST'])
def order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    books = []

    if request.method == 'GET':
        search_by = request.args.get('search_by')
        search_value = request.args.get('search_value')

        if search_by and search_value:
            if search_by == 'title':
                books = Books.query.filter(Books.title.ilike(f'%{search_value}%')).all()
            elif search_by == 'author':
                books = Books.query.join(Author).filter(Author.name.ilike(f'%{search_value}%')).all()
            elif search_by == 'book_id':
                books = Books.query.filter_by(id=int(search_value)).all()
    
    if request.method == 'POST':
        book_id = request.form['book_id']
        quantity = int(request.form['quantity'])
        customer_id = session['user_id']

        book = Books.query.get(book_id)
        if not book:
            return "Book not found"

        shopping_cart = ShoppingCart.query.filter_by(customer_id=customer_id).first()
        if shopping_cart is None:
            shopping_cart = ShoppingCart(customer_id=customer_id)
            db.session.add(shopping_cart)
            db.session.commit()
        
        cart_item = CartItem(
            cart_id=shopping_cart.id,
            book_id=book.id,
            quantity=quantity
        )
        db.session.add(cart_item)
        db.session.commit()
        
        order = Order(
            customer_id=customer_id,
            book_id=book.id,
            quantity=quantity,
            priority_id=1,  # Assuming a default priority
        )
        db.session.add(order)
        
        # Deduct quantity from inventory
        book.inventory.quantity -= quantity

        db.session.commit()
        
        return redirect(url_for('shopping_cart', id=order.id))
    
    return render_template('order.html', books=books)




@app.route('/shopping_cart', methods=['GET', 'POST'])
def shopping_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    customer_id = session['user_id']
    shopping_cart = ShoppingCart.query.filter_by(customer_id=customer_id).first()

    if shopping_cart is None:
        return "No shopping cart found for this customer."

    cart_items = CartItem.query.filter_by(cart_id=shopping_cart.id).join(Books).all()
    total_price = sum(item.quantity * item.book.price for item in cart_items if item.book and item.book.price is not None)

    if request.method == 'POST':
        if 'remove_item' in request.form:
            item_id = request.form['remove_item']
            CartItem.query.filter_by(id=item_id).delete()
            db.session.commit()
            return redirect(url_for('shopping_cart'))
        
        if 'clear_cart' in request.form:
            CartItem.query.filter_by(cart_id=shopping_cart.id).delete()
            db.session.commit()
            return redirect(url_for('shopping_cart'))
        
        if 'priority' in request.form:
            priority_level = request.form['priority']
            priority = Priority.query.filter_by(level=priority_level).first()

            if priority is None:
                return "Priority level does not exist."

            current_order_ids = []

            for item in cart_items:
                order = Order(
                    book_id=item.book_id,
                    customer_id=customer_id,
                    quantity=item.quantity,
                    priority_id=priority.id
                )
                db.session.add(order)
                db.session.commit()
                current_order_ids.append(order.id)

            # Store the current order IDs in the session
            session['current_order_ids'] = current_order_ids

            db.session.query(CartItem).filter_by(cart_id=shopping_cart.id).delete()
            db.session.commit()

            return redirect(url_for('payment'))

    return render_template('shopping_cart.html', cart_items=cart_items, total_price=total_price)




@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    customer_id = session['user_id']

    # Retrieve the current session's order IDs from the session
    current_order_ids = session.get('current_order_ids', [])
    orders = Order.query.filter(Order.id.in_(current_order_ids)).all()
    
    total_amount = sum(order.quantity * order.book.price for order in orders if order.book and order.book.price is not None)
    
    if request.method == 'POST':
        for order in orders:
            payment = Payment(amount=order.quantity * order.book.price, order_id=order.id)
            db.session.add(payment)
        
        invoice = Invoice(total=total_amount, customer_id=customer_id)
        db.session.add(invoice)
        db.session.commit()
        
        # Clear the current orders from the session
        session.pop('current_order_ids', None)
        
        return redirect(url_for('invoice'))
    
    return render_template('payment.html', total_amount=total_amount)


@app.route('/invoice', methods=['GET'])
def invoice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    customer_id = session['user_id']
    invoice = Invoice.query.filter_by(customer_id=customer_id).order_by(desc(Invoice.id)).first()
    
    return render_template('invoice.html', invoice=invoice)

@app.route('/order_record', methods=['GET'])
def order_record():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    sort_order = request.args.get('sort_priority', 'asc')
    
    orders = Order.query.all()
    
    if sort_order == 'asc':
        sorted_orders = bubble_sort_orders(orders, ascending=True)
    else:
        sorted_orders = bubble_sort_orders(orders, ascending=False)
    
    return render_template('order_record.html', orders=sorted_orders)

@app.route('/user_info', methods=['GET', 'POST'])
def user_info():
    users = User.query.all()
    

    if request.method == 'POST':
        if 'sort_users' in request.form:
            sort_order = request.form['sort_users']
            sorted_users = merge_sort(users, key='id', reverse=(sort_order == 'desc'))
        else:
            sorted_users = users

        
    else:
        sorted_users = users

    return render_template('user_info.html', sorted_users=sorted_users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Update user fields
        if username:
            user.username = username
        
        if password:
            # Update password only if a new password is provided
            user.password = password
        
        if name:
            user.name = name
        
        if phone:
            user.phone = phone
        
        if address:
            user.address = address
        
        # Commit changes to the database
        db.session.commit()
        
        flash('User information updated successfully!', 'success')
        return redirect(url_for('user_info'))  # Redirect to a user info or another relevant page

    return render_template('edit_user.html', user=user)

@app.route('/customer_info', methods=['GET', 'POST'])
def customer_info():    
    customers = Customer.query.all()

    if request.method == 'POST': 

        if 'sort_customers' in request.form:
            sort_order = request.form['sort_customers']
            sorted_customers = merge_sort(customers, key='id', reverse=(sort_order == 'desc'))
        else:
            sorted_customers = customers
    else:
        sorted_customers = customers

    return render_template('customer_info.html',  sorted_customers=sorted_customers)

def bubble_sort_orders(orders, ascending=True):
    start_time = time.time()
    n = len(orders)
    for i in range(n):
        for j in range(0, n - i - 1):
            priority_j = orders[j].priority.level if orders[j].priority else float('inf')
            priority_j1 = orders[j + 1].priority.level if orders[j + 1].priority else float('inf')
            
            if ascending:
                if priority_j > priority_j1:
                    orders[j], orders[j + 1] = orders[j + 1], orders[j]
            else:
                if priority_j < priority_j1:
                    orders[j], orders[j + 1] = orders[j + 1], orders[j]
    end_time = time.time()
    print(f"Bubble Sort Time: {end_time - start_time} seconds")
    return orders

@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Update customer fields
        if name:
            customer.name = name
        
        if phone:
            customer.phone = phone
        
        if address:
            customer.address = address
        
        # Commit changes to the database
        db.session.commit()
        
        flash('Customer information updated successfully!', 'success')
        return redirect(url_for('customer_info'))  # Redirect to a user info or another relevant page

    return render_template('edit_customer.html', customer=customer)



# Insertion Sort implementation for sorting inventory
def insertion_sort_inventory(books, sort_order):
    start_time = time.time()
    n = len(books)
    for i in range(1, n):
        key = books[i]
        j = i - 1
        while j >= 0 and ((sort_order == 'asc' and books[j].inventory.quantity > key.inventory.quantity) or
                          (sort_order == 'desc' and books[j].inventory.quantity < key.inventory.quantity)):
            books[j + 1] = books[j]
            j -= 1
        books[j + 1] = key
    end_time = time.time()
    print(f"Insertion Sort Time: {end_time - start_time} seconds")
    return books

# Merge Sort implementation for sorting users
def merge_sort_users(users):
    if len(users) <= 1:
        return users
    
    mid = len(users) // 2
    left = merge_sort_users(users[:mid])
    right = merge_sort_users(users[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i].id <= right[j].id:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sort(data, key, reverse=False):
    start_time = time.time()
    if len(data) > 1:
        mid = len(data) // 2
        left_half = data[:mid]
        right_half = data[mid:]

        merge_sort(left_half, key, reverse)
        merge_sort(right_half, key, reverse)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            if (getattr(left_half[i], key) < getattr(right_half[j], key)) ^ reverse:
                data[k] = left_half[i]
                i += 1
            else:
                data[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            data[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            data[k] = right_half[j]
            j += 1
            k += 1
    end_time = time.time()
    print(f"Merge Sort Time: {end_time - start_time} seconds")
    return data






if __name__ == '__main__':
    app.run(debug=True)