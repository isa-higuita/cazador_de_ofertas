from flask import Flask, g, render_template, request, session
import sqlite3
from usuarios import usuarios_bp
from productos import productos_bp
from precios import precios_bp
from alertas import alertas_bp
from lista_deseos import lista_deseos_bp

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

DATABASE = "cazador.db"

def get_db():
    """Conecta a la base de datos y retorna el objeto de conexión."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Para obtener los resultados como diccionarios
    return db

@app.teardown_appcontext
def close_connection(exception=None):
    """Cierra la conexión a la base de datos al finalizar la solicitud."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET'])
def index():
    """Ruta principal que maneja la búsqueda y muestra los productos."""
    db = get_db()
    busqueda = request.args.get('busqueda', '')  # Obtener la búsqueda desde el formulario

    # Consulta para obtener productos con sus precios más recientes
    query = """
        SELECT productos.idproducto, productos.nombre, productos.descripcion, productos.imagen, 
               precios.precio, precios.tienda
        FROM productos
        JOIN (
            SELECT idproducto, precio, tienda
            FROM PRECIOS
            WHERE (idproducto, fecha) IN (
                SELECT idproducto, MAX(fecha)
                FROM PRECIOS
                GROUP BY idproducto
            )
        ) AS precios ON productos.idproducto = precios.idproducto
    """

    # Parámetros para la consulta, en caso de que haya una búsqueda
    params = []
    if busqueda:
        query += " WHERE productos.nombre LIKE ?"
        params.append('%' + busqueda + '%')

    productos = db.execute(query, params).fetchall()  # Ejecutar la consulta y obtener los productos

    # Pasar los productos y la búsqueda a la plantilla
    return render_template('index.html', productos=productos, busqueda=busqueda, mostrar_navbar=True)

# Registrar Blueprints
app.register_blueprint(usuarios_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(precios_bp)
app.register_blueprint(alertas_bp)
app.register_blueprint(lista_deseos_bp)

if __name__ == "__main__":
    app.run(debug=True)
