from flask import Blueprint, render_template, session, redirect, url_for, g, request, flash
import sqlite3

lista_deseos_bp = Blueprint("lista_deseos", __name__, url_prefix="/lista_deseos")

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("cazador.db")
        db.row_factory = sqlite3.Row
    return db

@lista_deseos_bp.route("/agregar", methods=["POST"])
def agregar_a_lista():
    if "usuario_id" not in session:
        flash("Debes iniciar sesión para agregar productos a tu lista de deseos.", "error")
        return redirect(url_for("usuarios.registrar_usuario"))

    usuario_id = session["usuario_id"]
    producto_id = request.form.get("producto_id")

    if not producto_id:
        flash("Producto no válido.", "error")
        return redirect(url_for("productos.obtener_productos"))

    db = get_db()
    existente = db.execute(
        "SELECT id FROM lista_deseos WHERE producto_id = ? AND usuario_id = ?",
        (producto_id, usuario_id)
    ).fetchone()

    if existente:
        flash("El producto ya está en tu lista de deseos.", "info")
    else:
        db.execute(
            "INSERT INTO lista_deseos (producto_id, usuario_id) VALUES (?, ?)",
            (producto_id, usuario_id)
        )
        db.commit()
        flash("Producto agregado a tu lista de deseos.", "success")

    return redirect(url_for("productos.obtener_productos"))

@lista_deseos_bp.route("/")
def ver_lista_deseos():
    if "usuario_id" not in session:
        flash("Debes iniciar sesión para ver tu lista de deseos.", "error")
        return redirect(url_for("usuarios.mostrar_login"))

    usuario_id = session["usuario_id"]
    db = get_db()
    productos = db.execute("""
        SELECT p.idproducto, p.nombre, p.descripcion, p.imagen
        FROM lista_deseos ld
        JOIN PRODUCTOS p ON ld.producto_id = p.idproducto
        WHERE ld.usuario_id = ?
    """, (usuario_id,)).fetchall()

    return render_template("lista_deseos.html", productos=productos)


@lista_deseos_bp.route("/lista_deseos/eliminar/<int:producto_id>", methods=["POST"])
def eliminar_de_lista(producto_id):
    if "usuario_id" not in session:
        flash("Debes iniciar sesión para realizar esta acción.", "error")
        return redirect(url_for("usuarios.mostrar_login"))

    usuario_id = session["usuario_id"]
    db = get_db()
    db.execute("DELETE FROM lista_deseos WHERE producto_id = ? AND usuario_id = ?", (producto_id, usuario_id))
    db.commit()

    flash("Producto eliminado de tu lista de deseos.", "success")
    return redirect(url_for("lista_deseos.ver_lista_deseos"))




