import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from app.task_model import Task
from app.database import get_session
from app.config import load_config

# Cargar configuración
config = load_config()
db_path = os.environ.get("DATABASE_PATH", "data/tasks.db")
export_folder = os.environ.get("EXPORT_FOLDER", "export")

# Crear sesión de base de datos
session = get_session(db_path)

TITLE_REQUIRED_MSG = "El título de la tarea es obligatorio."

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager App")
        self.root.configure(bg='black')  # Fondo negro para la ventana
        self.session = session
        self.setup_ui()  # Asegúrate de que esta línea esté aquí

    def setup_ui(self):
        # Configurar el fondo negro para todos los widgets
        header_frame = tk.Frame(self.root, bg='black')
        header_frame.pack()

        tk.Label(header_frame, text="Descripción", width=50, borderwidth=2, relief="groove", bg='black', fg='white').grid(row=0, column=0)
        tk.Label(header_frame, text="Estado", width=50, borderwidth=2, relief="groove", bg='black', fg='white').grid(row=0, column=1)

        self.task_frame = tk.Frame(self.root, bg='black')
        self.task_frame.pack()

        self.description_listbox = tk.Listbox(self.task_frame, width=50, height=20, bg='black', fg='white', selectbackground='gray')
        self.description_listbox.grid(row=1, column=0)
        self.description_listbox.bind("<Double-1>", self.show_task_description)

        self.status_listbox = tk.Listbox(self.task_frame, width=50, height=20, bg='black', fg='white', selectbackground='gray')
        self.status_listbox.grid(row=1, column=1)

        # Botones con colores personalizados
        self.add_task_button = tk.Button(self.root, text="Agregar Tarea", command=self.add_task, bg='black', fg='white', activebackground='gray')
        self.add_task_button.pack()

        self.complete_task_button = tk.Button(self.root, text="Marcar como Completada", command=self.complete_task, bg='black', fg='white', activebackground='gray')
        self.complete_task_button.pack()

        self.delete_task_button = tk.Button(self.root, text="Eliminar Tarea", command=self.delete_task, bg='black', fg='white', activebackground='gray')
        self.delete_task_button.pack()

        self.export_button = tk.Button(self.root, text="Exportar Tareas", command=self.export_tasks, bg='black', fg='white', activebackground='gray')
        self.export_button.pack()

        self.import_button = tk.Button(self.root, text="Importar Tareas", command=self.import_tasks, bg='black', fg='white', activebackground='gray')
        self.import_button.pack()

        self.task_ids = []
        self.load_tasks()  # Asegúrate de que esto esté cargando las tareas correctamente

    def load_tasks(self):
        self.description_listbox.delete(0, tk.END)
        self.status_listbox.delete(0, tk.END)
        self.task_ids.clear()

        tasks = self.session.query(Task).all()
        for task in tasks:
            status = "Completada" if task.completed else "Pendiente"
            self.description_listbox.insert(tk.END, task.description or "Sin descripción")
            self.status_listbox.insert(tk.END, status)
            self.task_ids.append(task.id)

    def add_task(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Agregar Tarea")
        add_window.configure(bg='black')  # Fondo negro para la ventana de agregar tarea

        title_label = tk.Label(add_window, text="Título de la tarea", bg='black', fg='white')
        title_label.pack()

        title_entry = tk.Entry(add_window, bg='black', fg='white', insertbackground='white')
        title_entry.pack()

        description_label = tk.Label(add_window, text="Descripción de la tarea", bg='black', fg='white')
        description_label.pack()

        description_entry = tk.Entry(add_window, bg='black', fg='white', insertbackground='white')
        description_entry.pack()

        add_button = tk.Button(add_window, text="Agregar", command=lambda: self.save_task(title_entry.get(), description_entry.get(), add_window), bg='black', fg='white', activebackground='gray')
        add_button.pack()

    def save_task(self, title, description, window):
        if not title.strip():
            messagebox.showerror("Error", TITLE_REQUIRED_MSG)
            return
        new_task = Task(title=title.strip(), description=description.strip())
        self.session.add(new_task)
        self.session.commit()
        window.destroy()
        self.load_tasks()

    def complete_task(self):
        selected_task = self.get_selected_task()
        if selected_task:
            selected_task.completed = True
            self.session.commit()
            self.load_tasks()

    def delete_task(self):
        selected_task = self.get_selected_task()
        if selected_task:
            response = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar esta tarea?")
            if response:
                self.session.delete(selected_task)
                self.session.commit()
                self.load_tasks()

    def export_tasks(self):
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            tasks = self.session.query(Task).all()
            data = [{"id": t.id, "title": t.title, "description": t.description, "completed": t.completed} for t in tasks]
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
                messagebox.showinfo("Éxito", "Tareas exportadas con éxito.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {e}")

    def import_tasks(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    for task_data in data:
                        new_task = Task(
                            id=task_data.get("id"),
                            title=task_data.get("title", "Sin título"),
                            description=task_data.get("description", ""),
                            completed=task_data.get("completed", False)
                        )
                        self.session.merge(new_task)
                    self.session.commit()
                    self.load_tasks()
                    messagebox.showinfo("Éxito", "Tareas importadas con éxito.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al importar archivo JSON: {e}")

    def show_task_description(self, event):
        selected_task = self.get_selected_task()
        if selected_task:
            description_window = tk.Toplevel(self.root)
            description_window.title("Descripción de la Tarea")
            description_window.configure(bg='black')  # Fondo negro para la ventana de descripción
            description_label = tk.Label(description_window, text=selected_task.description or "Sin descripción", bg='black', fg='white', wraplength=300)
            description_label.pack()

    def get_selected_task(self):
        try:
            index = self.description_listbox.curselection()[0]
            task_id = self.task_ids[index]
            selected_task = self.session.query(Task).filter(Task.id == task_id).first()
            return selected_task
        except IndexError:
            messagebox.showerror("Error", "Por favor, selecciona una tarea.")
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
