import tkinter as tk
from tkinter import ttk
import mysql.connector
import random
import time

# Conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="TRIVIA"
)

cursor = db.cursor()

preguntas = []
preguntas_seleccionadas = []
respuestas_correctas = 0
pregunta_actual = 0
tiempo_inicial = 0
cantidad = 16  
nombre_usuario = ""
ventana_resultados = None
entrada_nombre = None
entrada_instagram = None

# Función para seleccionar preguntas al azar
def seleccionar_preguntas(preguntas, cantidad):
    random.shuffle(preguntas)
    return preguntas[:cantidad]

# Función para comprobar la respuesta del usuario
def comprobar_respuesta(pregunta, respuesta_usuario):
    pregunta, respuesta_correcta = pregunta
    return respuesta_usuario == respuesta_correcta

# Función para calcular el puntaje
def calcular_puntaje(respuestas_correctas):
    return respuestas_correctas * 100

# Función para registrar el tiempo respondido
def registrar_tiempo(tiempo):
    cursor.execute("UPDATE Usuarios SET tiempo_respondido = %s WHERE id = 1", (tiempo,))
    db.commit()

# Función para registrar el resultado del usuario en la base de datos
def registrar_resultado_usuario(nombre_usuario, red_social, puntaje, tiempo_total):
    try:
        insert_query = "INSERT INTO usuarios (nombre, redes, puntaje, tiempo_respondido) VALUES (%s, %s, %s, %s)"
        data = (nombre_usuario, red_social, puntaje, tiempo_total)
        cursor.execute(insert_query, data)
        db.commit()
    except Exception as e:
        print("Error:", str(e))

# Función para obtener los resultados de la base de datos
def obtener_resultados():
    try:
        cursor.execute("SELECT nombre, puntaje, tiempo_respondido FROM Usuarios")
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print("Error al obtener resultados:", str(e))
        return []

# Función para cargar preguntas y respuestas desde la base de datos
def cargar_preguntas_respuestas():
    query = "SELECT pregunta, respuesta FROM preguntas"
    cursor.execute(query)
    preguntas = cursor.fetchall()
    return preguntas

# Función para comenzar el juego
def comenzar_juego(nombre, instagram):
    global nombre_usuario
    nombre_usuario = nombre

    ventana_bienvenida.destroy()
    abrir_ventana_listo()

def abrir_ventana_listo():
    ventana_listo = tk.Toplevel()
    ventana_listo.title("TRIVIA ISAUI")
    ventana_listo.geometry("800x600")
    ventana_listo.config(bg="lavender")

    def comenzar_juego_desde_ventana_listo():
        ventana_listo.destroy()
        abrir_ventana_juego()

    mensaje_listo = tk.Label(ventana_listo, text="¿Estás listo?", font=("computerfont", 45))
    mensaje_listo.pack(pady=20)

    boton_jugar = tk.Button(ventana_listo, text="JUGAR", font=("Gameplay", 15), bg="white", fg="black", borderwidth=20, relief="solid", width=6, height=3, command=comenzar_juego_desde_ventana_listo)
    boton_jugar.pack(pady=20)

    ventana_listo.mainloop()

# Función para abrir la ventana del juego
def abrir_ventana_juego():
    ventana_juego = tk.Toplevel()
    ventana_juego.title("TRIVIA ISAUI")
    ventana_juego.geometry("800x600")
    ventana_juego.config(bg="lavender")

    preguntas = cargar_preguntas_respuestas()
    preguntas_seleccionadas = seleccionar_preguntas(preguntas, cantidad)
    respuestas_correctas = 0
    pregunta_actual = 0
    tiempo_inicial = time.time()

    def siguiente_pregunta():
        global pregunta_actual, respuestas_correctas

        if pregunta_actual < len(preguntas_seleccionadas) - 1:
            pregunta_actual += 1
            actualizar_pregunta()
        else:
            feedback_label.config(text=f"Juego terminado. Preguntas correctas: {respuestas_correctas}")

            # Al final del juego, muestra los resultados
            finalizar_juego()

        boton_siguiente.config(state="disabled")
        for boton in botones_respuestas:
            boton.config(state="active")

    def generar_respuestas():
        pregunta, respuesta_correcta = preguntas_seleccionadas[pregunta_actual]
        respuestas = [respuesta_correcta]
        while len(respuestas) < 3:
            respuesta_incorrecta = random.choice(preguntas)[1]
            if respuesta_incorrecta not in respuestas:
                respuestas.append(respuesta_incorrecta)
        random.shuffle(respuestas)
        return respuestas

    def verificar_respuesta(respuesta):
        global respuestas_correctas
        if respuesta == preguntas_seleccionadas[pregunta_actual][1]:
            respuestas_correctas += 1
            feedback_label.config(text="¡Respuesta correcta!", fg="green")
        else:
            feedback_label.config(text="Respuesta incorrecta", fg="red")

        boton_siguiente.config(state="active")
        for boton in botones_respuestas:
            boton.config(state="disabled")

        siguiente_pregunta()

    def actualizar_pregunta():
        respuestas = generar_respuestas()
        pregunta, _ = preguntas_seleccionadas[pregunta_actual]
        pregunta_label.config(text=pregunta)
        for i, boton in enumerate(botones_respuestas):
            boton.config(text=respuestas[i], command=lambda resp=respuestas[i]: verificar_respuesta(resp))

    pregunta_label = tk.Label(ventana_juego, text="", wraplength=800, font=("Arial", 20), bg="pink" )
    pregunta_label.pack(padx=20, pady=20)

    respuestas_frame = tk.Frame(ventana_juego)
    respuestas_frame.pack(padx=20, pady=20)

    botones_respuestas = []
    for i in range(3):
        boton = tk.Button(respuestas_frame, text="", font=("Arial", 16), fg= "dark slate blue")
        boton.pack(pady=10)
        botones_respuestas.append(boton)

    feedback_label = tk.Label(ventana_juego, text="", font=("Arial", 16), fg="white")
    feedback_label.pack(pady=20)

    boton_siguiente = tk.Button(ventana_juego, text="Siguiente", font=("Arial", 16), state="disabled", command=siguiente_pregunta)
    boton_siguiente.pack(side="right", padx=20, pady=20)

    actualizar_pregunta()

