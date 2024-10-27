import tkinter
from tkinter import ttk
from tkinter import messagebox, filedialog, PhotoImage
import tkinter.commondialog
from PIL import Image, ImageTk
import sqlite3
import re
import io
import base64

# Conecto la base de datos SQLite (o bien, crea el archivo si no existe)
conexion = sqlite3.connect('pokedex_prueba.db')
cursor = conexion.cursor ()

# Crea tabla si no existe
cursor.execute ('''
    CREATE TABLE IF NOT EXISTS pokemon (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        hight TEXT NOT NULL,
        type TEXT NOT NULL,
        info TEXT NOT NULL,
        category TEXT NOT NULL,
        ability TEXT NOT NULL,
        imagen BLOB NOT NULL
    )
''')
conexion.commit ()

cursor.execute ('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL UNIQUE
    )
''')
conexion.commit ()
types = ['Agua','Planta','Eléctrico','Fantasma','Normal','Fuego','Tierra', 'Hada','Dragón', 'Veneno', 'Acero', 'Siniestro', 'Roca', 'Bicho', 'Volador', 'Psíquico', 'Lucha', 'Hielo']

window = tkinter.Tk ()
window.geometry ("800x500")
window.grid_columnconfigure (4, weight=0,pad=2)
window.title("POKÉDEX")
window.config(bg="Gainsboro")

global_image_blob=''
imagen_binaria = None  # Variable para almacenar el binario de la imagen

def seleccionar_imagen():
    """Esta función permite seleccionar una imagen"""
    global imagen_binaria
    ruta_imagen = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png")])
    if ruta_imagen:
        with open(ruta_imagen, 'rb') as archivo_imagen:
            imagen_binaria = archivo_imagen.read()
        messagebox.showinfo("Imagen seleccionada", f"Seleccionaste la imagen: {ruta_imagen}")

def cargar_imagen():
    """Función para cargar una imagen y convertirla en base64"""
    file_path = filedialog.askopenfilename(
        title="Selecciona una imagen", filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")]
    )
    if file_path:
        # Convertir imagen a base64 sin Pillow
        with open(file_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        global  global_image_blob
        global_image_blob= image_base64
        return image_base64

def guardar_imagen_en_bd(new_window):
    """Simular el guardado del valor base64 en una base de datos"""
    imagen_base64 = cargar_imagen()
    if imagen_base64:
        #print("Imagen en formato base64 lista para guardar en la base de datos:")
        #print(imagen_base64)
        cargar_imagen_desde_base64(imagen_base64,new_window)

def cargar_imagen_desde_base64(base64_string,new_window,label_imagen=None):
    try:
        if base64_string:
            image_bytes = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_bytes))
            image.thumbnail((150,150))
            image_tk = ImageTk.PhotoImage(image)
            show_image=''
            if label_imagen:
                print('entra?')
                label_imagen.config(image=image_tk)
                label_imagen.image = image_tk 
                label_imagen.grid(row=11, column=0, sticky=("N","W"), padx=550)
            else:
                show_image = tkinter.Label(new_window)
                show_image.grid(row=7, column=1, sticky="e", padx=10, pady=5)
                show_image.config(image = image_tk)
                show_image.image = image_tk
                new_window.lift()
    except:
       print('no existe imagen')
    
def agregar_pokemon():
    """Esta función permite agregar un nuevo Pokémon"""
    # Nos aseguramos de que todas las entradas estén en la misma columna con un padding similar
    new_window = tkinter.Toplevel(window)
    new_window.title("Agregar Pokémon")
    new_window.geometry("350x450")
    entry_nombre = tkinter.Entry(new_window)
    entry_nombre.grid(row=1, column=1, padx=10, pady=5)
    entry_category = tkinter.Entry(new_window)
    entry_category.grid(row=2, column=1, padx=10, pady=5)
    entry_info = tkinter.Entry(new_window)
    entry_info.grid(row=3, column=1, padx=10, pady=5)
    entry_type = ttk.Combobox(new_window,values=types,state='readonly')
    entry_type.grid(row=4, column=1, padx=10, pady=5)
    entry_type.grid(row=4, column=1, padx=10, pady=5)
    entry_ability = tkinter.Entry(new_window)
    entry_ability.grid(row=5, column=1, padx=10, pady=5)
    
    button_image =  tkinter.Button(new_window,text='Cargar imagen',command=lambda:guardar_imagen_en_bd(new_window))
    button_image.grid(row=6,column=1,padx=10,pady=5)
    
    label_nombre = tkinter.Label(new_window, text="Nombre:")
    label_nombre.grid(row=1, column=0, sticky="e", padx=10, pady=5)  # Usamos 'sticky' para alinearlas
    label_category = tkinter.Label(new_window, text="Categoría:")
    label_category.grid(row=2, column=0, sticky="e", padx=10, pady=5)
    label_info = tkinter.Label(new_window, text="Información:")
    label_info.grid(row=3, column=0, sticky="e", padx=10, pady=5)
    label_type = tkinter.Label(new_window, text="Tipo:")
    label_type.grid(row=4, column=0, sticky="e", padx=10, pady=5)
    label_ability = tkinter.Label(new_window, text="Habilidad:")
    label_ability.grid(row=5, column=0, sticky="e", padx=10, pady=5)
    label_imagen = tkinter.Label(new_window, text="Imagen:")
    label_imagen.grid(row=6, column=0, sticky="e", padx=10, pady=5)
    
    button_image =  tkinter.Button(new_window,text='Guardar',command=lambda:(guardar(
        entry_nombre.get().strip(), 
        entry_type.get().strip(),
        entry_info.get().strip(), 
        entry_category.get().strip(),
        entry_ability.get().strip()),
        new_window.destroy())
        )
    button_image.grid(row=8,column=1,padx=10,pady=5)
    
def guardar(nombre,hight,info,category,ability):

    # Validamos los datos y sumamos regex
    if not re.match (r"^[A-Za-z\s]+$", nombre):
        messagebox.showerror("¡OOPS!", "El nombre sólo puede tener letras y espacios. Intentá de nuevo, por favor.")
        return
    if len (info) == 0 or len (category) == 0 or len (ability) == 0:
        messagebox.showerror("¡OOPS!", "Rellená todos los campos correctamente.")
        return

    cursor.execute ("SELECT id FROM pokemon WHERE nombre = ?", (nombre,))
    pokemon_existe = cursor.fetchone ()

    if pokemon_existe:
        cursor.execute ('''
            UPDATE pokemon
            SET hight = ?, info = ?, category = ?, ability = ?, imagen = ?
            WHERE nombre = ?
        ''', (hight, info, category, ability, global_image_blob, nombre))
        messagebox.showinfo("MODIFICACIÓN EXITOSA", f"Modificaste correctamente a {nombre} en la Pokédex ¡Muchas gracias por tu aporte!")
    else:
        cursor.execute ('''
            INSERT INTO pokemon (nombre, hight, info, category, ability, imagen)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, hight, info, category, ability, global_image_blob))
        messagebox.showinfo ("MODIFICACIÓN EXITOSA", f"Añadiste a {nombre} exitosamente.")

    conexion.commit ()
    load_grid()

