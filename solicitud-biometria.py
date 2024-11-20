import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime

# Definir las rutas
BASE_RUTA = r"C:\Users\Dilan\Desktop\solicitud Biometria"
CARPETA_SOLICITUDES = os.path.join(BASE_RUTA, "Solicitudes")
CARPETA_INICIOS_SESION = os.path.join(BASE_RUTA, "Inicios de sesion")
CARPETA_REGISTRO_USUARIOS = os.path.join(BASE_RUTA, "Registro de usuarios")

# Crear carpetas si no existen
for carpeta in [CARPETA_SOLICITUDES, CARPETA_INICIOS_SESION, CARPETA_REGISTRO_USUARIOS]:
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

# Usuario actual que inició sesión
usuario_actual = {"nombre": None, "correo": None}


# Función para registrar un nuevo usuario
def registrar_usuario(nombre, correo, contrasena, confirmacion):
    if not correo or not nombre or not contrasena or not confirmacion:
        messagebox.showwarning("Error", "Todos los campos son obligatorios.")
        return False

    if contrasena != confirmacion:
        messagebox.showwarning("Error", "Las contraseñas no coinciden.")
        return False

    # Guardar las credenciales en el archivo correspondiente
    archivo_registro = os.path.join(CARPETA_REGISTRO_USUARIOS, f"{correo}.txt")
    if os.path.exists(archivo_registro):
        messagebox.showwarning("Error", "El correo electrónico ya está registrado.")
        return False

    with open(archivo_registro, "w", encoding="utf-8") as archivo:
        archivo.write(f"Nombre: {nombre}\n")
        archivo.write(f"Correo: {correo}\n")
        archivo.write(f"Contraseña: {contrasena}\n")

    messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
    return True


# Función para verificar inicio de sesión
def iniciar_sesion(correo, contrasena):
    archivo_registro = os.path.join(CARPETA_REGISTRO_USUARIOS, f"{correo}.txt")
    if os.path.exists(archivo_registro):
        with open(archivo_registro, "r", encoding="utf-8") as archivo:
            credenciales = archivo.readlines()
            nombre_guardado = credenciales[0].split(":")[1].strip()
            correo_guardado = credenciales[1].split(":")[1].strip()
            contrasena_guardada = credenciales[2].split(":")[1].strip()

            if correo == correo_guardado and contrasena == contrasena_guardada:
                usuario_actual["nombre"] = nombre_guardado
                usuario_actual["correo"] = correo_guardado
                messagebox.showinfo("Éxito", f"Bienvenido, {nombre_guardado}!")
                return True
            else:
                messagebox.showerror("Error", "Correo o contraseña incorrectos.")
                return False
    else:
        messagebox.showerror("Error", "Correo no registrado.")
        return False


# Función para abrir la ventana de registro
def abrir_registro():
    def registrar():
        # Obtener los valores del formulario
        nombre = entry_nombre.get()
        correo = entry_correo.get()
        contrasena = entry_contrasena.get()
        confirmacion = entry_confirmar.get()

        # Llamar a la función de registro
        if registrar_usuario(nombre, correo, contrasena, confirmacion):
            registro_window.destroy()

    registro_window = tk.Toplevel(root)
    registro_window.title("Registrar Usuario")
    registro_window.geometry("300x300")

    # Definir las entradas
    tk.Label(registro_window, text="Nombre").grid(row=0, column=0)
    entry_nombre = tk.Entry(registro_window)
    entry_nombre.grid(row=0, column=1)

    tk.Label(registro_window, text="Correo").grid(row=1, column=0)
    entry_correo = tk.Entry(registro_window)
    entry_correo.grid(row=1, column=1)

    tk.Label(registro_window, text="Contraseña").grid(row=2, column=0)
    entry_contrasena = tk.Entry(registro_window, show="*")
    entry_contrasena.grid(row=2, column=1)

    tk.Label(registro_window, text="Confirmar Contraseña").grid(row=3, column=0)
    entry_confirmar = tk.Entry(registro_window, show="*")
    entry_confirmar.grid(row=3, column=1)

    # Botón para registrar
    tk.Button(registro_window, text="Registrar", command=registrar).grid(row=4, columnspan=2)


