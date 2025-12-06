from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# -------------------- CONEXIÓN BD --------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------- PÁGINA PRINCIPAL --------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------------------------------------
#                        CLIENTES
# ------------------------------------------------------------
@app.route("/clientes")
def listar_clientes():
    db = get_db()
    clientes = db.execute("SELECT * FROM clientes").fetchall()
    return render_template("clientes.html", clientes=clientes)


@app.route("/clientes/add", methods=["GET", "POST"])
def agregar_cliente():
    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]

        db = get_db()
        db.execute("INSERT INTO clientes(nombre, telefono) VALUES (?, ?)",
                   (nombre, telefono))
        db.commit()
        return redirect(url_for("listar_clientes"))

    return render_template("editar_cliente.html", cliente=None)


@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    db = get_db()
    cliente = db.execute("SELECT * FROM clientes WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]

        db.execute("UPDATE clientes SET nombre=?, telefono=? WHERE id=?",
                   (nombre, telefono, id))
        db.commit()
        return redirect(url_for("listar_clientes"))

    return render_template("editar_cliente.html", cliente=cliente)


# ------------------------------------------------------------
#                        EQUIPOS
# ------------------------------------------------------------
@app.route("/equipos")
def listar_equipos():
    db = get_db()
    equipos = db.execute("""
        SELECT equipos.*, clientes.nombre AS cliente_nombre
        FROM equipos
        LEFT JOIN clientes ON clientes.id = equipos.cliente_id
    """).fetchall()
    return render_template("equipos.html", equipos=equipos)


@app.route("/equipos/add", methods=["GET", "POST"])
def agregar_equipo():
    db = get_db()
    clientes = db.execute("SELECT * FROM clientes").fetchall()

    if request.method == "POST":
        tipo = request.form["tipo"]
        modelo = request.form["modelo"]
        cliente_id = request.form["cliente_id"]

        db.execute("""
            INSERT INTO equipos(tipo, modelo, cliente_id)
            VALUES (?, ?, ?)
        """, (tipo, modelo, cliente_id))
        db.commit()
        return redirect(url_for("listar_equipos"))

    return render_template("editar_equipo.html", equipo=None, clientes=clientes)


@app.route("/equipos/editar/<int:id>", methods=["GET", "POST"])
def editar_equipo(id):
    db = get_db()

    equipo = db.execute("SELECT * FROM equipos WHERE id=?", (id,)).fetchone()
    clientes = db.execute("SELECT * FROM clientes").fetchall()

    if request.method == "POST":
        tipo = request.form["tipo"]
        modelo = request.form["modelo"]
        cliente_id = request.form["cliente_id"]

        db.execute("""
            UPDATE equipos SET tipo=?, modelo=?, cliente_id=? WHERE id=?
        """, (tipo, modelo, cliente_id, id))
        db.commit()
        return redirect(url_for("listar_equipos"))

    return render_template("editar_equipo.html", equipo=equipo, clientes=clientes)


# ------------------------------------------------------------
#                   MANTENIMIENTOS
# ------------------------------------------------------------
@app.route("/mantenimientos")
def listar_mantenimientos():
    db = get_db()
    mantenimientos = db.execute("""
        SELECT m.*, 
               e.tipo AS equipo_tipo, 
               e.modelo AS equipo_modelo,
               c.nombre AS cliente_nombre
        FROM mantenimientos m
        LEFT JOIN equipos e ON e.id = m.equipo_id
        LEFT JOIN clientes c ON c.id = e.cliente_id
    """).fetchall()

    return render_template("mantenimientos.html", mantenimientos=mantenimientos)


@app.route("/mantenimientos/add", methods=["GET", "POST"])
def agregar_mantenimiento():
    db = get_db()
    equipos = db.execute("SELECT * FROM equipos").fetchall()

    if request.method == "POST":
        equipo_id = request.form["equipo_id"]
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"]
        piezas = request.form["piezas"]
        fecha_ingreso = request.form["fecha_ingreso"]
        fecha_entrega = request.form["fecha_entrega"]
        costo = request.form["costo"]
        estado = request.form["estado"]

        db.execute("""
            INSERT INTO mantenimientos(equipo_id, tipo, descripcion, piezas, fecha_ingreso, fecha_entrega, costo, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (equipo_id, tipo, descripcion, piezas, fecha_ingreso, fecha_entrega, costo, estado))
        db.commit()
        return redirect(url_for("listar_mantenimientos"))

    return render_template("editar_mantenimiento.html", mantenimiento=None, equipos=equipos)


@app.route("/mantenimientos/editar/<int:id>", methods=["GET", "POST"])
def editar_mantenimiento(id):
    db = get_db()

    mantenimiento = db.execute("SELECT * FROM mantenimientos WHERE id=?", (id,)).fetchone()
    equipos = db.execute("SELECT * FROM equipos").fetchall()

    if request.method == "POST":
        equipo_id = request.form["equipo_id"]
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"]
        piezas = request.form["piezas"]
        fecha_ingreso = request.form["fecha_ingreso"]
        fecha_entrega = request.form["fecha_entrega"]
        costo = request.form["costo"]
        estado = request.form["estado"]

        db.execute("""
            UPDATE mantenimientos SET equipo_id=?, tipo=?, descripcion=?, piezas=?, 
                                     fecha_ingreso=?, fecha_entrega=?, costo=?, estado=?
            WHERE id=?
        """, (equipo_id, tipo, descripcion, piezas, fecha_ingreso, fecha_entrega, costo, estado, id))
        db.commit()

        return redirect(url_for("listar_mantenimientos"))

    return render_template("editar_mantenimiento.html", mantenimiento=mantenimiento, equipos=equipos)


# ------------------------------------------------------------
#                   CREAR BASE DE DATOS
# ------------------------------------------------------------
def inicializar_bd():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            modelo TEXT,
            cliente_id INTEGER,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    """)

    db.execute("""
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

    db.commit()


# ------------------------------------------------------------
#                       RUN
# ------------------------------------------------------------
if __name__ == "__main__":
    inicializar_bd()
    app.run(debug=True)