ventana_resultados = None
ventana_usuario = None

def finalizar_juego():
    global ventana_resultados
    puntaje = calcular_puntaje(respuestas_correctas)
    tiempo_total = round(time.time() - tiempo_inicial, 2)

    registrar_resultado_usuario(nombre_usuario, entrada_instagram.get() if entrada_instagram else "", puntaje, tiempo_total)

    mostrar_resultados_usuario(nombre_usuario, entrada_instagram.get() if entrada_instagram else "", puntaje, tiempo_total)

def mostrar_resultados_usuario(nombre, red_social, puntaje, tiempo):
    global ventana_usuario
    if ventana_usuario:
        ventana_usuario.destroy()

    ventana_usuario = tk.Toplevel()
    ventana_usuario.title(f'Resultados para {nombre}')

    etiqueta_nombre = tk.Label(ventana_usuario, text=f"Nombre: {nombre}", font=('Arial', 16))
    etiqueta_nombre.pack()

    etiqueta_red_social = tk.Label(ventana_usuario, text=f"Red Social: {red_social}", font=('Arial', 16))
    etiqueta_red_social.pack()

    etiqueta_puntaje = tk.Label(ventana_usuario, text=f"Puntaje: {puntaje} puntos", font=('Arial', 16))
    etiqueta_puntaje.pack()

    etiqueta_tiempo = tk.Label(ventana_usuario, text=f"Tiempo: {tiempo} segundos", font=('Arial', 16))
    etiqueta_tiempo.pack()


def abrir_ventana_resultados():
    if entrada_nombre is not None and entrada_instagram is not None:
        ventana_resultados = tk.Toplevel()
        ventana_resultados.title("Resultados del Juego")

        etiqueta_nombre = tk.Label(ventana_resultados, text=f"Nombre: {entrada_nombre.get()}", font=("Arial", 16))
        etiqueta_nombre.pack()

        etiqueta_red_social = tk.Label(ventana_resultados, text=f"Red Social: {entrada_instagram.get()}", font=("Arial", 16))
        etiqueta_red_social.pack()

        puntaje = calcular_puntaje(respuestas_correctas)
        etiqueta_puntaje = tk.Label(ventana_resultados, text=f"Puntaje: {puntaje} puntos", font=("Arial", 16))
        etiqueta_puntaje.pack()

        tiempo_total = round(time.time() - tiempo_inicial, 2)
        etiqueta_tiempo = tk.Label(ventana_resultados, text=f"Tiempo total: {tiempo_total} segundos", font=("Arial", 16))
        etiqueta_tiempo.pack()


# Ventana de bienvenida
ventana_bienvenida = tk.Tk()
ventana_bienvenida.title("TRIVIA ISAUI")
ventana_bienvenida.geometry("800x600")
ventana_bienvenida.config(bg="lavender")

marco_centro = tk.Frame(ventana_bienvenida)
marco_centro.pack(expand=True)

etiqueta_bienvenida = tk.Label(marco_centro, text="BIENVENIDOS A TRIVIA ISAUI", font=("computerfont", 45))
etiqueta_bienvenida.pack(pady=20)

etiqueta_nombre = tk.Label(marco_centro, text="Nombre:")
etiqueta_nombre.pack()

entrada_nombre = tk.Entry(marco_centro)
entrada_nombre.pack()

etiqueta_instagram = tk.Label(marco_centro, text="Instagram:")
etiqueta_instagram.pack()

entrada_instagram = tk.Entry(marco_centro)
entrada_instagram.pack()

boton_inicio = tk.Button(ventana_bienvenida, text="PLAY", font=("Gameplay", 15), bg="white", fg="black", borderwidth=20, relief="solid", width=6, height=3, command=lambda: comenzar_juego(entrada_nombre.get(), entrada_instagram.get()))
boton_inicio.pack(pady=100)

ventana_bienvenida.mainloop()

