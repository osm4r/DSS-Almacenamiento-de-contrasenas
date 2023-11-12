import sqlite3

def mostrar_contenido_base_datos(nombre_base_datos):
    try:
        conexion = sqlite3.connect(nombre_base_datos)
        cursor = conexion.cursor()

        # Obtener todos los nombres de tablas en la base de datos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()

        for tabla in tablas:
            nombre_tabla = tabla[0]
            print(f"\nContenido de la tabla '{nombre_tabla}':")

            cursor.execute(f"SELECT * FROM {nombre_tabla};")
            filas = cursor.fetchall()

            encabezados = [descripcion[0] for descripcion in cursor.description]
            print("|".join(encabezados))

            for fila in filas:
                print("|".join(map(str, fila)))

        conexion.close()

    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")

mostrar_contenido_base_datos('password.db')
