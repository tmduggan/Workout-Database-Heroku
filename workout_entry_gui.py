import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime

# Replace with your Heroku database URL
DATABASE_URL = "postgres://udpnsji7h49vfe:p20aa2e954b559862de4011f375c341d4c78d45fff7238501261a544661e7153f@cf980tnnkgv1bp.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d45o393jceliua"

# Function to fetch workout names from the database
def fetch_workout_names():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT workout_name FROM workout_data ORDER BY workout_name;")
        workout_names = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return workout_names
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not fetch workout names: {e}")
        return []

# Function to handle "Add New" workout name
def handle_add_new(event):
    if workout_dropdown.get() == "Add New":
        new_workout_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        new_workout_entry.grid(row=1, column=1, padx=10, pady=5)
    else:
        new_workout_label.grid_forget()
        new_workout_entry.grid_forget()

# Function to add a row to the table
def add_row():
    workout_name = workout_dropdown.get()
    if workout_name == "Add New":
        workout_name = new_workout_entry.get().strip().title()

    weight = weight_entry.get().strip()
    reps = reps_entry.get().strip()
    workout_date = date_entry.get().strip()

    if not workout_name or not workout_date:
        messagebox.showwarning("Input Error", "Workout name and date are required.")
        return

    try:
        datetime.strptime(workout_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showwarning("Input Error", "Date must be in YYYY-MM-DD format.")
        return

    table.insert("", "end", values=(workout_name, weight, reps, workout_date))
    workout_dropdown.set("")
    weight_entry.delete(0, tk.END)
    reps_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    new_workout_entry.delete(0, tk.END)

# Function to submit data to the database
def submit_data():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        cur = conn.cursor()
        for child in table.get_children():
            values = table.item(child)["values"]
            workout_name = values[0]
            weight = float(values[1]) if values[1] else None
            reps = int(values[2]) if values[2] else None
            workout_date = datetime.strptime(values[3], "%Y-%m-%d").date()
            one_rm = weight * (1 + 0.0333 * reps) if weight and reps else None
            cur.execute("""
                INSERT INTO workout_data (workout_name, weight, reps, workout_date, one_rm)
                VALUES (%s, %s, %s, %s, %s)
            """, (workout_name, weight, reps, workout_date, one_rm))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("Success", "Data successfully submitted to the database!")
        for child in table.get_children():
            table.delete(child)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Main window
root = tk.Tk()
root.title("Workout Data Entry")

# Fetch workout names
WORKOUTS = fetch_workout_names() + ["Add New"]

# Workout dropdown
tk.Label(root, text="Workout Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
workout_dropdown = ttk.Combobox(root, values=WORKOUTS, state="readonly")
workout_dropdown.grid(row=0, column=1, padx=10, pady=5)
workout_dropdown.bind("<<ComboboxSelected>>", handle_add_new)

# New workout entry (hidden by default)
new_workout_label = tk.Label(root, text="New Workout Name:")
new_workout_entry = tk.Entry(root)

# Weight entry
tk.Label(root, text="Weight (lbs):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
weight_entry = tk.Entry(root)
weight_entry.grid(row=2, column=1, padx=10, pady=5)

# Reps entry
tk.Label(root, text="Reps:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
reps_entry = tk.Entry(root)
reps_entry.grid(row=3, column=1, padx=10, pady=5)

# Date entry
tk.Label(root, text="Date (YYYY-MM-DD):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
date_entry = tk.Entry(root)
date_entry.grid(row=4, column=1, padx=10, pady=5)

# Add row button
add_row_button = tk.Button(root, text="Add Row", command=add_row)
add_row_button.grid(row=5, column=0, columnspan=2, pady=10)

# Treeview table
table = ttk.Treeview(root, columns=("Workout", "Weight", "Reps", "Date"), show="headings", height=10)
table.heading("Workout", text="Workout")
table.heading("Weight", text="Weight (lbs)")
table.heading("Reps", text="Reps")
table.heading("Date", text="Date")
table.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Add default row
table.insert("", "end", values=("", "", "", ""))

# Submit button
submit_button = tk.Button(root, text="Submit to Database", command=submit_data)
submit_button.grid(row=7, column=0, columnspan=2, pady=10)

# Main loop
root.mainloop()
