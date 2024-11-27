import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Configuración de Azure Storage
AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=biometria10;AccountKey=NQHiBY0gLPVJSkb53871s281vtHAcSUezY26w9oe0i80IPr6B1yCQlVB4NmtvmWHw7NtLjC0ymQK+AStW6DQqw==;EndpointSuffix=core.windows.net"  # Reemplaza con tu cadena de conexión
AZURE_CONTAINER_NAME = "biometria-solicitudes"  # Reemplaza con el nombre de tu contenedor

# Inicializar cliente de Azure Blob
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

# Crear contenedor si no existe
try:
    container_client.create_container()
except Exception as e:
    print("El contenedor ya existe o hubo un error:", e)

# Obtener el directorio actual donde se encuentra el archivo .py
directorio_actual = os.path.dirname(os.path.abspath(__file__))

# Crear las carpetas locales dentro del directorio actual
CARPETA_INICIOS_SESION = os.path.join(directorio_actual, "Inicios de sesion")
CARPETA_REGISTRO_USUARIOS = os.path.join(directorio_actual, "Registro de usuarios")

# Crear las carpetas si no existen
os.makedirs(CARPETA_INICIOS_SESION, exist_ok=True)
os.makedirs(CARPETA_REGISTRO_USUARIOS, exist_ok=True)

usuario_actual = None  # Almacena la información del usuario logueado

# Funciones para la autenticación
def registrar_usuario(nombre, correo, contrasena, confirmar):
    if not all([nombre, correo, contrasena, confirmar]):
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return False

    if contrasena != confirmar:
        messagebox.showwarning("Advertencia", "Las contraseñas no coinciden.")
        return False

    archivo_usuario = os.path.join(CARPETA_REGISTRO_USUARIOS, f"{correo}.txt")
    if os.path.exists(archivo_usuario):
        messagebox.showwarning("Advertencia", "El usuario ya está registrado.")
        return False

    with open(archivo_usuario, "w", encoding="utf-8") as archivo:
        archivo.write(f"{nombre}\n{correo}\n{contrasena}\n")
    return True

def iniciar_sesion(correo, contrasena):
    archivo_usuario = os.path.join(CARPETA_REGISTRO_USUARIOS, f"{correo}.txt")
    if not os.path.exists(archivo_usuario):
        return None

    with open(archivo_usuario, "r", encoding="utf-8") as archivo:
        datos = archivo.readlines()
        nombre, correo_guardado, contrasena_guardada = [dato.strip() for dato in datos]

        if correo == correo_guardado and contrasena == contrasena_guardada:
            return {"nombre": nombre, "correo": correo}

    return None

# Funciones para interactuar con Azure Storage
def guardar_archivo_en_azure(nombre_archivo, contenido):
    try:
        blob_client = container_client.get_blob_client(nombre_archivo)
        blob_client.upload_blob(contenido, overwrite=True)
        print(f"Archivo {nombre_archivo} subido a Azure Storage.")
    except Exception as e:
        print("Error subiendo archivo a Azure Storage:", e)

def listar_archivos_en_azure():
    try:
        blobs = container_client.list_blobs()
        print("Archivos en Azure Storage:")
        for blob in blobs:
            print(blob.name)
    except Exception as e:
        print("Error listando archivos en Azure Storage:", e)

