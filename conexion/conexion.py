import mysql.connector

def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",  
        database="desarrollo_web",
        port=3307   # <--- Aquí el puerto correcto
    )
    return conexion
