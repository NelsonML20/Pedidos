import sqlite3

DB_NAME = "database.db"

# -------------------------
# Conexión
# -------------------------
def get_connection():
    return sqlite3.connect(DB_NAME)


# -------------------------
# Crear tablas
# -------------------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        activo INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        total REAL NOT NULL,
        estado TEXT DEFAULT 'pendiente',
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    );

    CREATE TABLE IF NOT EXISTS detalle_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    );
    """)

    conn.commit()
    conn.close()

# -------------------------
# CLIENTES
# -------------------------
def obtener_o_crear_cliente(nombre):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM clientes WHERE nombre = ?",
        (nombre,)
    )
    row = cursor.fetchone()

    if row:
        cliente_id = row[0]
    else:
        cursor.execute(
            "INSERT INTO clientes (nombre) VALUES (?)",
            (nombre,)
        )
        cliente_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return cliente_id


def cargar_productos_iniciales():
    conn = get_connection()
    cursor = conn.cursor()

    productos = [
        ("Pupusa Revuelta", 0.75),
        ("Pupusa de Queso", 0.75),
        ("Soda Coca Cola", 1.00),
        ("Soda Fanta", 1.00),
        ("Soda Tropical Uva", 1.00),
        ("Jugo valle Mandarina", 0.75),
        ("Botella Agua Cristal 600ml", 0.75),
        ("Jugo de Naranja", 1.25),
        ("Café", 0.50),
        ("Chocolate", 0.75)
    ]

    cursor.executemany(
        "INSERT INTO productos (nombre, precio) VALUES (?, ?)",
        productos
    )

    conn.commit()
    conn.close()


# -------------------------
# PRODUCTOS
# -------------------------
def obtener_productos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nombre, precio FROM productos WHERE activo = 1"
    )
    productos = cursor.fetchall()

    conn.close()
    return productos

def obtener_pedidos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, c.nombre, p.total
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.id DESC
    """)

    pedidos = cursor.fetchall()
    conn.close()
    return pedidos


# -------------------------
# PEDIDOS
# -------------------------
def crear_pedido(cliente_id, total):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO pedidos (cliente_id, total) VALUES (?, ?)",
        (cliente_id, total)
    )
    pedido_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return pedido_id

def agregar_detalle_pedido(pedido_id, producto_id, cantidad, precio):
    subtotal = cantidad * precio

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO detalle_pedido
        (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
        VALUES (?, ?, ?, ?, ?)
    """, (pedido_id, producto_id, cantidad, precio, subtotal))

    conn.commit()
    conn.close()

# --------------------------------
# Obtener detalle de un pedido
# --------------------------------
def obtener_detalle_pedido(pedido_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.nombre, d.cantidad, d.precio_unitario, d.subtotal
        FROM detalle_pedido d
        JOIN productos p ON p.id = d.producto_id
        WHERE d.pedido_id = ?
    """, (pedido_id,))

    data = cursor.fetchall()
    conn.close()
    return data

# --------------------------------
# Eliminar pedido completo
# --------------------------------
def eliminar_pedido(pedido_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM detalle_pedido WHERE pedido_id = ?", (pedido_id,))
    cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))

    conn.commit()
    conn.close()

def eliminar_detalle_pedido(pedido_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM detalle_pedido WHERE pedido_id = ?",
        (pedido_id,)
    )
    conn.commit()
    conn.close()


def actualizar_total_pedido(pedido_id, total):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pedidos SET total = ? WHERE id = ?",
        (total, pedido_id)
    )
    conn.commit()
    conn.close()
