from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

usuarios_bp = Blueprint('usuarios', __name__)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("cazador.db")
        db.row_factory = sqlite3.Row
    return db

@usuarios_bp.route("/registro", methods=["GET"])
def mostrar_registro():
    return render_template("registro.html")

@usuarios_bp.route("/registro", methods=["POST"])
def registrar_usuario():
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    contraseña = request.form.get("contraseña")

    if not nombre or not email or not contraseña:
        flash("Todos los campos son obligatorios", "error")
        return redirect(url_for("usuarios.mostrar_registro"))

    contraseña_hash = generate_password_hash(contraseña)

    db = get_db()
    try:
        db.execute("INSERT INTO USUARIOS (nombre, email, contraseña) VALUES (?, ?, ?)", 
                   (nombre, email, contraseña_hash))
        db.commit()
        flash("Usuario registrado exitosamente. Por favor, inicia sesión.", "success")
    except sqlite3.IntegrityError:
        flash("El correo ya está registrado. Intenta con otro.", "error")
        return redirect(url_for("usuarios.mostrar_registro"))

    return redirect(url_for("usuarios.mostrar_login"))

@usuarios_bp.route("/login", methods=["GET"])
def mostrar_login():
    return render_template("registro.html")  # Puedes usar la misma plantilla para registro e inicio de sesión

@usuarios_bp.route("/login", methods=["POST"])
def iniciar_sesion():
    email = request.form.get("email")
    contraseña = request.form.get("contraseña")

    if not email or not contraseña:
        flash("Todos los campos son obligatorios", "error")
        return redirect(url_for("usuarios.mostrar_login"))

    db = get_db()
    usuario = db.execute("SELECT idusuario, nombre, email, contraseña FROM USUARIOS WHERE email = ?", (email,)).fetchone()

    if not usuario or not check_password_hash(usuario["contraseña"], contraseña):
        flash("Correo o contraseña incorrectos", "error")
        return redirect(url_for("usuarios.mostrar_login"))

    session["usuario_id"] = usuario["idusuario"]
    session["usuario_nombre"] = usuario["nombre"]
    flash(f"Bienvenido, {usuario['nombre']}!", "success")
    return redirect(url_for("index")) 

@usuarios_bp.route("/logout")
def cerrar_sesion():
    session.clear()
    flash("Has cerrado sesión exitosamente.", "success")
    return redirect(url_for("usuarios.mostrar_login"))