def mostrar_imagen(pokemon_nombre):
    cursor.execute("SELECT imagen FROM pokemon WHERE nombre = ?", (pokemon_nombre,))
    resultado = cursor.fetchone()

    if resultado:
        imagen_blob = resultado[0]
        imagen = Image.open(io.BytesIO(imagen_blob))
        imagen_tk = ImageTk.PhotoImage(imagen)

        # label_imagen.config(image = imagen_tk)
        # label_imagen.image = imagen_tk
    else:
        messagebox.showerror("ERROR", f"No se encontró el Pokémon '{pokemon_nombre}'.")

def load_grid():
    for row in grilla.get_children():
        grilla.delete(row)
    cursor.execute ("SELECT * FROM pokemon")
    pokemons = cursor.fetchall()

    for poke in pokemons:
        grilla.insert(parent='',index='end',values=(poke))
        
def busqueda(event):
    for row in grilla.get_children():
        grilla.delete(row)
    nombre = input_buscar.get().lower()
    cursor.execute ("SELECT * FROM pokemon WHERE nombre LIKE ?", ('%' + nombre + '%',))
    pokemons = cursor.fetchall ()
    
    
    for poke in pokemons:
        grilla.insert(parent='',index='end',values=(poke))

def eliminar():
    try:
        select_poke = grilla.selection()[0]  # Obtener el item seleccionado en la grilla
        poke_values = grilla.item(select_poke, 'values')  # Obtener los valores del Pokémon

        # Mostrar el cuadro de confirmación con el nombre del Pokémon
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación", f"¿Deseas eliminar el Pokémon {poke_values[1]}?"
        )

        if confirmacion:
            # Si el usuario confirma la eliminación, eliminar el Pokémon de la grilla
            grilla.delete(select_poke)
            nombre = poke_values[1]

            # Valido los datos y sumamos regex
            if not re.match(r"^[A-Za-z\s]+$", nombre):
                messagebox.showerror("¡OOPS!", "El nombre sólo puede contener letras y espacios. Intentá nuevamente.")
                return

            cursor.execute("SELECT 1 FROM pokemon WHERE nombre = ?", (nombre,))
            pokemon_existe = cursor.fetchone()

            if pokemon_existe:
                cursor.execute("DELETE FROM pokemon WHERE nombre = ?", (nombre,))
                conexion.commit()
                #messagebox.showinfo("¡ÉXITO!", f"Pokémon eliminado correctamente")
                messagebox.showinfo("Eliminado", f"El Pokémon {poke_values[1]} ha sido eliminado.")
            else:
                messagebox.showerror("ERROR", f"El Pokémon no existe.")
            
          
        else:
            # Si el usuario cancela la eliminación
            messagebox.showinfo("Cancelado", "El Pokémon no ha sido eliminado.")
    except IndexError:
        # Si no se ha seleccionado ningún Pokémon
        messagebox.showwarning("Advertencia", "No has seleccionado ningún Pokémon.")
    