# Función para abrir la ventana de inicio de sesión
def abrir_inicio_sesion():
    def iniciar():
        if iniciar_sesion(entry_correo.get(), entry_contrasena.get()):
            login_window.destroy()
            abrir_seccion_principal()

    login_window = tk.Toplevel(root)
    login_window.title("Iniciar sesión")
    login_window.geometry("300x200")

    tk.Label(login_window, text="Correo:").grid(row=0, column=0)
    tk.Label(login_window, text="Contraseña:").grid(row=1, column=0)

    entry_correo = tk.Entry(login_window)
    entry_correo.grid(row=0, column=1)
    entry_contrasena = tk.Entry(login_window, show="*")
    entry_contrasena.grid(row=1, column=1)

    tk.Button(login_window, text="Iniciar sesión", command=iniciar).grid(row=2, columnspan=2)


# Función que abre las secciones principales una vez que el usuario inicia sesión
def abrir_seccion_principal():
    principal_window = tk.Toplevel(root)
    principal_window.title("Secciones del sistema")
    principal_window.geometry("300x200")

    tk.Button(principal_window, text="POR VER").pack(pady=10)
    tk.Button(principal_window, text="Solicitud", command=abrir_seccion_solicitud).pack(pady=10)


# Función para abrir la sección de solicitud
def abrir_seccion_solicitud():
    def enviar_datos():
        nombre = entry_nombre.get()
        rut = entry_rut.get()
        carrera_semestre = entry_carrera_semestre.get()
        material = entry_material.get()
        motivo = entry_motivo.get()

        if not all([nombre, rut, carrera_semestre, material, motivo]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        # Guardar la solicitud vinculada al usuario
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        nombre_archivo_fecha = datetime.now().strftime("%d-%m-%Y_%H-%M")
        archivo_nombre = os.path.join(
            CARPETA_SOLICITUDES, f"{nombre}_{rut}_{nombre_archivo_fecha}.txt"
        )

        with open(archivo_nombre, "w", encoding="utf-8") as archivo:
            archivo.write(f"Fecha y hora: {fecha_hora}\n")
            archivo.write(f"Usuario: {usuario_actual['nombre']} ({usuario_actual['correo']})\n")
            archivo.write(f"Nombre: {nombre}\n")
            archivo.write(f"RUT: {rut}\n")
            archivo.write(f"Carrera y semestre: {carrera_semestre}\n")
            archivo.write(f"Material y equipamiento: {material}\n")
            archivo.write(f"Motivo: {motivo}\n")

        messagebox.showinfo("Éxito", "Solicitud guardada exitosamente.")
        seccion_solicitud.destroy()

    seccion_solicitud = tk.Toplevel(root)
    seccion_solicitud.title("Solicitud")
    seccion_solicitud.geometry("400x400")

    fields = [
        ("Nombre", "entry_nombre"),
        ("RUT", "entry_rut"),
        ("Carrera y semestre", "entry_carrera_semestre"),
        ("Material y equipamiento", "entry_material"),
        ("Motivo", "entry_motivo"),
    ]

    entries = {}
    for i, (label_text, entry_name) in enumerate(fields):
        tk.Label(seccion_solicitud, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        entry = tk.Entry(seccion_solicitud, width=30)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[entry_name] = entry

    entry_nombre = entries["entry_nombre"]
    entry_rut = entries["entry_rut"]
    entry_carrera_semestre = entries["entry_carrera_semestre"]
    entry_material = entries["entry_material"]
    entry_motivo = entries["entry_motivo"]

    tk.Button(seccion_solicitud, text="Enviar", command=enviar_datos).grid(row=len(fields), column=0, columnspan=2, pady=20)


# Ventana principal
root = tk.Tk()
root.title("Sistema de Solicitudes")
root.geometry("300x200")

# Botones de inicio
tk.Button(root, text="Iniciar sesión", command=abrir_inicio_sesion).pack(pady=10)
tk.Button(root, text="Registrar Usuario", command=abrir_registro).pack(pady=10)

root.mainloop()
