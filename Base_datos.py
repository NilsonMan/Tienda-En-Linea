import sqlite3

# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect('delivery_service.db')
    cursor = conn.cursor()

    # Eliminar tablas si existen
    cursor.execute("DROP TABLE IF EXISTS usuarios")
    cursor.execute("DROP TABLE IF EXISTS productos")
    cursor.execute("DROP TABLE IF EXISTS pedidos")

    # Crear tabla usuarios
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

    # Crear tabla productos
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

    # Crear tabla pedidos
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

    # Añadir productos de ejemplo
    cursor.execute("INSERT INTO productos (nombre, precio, descripcion, imagen, cocinero_id) VALUES ('Sopa', 5.0, 'Deliciosa sopa casera', 'sopa.jpeg', 1)")
    cursor.execute("INSERT INTO productos (nombre, precio, descripcion, imagen, cocinero_id) VALUES ('Puchero', 8.0, 'Sabroso puchero casero', 'puchero.jpeg', 1)")

    # Crear usuario administrador de ejemplo
    cursor.execute("INSERT INTO usuarios (nombre, direccion, tipo, username, password) VALUES ('Admin', 'Direccion Admin', 'admin', 'admin', 'admin')")

    conn.commit()
    conn.close()

# Llamar a la función para inicializar la base de datos
init_db()
