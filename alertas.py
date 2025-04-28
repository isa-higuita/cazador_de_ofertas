from flask import Blueprint, flash, redirect, render_template, request, jsonify, g, session, url_for
import sqlite3

alertas_bp = Blueprint("alertas", __name__)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("cazador.db", check_same_thread=False)
        db.row_factory = sqlite3.Row
    return db

@alertas_bp.route("/agregar_alerta", methods=["POST"])
def agregar_alerta():
    print(request.form.to_dict())  

    try:
        idusuario = request.form.get("usuario_id")  # Cambiado a usuario_id
        idproducto = request.form.get("producto_id")  # Cambiado a producto_id
        precio_objetivo = request.form.get("precio_objetivo")

        # Validar que los datos sean correctos
        if not idusuario or not idproducto or not precio_objetivo:
             return jsonify({"error": f"Faltan datos: {request.form.to_dict()}"}), 400
        if not precio_objetivo.isdigit() and not precio_objetivo.replace('.', '', 1).isdigit():
            return jsonify({"error": "El precio objetivo debe ser un número válido"}), 400

        db = get_db()

        # Verificar si ya existe una alerta para este usuario y producto
        cursor = db.execute("SELECT * FROM ALERTAS WHERE idusuario = ? AND idproducto = ?", (idusuario, idproducto))
        if cursor.fetchone():
            return jsonify({"error": "Ya tienes una alerta para este producto"}), 409

        # Insertar la nueva alerta
        db.execute("INSERT INTO ALERTAS (idusuario, idproducto, precio_objetivo) VALUES (?, ?, ?)",
                   (idusuario, idproducto, float(precio_objetivo)))
        db.commit()

        return jsonify({"mensaje": "Alerta creada correctamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@alertas_bp.route("/ver_alertas")
def ver_alertas():
    idusuario = session.get("usuario_id")  # Asegúrate de que coincida con el formulario

    if not idusuario:
        return redirect(url_for("usuarios.mostrar_login"))

    db = get_db()
    cursor = db.execute("""
        SELECT A.idalerta, P.nombre, P.imagen, A.precio_objetivo
        FROM ALERTAS A
        JOIN PRODUCTOS P ON A.idproducto = P.idproducto
        WHERE A.idusuario = ?
    """, (idusuario,))

    alertas = cursor.fetchall()
    return render_template("alertas.html", alertas=alertas)    
@alertas_bp.route("/alertas/eliminar/<int:idalerta>", methods=["POST"])
def eliminar_alerta(idalerta):
    if "usuario_id" not in session:
        flash("Debes iniciar sesión para realizar esta acción.", "error")
        return redirect(url_for("usuarios.mostrar_login"))

    usuario_id = session["usuario_id"]
    db = get_db()
    db.execute("DELETE FROM ALERTAS WHERE idalerta = ? AND idusuario = ?", (idalerta, usuario_id))
    db.commit()

    flash("Alerta eliminada correctamente.", "success")
    return redirect(url_for("alertas.ver_alertas")) 