from flask import Blueprint, jsonify, request, g, render_template
import sqlite3

productos_bp = Blueprint("productos", __name__)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("cazador.db")
        db.row_factory = sqlite3.Row
    return db

@productos_bp.route("/productos", methods=["GET"])
def obtener_productos():
    db = get_db()
    cursor = db.execute("""
        SELECT 
            p.idproducto AS idproducto, 
            p.nombre AS nombre, 
            p.descripcion AS descripcion, 
            p.imagen AS imagen, 
            (SELECT precio FROM PRECIOS WHERE idproducto = p.idproducto ORDER BY fecha DESC LIMIT 1) AS precio
        FROM PRODUCTOS p
    """)
    productos = [dict(row) for row in cursor.fetchall()]

    return render_template("product.html", productos=productos)