def modificar ():
    select_poke = grilla.selection()[0]
    poke_values = grilla.item(select_poke,'values')
    new_window = tkinter.Toplevel(window)
    new_window.title(f"Modificar pokemon - {poke_values[1]}")
    new_window.geometry("350x450")    
  
    entry_nombre = tkinter.Entry (new_window)
    entry_nombre.insert(0,poke_values[1])
    entry_nombre.grid (row=1, column=1, padx=10, pady=5)
    entry_type = tkinter.Entry (new_window)
    entry_type.insert(0,poke_values[4])
    entry_type.grid (row=2, column=1, padx=10, pady=5)
    entry_info = tkinter.Entry (new_window)
    entry_info.insert(0,poke_values[3])
    entry_info.grid (row=3, column=1, padx=10, pady=5)

    entry_category = ttk.Combobox(new_window,values=types,state='readonly')
    entry_category.set(poke_values[2])
    entry_category.grid (row=4, column=1, padx=10, pady=5)
    
    entry_ability = tkinter.Entry (new_window)
    entry_ability.insert(0,poke_values[5])
    entry_ability.grid (row=5, column=1, padx=10, pady=5)
    cargar_imagen_desde_base64(poke_values[6],new_window)

    label_nombre = tkinter.Label(new_window, text="Nombre:")
    label_nombre.grid(row=1, column=0, sticky="e", padx=10, pady=5)  # Usamos 'sticky' para alinearlas
    label_category = tkinter.Label(new_window, text="Categoría:")
    label_category.grid(row=2, column=0, sticky="e", padx=10, pady=5)
    label_info = tkinter.Label(new_window, text="Información:")
    label_info.grid(row=3, column=0, sticky="e", padx=10, pady=5)
    label_type = tkinter.Label(new_window, text="Tipo:")
    label_type.grid(row=4, column=0, sticky="e", padx=10, pady=5)
    label_ability = tkinter.Label(new_window, text="Habilidad:")
    label_ability.grid(row=5, column=0, sticky="e", padx=10, pady=5)
    label_imagen = tkinter.Label(new_window, text="Imagen:")
    label_imagen.grid(row=6, column=0, sticky="e", padx=10, pady=5)

    button_image =  tkinter.Button(new_window,text='Guardar',command=lambda:(guardar(
        entry_nombre.get().strip(), 
        entry_type.get().strip(),
        entry_info.get().strip(), 
        entry_category.get().strip(),
        entry_ability.get().strip()),
        new_window.destroy())
        )
    button_image.grid(row=8,column=1,padx=10,pady=5)

def view_info(event):
    select_poke = grilla.selection()[0]
    poke_values = grilla.item(select_poke,'values')
    cargar_imagen_desde_base64(poke_values[6],window,label_imagen)
    label_name.config(text=f"Nombre: {poke_values[1]}")
    label_tipo.config(text=f"Tipo: {poke_values[2]}")
    label_info.config(text=f"Información: {poke_values[3]}")
    
boton_agregar = tkinter.Button (window, text="Agregar Pokémon", command=agregar_pokemon, relief="raised", bg="Light Gray")
boton_agregar.grid (row=1, column=0,padx=470, pady=10,sticky="W")

boton_eliminar = tkinter.Button (window, text="Eliminar Pokémon", command=eliminar, relief="raised", bg="Light Gray")
boton_eliminar.grid (row=1, column=0,padx=350, pady=10,sticky="W")

boton_modificar = tkinter.Button (window, text="Modificar Pokémon", command=modificar, relief="raised", bg="Light Gray")
boton_modificar.grid (row=1, column=0,padx=220,pady=10,sticky="W")


label_buscar = tkinter.Label(window,text="Buscar")
label_buscar.grid(row=1, column=0,pady=5,padx=20,sticky='W')
input_buscar = tkinter.Entry(window)
input_buscar.grid (row=1, column=0, padx=60, pady=5,sticky='W')

input_buscar.bind("<KeyRelease>",busqueda)



grilla = ttk.Treeview(height=10)
grilla['columns'] =['#id',"Nombre", "Category"]
grilla.column("#0", width=0, stretch=tkinter.NO)
grilla.column("#id",width=100,minwidth=30)
grilla.column("Nombre",width=150,minwidth=30)
grilla.column("Category",width=150,minwidth=30)
grilla.heading("#id",text="id",anchor="w")
grilla.heading("Nombre",text="Nombre")
grilla.heading("Category",text="Tipo")



grilla.grid (row=11, column=0, padx=60,pady=10,sticky=('W','N'))
grilla.bind("<<TreeviewSelect>>", view_info)
label_imagen = tkinter.Label(window, text="Imagen del Pokémon")
#label_imagen.grid(row=11, column=1, padx=200, pady=10, sticky='W')
load_grid()
label_name = tkinter.Label(window)
label_name.grid(row=11, column=0,pady=65,padx=20,sticky=("S"))
label_tipo = tkinter.Label(window)
label_tipo.grid(row=11, column=0,pady=40,padx=20,sticky=("S"))
label_info = tkinter.Label(window)
label_info.grid(row=11, column=0,pady=15,padx=20, sticky=("S"))


window.mainloop ()