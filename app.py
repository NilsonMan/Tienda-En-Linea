from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import sqlite3
import os
import folium

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuration for static files folder (images)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(APP_ROOT, 'static/assets')

# Initialize the database
def init_db():
    if not os.path.exists('delivery_service.db'):
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT,
            tipo TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT NOT NULL,
            imagen TEXT,
            cocinero_id INTEGER,
            FOREIGN KEY (cocinero_id) REFERENCES usuarios(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            cocinero_id INTEGER,
            repartidor_id INTEGER,
            productos_pedido TEXT,
            estado TEXT,
            FOREIGN KEY (cliente_id) REFERENCES usuarios(id),
            FOREIGN KEY (cocinero_id) REFERENCES usuarios(id),
            FOREIGN KEY (repartidor_id) REFERENCES usuarios(id)
        )
        ''')

        # Examples of initial data
        cursor.execute("INSERT INTO productos (nombre, precio, descripcion, imagen, cocinero_id) VALUES ('Sopa', 5.0, 'Deliciosa sopa casera', 'sopa.jpeg', 1)")
        cursor.execute("INSERT INTO productos (nombre, precio, descripcion, imagen, cocinero_id) VALUES ('Puchero', 8.0, 'Sabroso puchero casero', 'puchero.jpeg', 1)")
        cursor.execute("INSERT INTO usuarios (nombre, direccion, tipo, username, password) VALUES ('Admin', 'Direccion Admin', 'admin', 'admin', 'admin')")

        conn.commit()
        conn.close()

# Initialize the database if necessary
init_db()

# Route to serve static images
@app.route('/static/assets/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Function to create the map with the current location of the delivery person
def create_map(start_lat, start_lng, client_lat, client_lng):
    map = folium.Map(location=[start_lat, start_lng], zoom_start=13)
    folium.Marker([start_lat, start_lng], tooltip='Repartidor').add_to(map)
    folium.Marker([client_lat, client_lng], tooltip='Cliente', icon=folium.Icon(color='red')).add_to(map)
    return map._repr_html_()

# Simulated function to get the current location of the delivery person
def get_current_location():
    # This function should connect to your database or location service to get the current position
    return 20.967370, -89.592586

# Simulated function to get the client location
def get_client_location():
    # This should also be fetched from your database
    return 20.987654, -89.123456

@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validate admin user
        if username == 'admin' and password == 'admin':
            session['user_id'] = 1  # Assuming admin user has id=1
            session['user_type'] = 'admin'
            return redirect(url_for('admin_menu'))
        
        # Validate other users in the database
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_type'] = user[3]
            if user[3] == 'cliente':
                return redirect(url_for('client_menu'))
            elif user[3] == 'repartidor':
                return redirect(url_for('delivery_menu'))
        else:
            return 'Usuario o contraseña incorrectos'
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        user_type = request.form['user_type']
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, direccion, tipo, username, password) VALUES (?, ?, ?, ?, ?)",
                       (name, address, user_type, username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Client menu route
@app.route('/client_menu')
def client_menu():
    if 'user_id' in session and session['user_type'] == 'cliente':
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        products = cursor.fetchall()
        conn.close()
        return render_template('client_menu.html', products=products)
    return redirect(url_for('login'))

# Delivery menu route
@app.route('/delivery_menu')
def delivery_menu():
    if 'user_id' in session and session['user_type'] == 'repartidor':
        return render_template('delivery_menu.html')
    return redirect(url_for('login'))

# Admin menu route
@app.route('/admin_menu')
def admin_menu():
    if 'user_id' in session and session['user_type'] == 'admin':
        return render_template('admin_menu.html')
    return redirect(url_for('login'))

# Products route
@app.route('/products')
def products():
    if 'user_id' in session and session['user_type'] == 'cliente':
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        products = cursor.fetchall()
        conn.close()
        return render_template('products.html', products=products)
    return redirect(url_for('login'))

# Add product route
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            price = float(request.form['price'])
            description = request.form['description']
            cocinero_id = request.form['cocinero_id']
            
            # Process image
            image = request.files['image']
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            
            conn = sqlite3.connect('delivery_service.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (nombre, precio, descripcion, imagen, cocinero_id) VALUES (?, ?, ?, ?, ?)",
                           (name, price, description, image_filename, cocinero_id))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_menu'))
        return render_template('add_product.html')
    return redirect(url_for('login'))

# Simulate purchase route
@app.route('/simulate_purchase/<int:product_id>', methods=['GET', 'POST'])
def simulate_purchase(product_id):
    if 'user_id' in session and session['user_type'] == 'cliente':
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id=?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        if request.method == 'POST':
            # Here you could implement purchase confirmation logic
            return redirect(url_for('confirm_purchase', product_id=product_id))
        return render_template('simulate_purchase.html', product=product)
    return redirect(url_for('login'))

# Confirm purchase route
# Confirm purchase route
@app.route('/confirm_purchase/<int:product_id>', methods=['GET', 'POST'])
def confirm_purchase(product_id):
    if 'user_id' in session and session['user_type'] == 'cliente':
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id=?", (product_id,))
        product = cursor.fetchone()  # Obtener el producto como una tupla
        
        # Aquí product es una tupla, accedemos a sus elementos por índice numérico
        if request.method == 'POST':
            # Update order status and assign delivery person
            conn = sqlite3.connect('delivery_service.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pedidos (cliente_id, cocinero_id, productos_pedido, estado) VALUES (?, ?, ?, ?)",
                           (session['user_id'], product[5], product[1], 'pendiente'))
            conn.commit()
            conn.close()
            return redirect(url_for('track_order', product_id=product_id))
        return render_template('confirm_purchase.html', product=product)
    return redirect(url_for('login'))


# Track order route
@app.route('/track_order/<int:product_id>')
def track_order(product_id):
    if 'user_id' in session and session['user_type'] == 'cliente':
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE cliente_id=? AND estado='pendiente'", (session['user_id'],))
        order = cursor.fetchone()
        conn.close()
        if order:
            return render_template('track_order.html', order=order)
        else:
            return 'No se encontró ningún pedido pendiente.'
    return redirect(url_for('login'))

# Make order route
@app.route('/make_order', methods=['POST'])
def make_order():
    if 'user_id' in session and session['user_type'] == 'cliente':
        product_id = request.form['product_id']
        return redirect(url_for('simulate_purchase', product_id=product_id))
    return redirect(url_for('login'))

@app.route('/delivery_orders')
def delivery_orders():
    if 'user_id' in session and session['user_type'] == 'repartidor':
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE repartidor_id=? AND estado='pendiente'", (session['user_id'],))
        orders = cursor.fetchall()
        conn.close()
        return render_template('delivery_orders.html', orders=orders)
    return redirect(url_for('login'))

# Take order route
@app.route('/take_order/<int:order_id>')
def take_order(order_id):
    if 'user_id' in session and session['user_type'] == 'repartidor':
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE pedidos SET repartidor_id=?, estado='en camino' WHERE id=?", (session['user_id'], order_id))
        conn.commit()
        conn.close()
        return redirect(url_for('track_delivery', order_id=order_id))
    return redirect(url_for('login'))

# Track delivery route
@app.route('/track_delivery/<int:order_id>')
def track_delivery(order_id):
    if 'user_id' in session and session['user_type'] == 'repartidor':
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE id=?", (order_id,))
        order = cursor.fetchone()
        conn.close()
        if order and order['estado'] == 'en camino':
            return render_template('track_delivery.html', order=order)
        else:
            return 'No se encontró el pedido o no está en camino.'
    return redirect(url_for('login'))

# Complete delivery route
@app.route('/complete_delivery/<int:order_id>')
def complete_delivery(order_id):
    if 'user_id' in session and session['user_type'] == 'repartidor':
        conn = sqlite3.connect('delivery_service.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE pedidos SET estado='entregado' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('delivery_orders'))
    return redirect(url_for('login'))

@app.route('/map')
def map_view():
    start_lat, start_lng = get_current_location()
    client_lat, client_lng = get_client_location()
    folium_map = create_map(start_lat, start_lng, client_lat, client_lng)
    return render_template('map.html', folium_map=folium_map, start_lat=start_lat, start_lng=start_lng, client_lat=client_lat, client_lng=client_lng)

@app.route('/update_location', methods=['POST'])
def update_location():
    new_lat = request.json.get('lat')
    new_lng = request.json.get('lng')
    # Actualiza la ubicación en la base de datos o sistema de seguimiento
    # Lógica para actualizar la ubicación
    return jsonify(status="success", lat=new_lat, lng=new_lng)

# Otras rutas de tu aplicación Flask
# ...

if __name__ == "__main__":
    app.run(debug=True)