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

# ---------------- CLIENTES ----------------
@app.route("/clientes")
def clientes():
    conn = get_db()
    clientes = conn.execute("SELECT * FROM clientes").fetchall()
    conn.close()
    return render_template("clientes.html", clientes=clientes)

@app.route("/clientes/add", methods=["POST"])
def clientes_add():
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    conn = get_db()
    conn.execute("INSERT INTO clientes(nombre, telefono) VALUES (?,?)", (nombre, telefono))
    conn.commit()
    conn.close()
    return redirect("/clientes")

# ---------------- EQUIPOS ----------------
@app.route("/equipos")
def equipos():
    conn = get_db()
    equipos = conn.execute("""
        SELECT e.id, c.nombre AS cliente, e.marca, e.modelo, e.serie
        FROM equipos e JOIN clientes c ON e.cliente_id = c.id
    """).fetchall()
    clientes = conn.execute("SELECT * FROM clientes").fetchall()
    conn.close()
    return render_template("equipos.html", equipos=equipos, clientes=clientes)

@app.route("/equipos/add", methods=["POST"])
def equipos_add():
    cliente_id = request.form["cliente"]
    marca = request.form["marca"]
    modelo = request.form["modelo"]
    serie = request.form["serie"]

    conn = get_db()
    conn.execute("INSERT INTO equipos(cliente_id, marca, modelo, serie) VALUES (?,?,?,?)",
                 (cliente_id, marca, modelo, serie))
    conn.commit()
    conn.close()
    return redirect("/equipos")

# ---------------- MANTENIMIENTOS ----------------
@app.route("/mantenimientos")
def mantenimientos():
    conn = get_db()
    mant = conn.execute("""
        SELECT m.id, c.nombre AS cliente, e.marca, m.tipo, m.estado
        FROM mantenimientos m
        JOIN equipos e ON m.equipo_id = e.id
        JOIN clientes c ON e.cliente_id = c.id
    """).fetchall()

    equipos = conn.execute("""
        SELECT e.id, c.nombre, e.marca
        FROM equipos e JOIN clientes c ON e.cliente_id = c.id
    """).fetchall()

    conn.close()
    return render_template("mantenimientos.html", mant=mant, equipos=equipos)

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
#base
def inicializar_bd():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            marca TEXT,
            modelo TEXT,
            serie TEXT,
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

