from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- LISTAR CLIENTES ----------------
@app.route("/clientes")
def listar_clientes():
    db = get_db()
    clientes = db.execute("SELECT * FROM clientes").fetchall()
    return render_template("clientes.html", clientes=clientes)

# ---------------- AGREGAR CLIENTE ----------------
@app.route('/clientes/add', methods=['POST'])
def agregar_cliente():
    nombre = request.form['nombre']
    cedula = request.form.get('cedula', '')
    telefono = request.form['telefono']

    db = get_db()
    db.execute("""
        INSERT INTO clientes(nombre, cedula, telefono) VALUES (?, ?, ?)
    """, (nombre, cedula, telefono))
    db.commit()
    return redirect('/clientes')

# ---------------- EDITAR CLIENTE ----------------
@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    db = get_db()
    cliente = db.execute("SELECT * FROM clientes WHERE id = ?", (id,)).fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form.get('cedula', '')
        telefono = request.form['telefono']

        db.execute("""
            UPDATE clientes SET nombre=?, cedula=?, telefono=? WHERE id=?
        """, (nombre, cedula, telefono, id))
        db.commit()

        return redirect('/clientes')

    return render_template('editar_cliente.html', cliente=cliente)

# ---------------- LISTAR EQUIPOS ----------------
@app.route("/equipos")
def listar_equipos():
    db = get_db()
    equipos = db.execute("""
        SELECT equipos.*, clientes.nombre AS cliente_nombre
        FROM equipos
        LEFT JOIN clientes ON equipos.cliente_id = clientes.id
    """).fetchall()
    return render_template("equipos.html", equipos=equipos)

# ---------------- EDITAR EQUIPO ----------------
@app.route('/equipos/editar/<int:id>', methods=['GET', 'POST'])
def editar_equipo(id):
    db = get_db()
    equipo = db.execute("SELECT * FROM equipos WHERE id = ?", (id,)).fetchone()
    clientes = db.execute("SELECT * FROM clientes").fetchall()

    if request.method == 'POST':
        tipo = request.form['tipo']
        modelo = request.form['modelo']
        cliente_id = request.form['cliente_id']

        db.execute("""
            UPDATE equipos SET tipo=?, modelo=?, cliente_id=? WHERE id=?
        """, (tipo, modelo, cliente_id, id))
        db.commit()

        return redirect('/equipos')

    return render_template('editar_equipo.html', equipo=equipo, clientes=clientes)

# ---------------- LISTAR MANTENIMIENTOS ----------------
@app.route("/mantenimientos")
def listar_mantenimientos():
    db = get_db()
    mantenimientos = db.execute("""
        SELECT mantenimientos.*, equipos.modelo AS equipo_modelo, clientes.nombre AS cliente_nombre
        FROM mantenimientos
        LEFT JOIN equipos ON mantenimientos.equipo_id = equipos.id
        LEFT JOIN clientes ON equipos.cliente_id = clientes.id
    """).fetchall()
    return render_template("mantenimientos.html", mantenimientos=mantenimientos)

# ---------------- EDITAR MANTENIMIENTO ----------------
@app.route('/mantenimientos/editar/<int:id>', methods=['GET', 'POST'])
def editar_mantenimiento(id):
    db = get_db()
    mantenimiento = db.execute("SELECT * FROM mantenimientos WHERE id = ?", (id,)).fetchone()
    equipos = db.execute("SELECT * FROM equipos").fetchall()

    if request.method == 'POST':
        fecha = request.form['fecha']
        detalle = request.form['detalle']
        equipo_id = request.form['equipo_id']

        db.execute("""
            UPDATE mantenimientos SET fecha=?, detalle=?, equipo_id=? WHERE id=?
        """, (fecha, detalle, equipo_id, id))
        db.commit()

        return redirect('/mantenimientos')

    return render_template('editar_mantenimiento.html', mantenimiento=mantenimiento, equipos=equipos)

# ---------------- AGREGAR MANTENIMIENTO ----------------
@app.route("/mantenimientos/add", methods=["POST"])
def mantenimientos_add():
    equipo_id = request.form["equipo"]
    tipo = request.form["tipo"]
    descripcion = request.form["desc"]
    piezas = request.form["piezas"]
    fecha_ing = request.form["ingreso"]
    fecha_ent = request.form["entrega"]
    costo = request.form["costo"]
    estado = request.form["estado"]

    conn = get_db()
    conn.execute("""
        INSERT INTO mantenimientos(equipo_id, tipo, descripcion, piezas, fecha_ingreso, fecha_entrega, costo, estado)
        VALUES (?,?,?,?,?,?,?,?)
    """, (equipo_id, tipo, descripcion, piezas, fecha_ing, fecha_ent, costo, estado))
    conn.commit()
    conn.close()

    return redirect("/mantenimientos")

# ---------------- INICIALIZAR BASE DE DATOS ----------------
def inicializar_bd():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            cedula TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            marca TEXT,
            modelo TEXT,
            serie TEXT,
            tipo TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mantenimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo_id INTEGER,
            tipo TEXT,
            descripcion TEXT,
            piezas TEXT,
            fecha_ingreso TEXT,
            fecha_entrega TEXT,
            costo REAL,
            estado TEXT,
            FOREIGN KEY(equipo_id) REFERENCES equipos(id)
        )
    """)

    conn.commit()
    conn.close()

# ---------------- RUN ----------------
if __name__ == "__main__":
    inicializar_bd()
    app.run(debug=True)