# Sección de solicitud
def abrir_seccion_solicitud():
    def enviar_datos():
        nombre = entry_nombre.get()
        rut = entry_rut.get()
        carrera_semestre = entry_carrera_semestre.get()
        material = text_material.get("1.0", tk.END).strip()  # Campo de texto grande
        motivo = entry_motivo.get()

        if not all([nombre, rut, carrera_semestre, material, motivo]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        # Guardar la solicitud vinculada al usuario
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        nombre_archivo_fecha = datetime.now().strftime("%d-%m-%Y_%H-%M")
        nombre_archivo = f"{nombre}_{rut}_{nombre_archivo_fecha}.txt"
        contenido = (
            f"Fecha y hora: {fecha_hora}\n"
            f"Usuario: {usuario_actual['nombre']} ({usuario_actual['correo']})\n"
            f"Nombre: {nombre}\n"
            f"RUT: {rut}\n"
            f"Carrera y semestre: {carrera_semestre}\n"
            f"Material y equipamiento: {material}\n"
            f"Motivo: {motivo}\n"
        )

        # Guardar en Azure Storage
        guardar_archivo_en_azure(nombre_archivo, contenido)
        messagebox.showinfo("Éxito", "Solicitud guardada exitosamente.")
        seccion_solicitud.destroy()

    # Crear la ventana
    seccion_solicitud = tk.Toplevel(root)
    seccion_solicitud.title("Solicitud")
    seccion_solicitud.geometry("600x600")

    # Configurar el diseño
    tk.Label(seccion_solicitud, text="Formulario de Solicitud", font=("Arial", 14, "bold")).pack(pady=10)

    frame_formulario = tk.Frame(seccion_solicitud)
    frame_formulario.pack(padx=20, pady=10, fill="x")

    # Campos del formulario
    def agregar_campo(frame, texto, es_text_area=False):
        tk.Label(frame, text=texto, anchor="w").pack(fill="x")
        if es_text_area:
            text = tk.Text(frame, height=5, width=50)
            text.pack(fill="x", pady=5)
            return text
        else:
            entry = tk.Entry(frame)
            entry.pack(fill="x", pady=5)
            return entry

    entry_nombre = agregar_campo(frame_formulario, "Nombre completo")
    entry_rut = agregar_campo(frame_formulario, "RUT")
    entry_carrera_semestre = agregar_campo(frame_formulario, "Carrera y semestre")
    text_material = agregar_campo(frame_formulario, "Material y equipamiento (descripción amplia)", es_text_area=True)
    entry_motivo = agregar_campo(frame_formulario, "Motivo de la solicitud")

    # Botón para enviar
    tk.Button(seccion_solicitud, text="Enviar", command=enviar_datos).pack(pady=20)

# Sección de inicio de sesión
def abrir_inicio_sesion():
    def iniciar():
        correo = entry_correo.get()
        contrasena = entry_contrasena.get()
        global usuario_actual
        usuario_actual = iniciar_sesion(correo, contrasena)

        if usuario_actual:
            messagebox.showinfo("Éxito", "Inicio de sesión exitoso.")
            inicio_sesion.destroy()
            mostrar_menu_principal()
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")

    inicio_sesion = tk.Toplevel(root)
    inicio_sesion.title("Iniciar Sesión")
    inicio_sesion.geometry("300x200")

    tk.Label(inicio_sesion, text="Correo electrónico").pack()
    entry_correo = tk.Entry(inicio_sesion)
    entry_correo.pack(pady=5)

    tk.Label(inicio_sesion, text="Contraseña").pack()
    entry_contrasena = tk.Entry(inicio_sesion, show="*")
    entry_contrasena.pack(pady=5)

    tk.Button(inicio_sesion, text="Iniciar sesión", command=iniciar).pack(pady=10)

# Sección de registro
def abrir_registro():
    def registrar():
        if registrar_usuario(entry_nombre.get(), entry_correo.get(), entry_contrasena.get(), entry_confirmar.get()):
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            registro.destroy()

    registro = tk.Toplevel(root)
    registro.title("Registrar Usuario")
    registro.geometry("300x300")

    tk.Label(registro, text="Nombre completo").pack()
    entry_nombre = tk.Entry(registro)
    entry_nombre.pack(pady=5)

    tk.Label(registro, text="Correo electrónico").pack()
    entry_correo = tk.Entry(registro)
    entry_correo.pack(pady=5)

    tk.Label(registro, text="Contraseña").pack()
    entry_contrasena = tk.Entry(registro, show="*")
    entry_contrasena.pack(pady=5)

    tk.Label(registro, text="Confirmar contraseña").pack()
    entry_confirmar = tk.Entry(registro, show="*")
    entry_confirmar.pack(pady=5)

    tk.Button(registro, text="Registrar", command=registrar).pack(pady=10)

# Menú principal
def mostrar_menu_principal():
    menu_principal = tk.Toplevel(root)
    menu_principal.title("Menú Principal")
    menu_principal.geometry("300x200")

    tk.Button(menu_principal, text="Solicitar", command=abrir_seccion_solicitud).pack(pady=10)
    tk.Button(menu_principal, text="Cerrar sesión", command=menu_principal.destroy).pack(pady=10)

# Ventana principal
root = tk.Tk()
root.title("Aplicación de Registro y Solicitudes")
root.geometry("300x200")

tk.Button(root, text="Iniciar sesión", command=abrir_inicio_sesion).pack(pady=10)
tk.Button(root, text="Registrar usuario", command=abrir_registro).pack(pady=10)

root.mainloop()
