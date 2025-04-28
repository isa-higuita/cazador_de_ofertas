from flask import Blueprint, jsonify, g
import sqlite3

precios_bp = Blueprint('precios', __name__)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("cazador.db")
        db.row_factory = sqlite3.Row
    return db

@precios_bp.route("/precios/<int:idproducto>", methods=["GET"])
def obtener_precios(idproducto):
    db = get_db()
    cursor = db.execute("SELECT * FROM PRECIOS WHERE idproducto = ? ORDER BY fecha DESC", (idproducto,))

    precios = cursor.fetchall()

    if not precios:
        return jsonify({"mensaje": "No hay precios para este producto"}), 404

    resultado = []
    for precio in precios:
        resultado.append({
            "idprecio": precio["idprecio"],
            "idproducto": precio["idproducto"],
            "precio": precio["precio"],
            "tienda": precio["tienda"],
            "fecha": precio["fecha"]
        })

    return jsonify(resultado), 200