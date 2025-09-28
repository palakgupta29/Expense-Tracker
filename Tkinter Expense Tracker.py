import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Database
connector = sqlite3.connect('expenses.db')
cursor = connector.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)
""")
connector.commit()

# Functions
def display_records():
    tree.delete(*tree.get_children())
    for i, row in enumerate(cursor.execute("SELECT * FROM expenses")):
        tag = 'even' if i % 2 == 0 else 'odd'
        tree.insert('', END, values=row, tags=(tag,))
    update_pie_chart()

def clear_fields():
    amount.set('')
    category.set('')
    description.set('')
    date.set('')
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass

def add_record():
    if not amount.get() or not category.get() or not date.get():
        mb.showerror("Required Fields", "Amount, Category, and Date are required.")
        return
    cursor.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                   (amount.get(), category.get(), description.get(), date.get()))
    connector.commit()
    clear_fields()
    display_records()
    mb.showinfo("Success", "Expense added successfully!")

def remove_record():
    if not tree.selection():
        mb.showerror("Error", "Select a record to delete.")
        return
    current_item = tree.focus()
    values = tree.item(current_item)["values"]
    cursor.execute("DELETE FROM expenses WHERE id=?", (values[0],))
    connector.commit()
    display_records()
    mb.showinfo("Deleted", "Expense deleted successfully!")

def update_record():
    if not tree.selection():
        mb.showerror("Error", "Select a record to update.")
        return
    current_item = tree.focus()
    values = tree.item(current_item)["values"]
    new_amount = sd.askstring("Update Amount", f"Current: {values[1]}")
    new_category = sd.askstring("Update Category", f"Current: {values[2]}")
    new_description = sd.askstring("Update Description", f"Current: {values[3]}")
    new_date = sd.askstring("Update Date", f"Current: {values[4]}")
    cursor.execute("UPDATE expenses SET amount=?, category=?, description=?, date=? WHERE id=?",
                   (new_amount or values[1], new_category or values[2],
                    new_description or values[3], new_date or values[4], values[0]))
    connector.commit()
    display_records()
    mb.showinfo("Updated", "Expense updated successfully!")

def update_pie_chart():
    fig.clear()
    ax = fig.add_subplot(111)
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    if data:
        categories, amounts = zip(*data)
        ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
        ax.set_title("Spending by Category")
    canvas.draw()

# Hover effects
def on_enter(e):
    e.widget['background'] = '#ffda77'
def on_leave(e):
    e.widget['background'] = btn_bg

# UI Colors & Fonts
lf_bg = '#6c5ce7'
rtf_bg = '#55efc4'
rbf_bg = '#ffeaa7'
btn_bg = '#fab1a0'
lbl_font = ('Verdana', 11, 'bold')
entry_font = ('Calibri', 12)
btn_font = ('Verdana', 11, 'bold')

# Main Window
root = Tk()
root.title("💰 Expense Tracker")
root.geometry("1300x800")
root.config(bg="#dfe6e9")
root.resizable(False, False)

# Header
header = Label(root, text="💰 Expense Tracker", font=('Arial', 18, 'bold'), bg="#00b894", fg="white", pady=10)
header.pack(side=TOP, fill=X)

# Variables
amount = StringVar()
category = StringVar()
description = StringVar()
date = StringVar()

# Frames
left_frame = Frame(root, bg=lf_bg)
left_frame.place(x=0, y=50, relwidth=0.3, relheight=0.95)

RT_frame = Frame(root, bg=rtf_bg)
RT_frame.place(relx=0.3, y=50, relheight=0.15, relwidth=0.7)

RB_frame = Frame(root)
RB_frame.place(relx=0.3, rely=0.2, relheight=0.75, relwidth=0.7)

# Left Frame Widgets
Label(left_frame, text="Amount", bg=lf_bg, fg="white", font=lbl_font).place(x=70, y=20)
Entry(left_frame, textvariable=amount, font=entry_font, width=25).place(x=30, y=50)

Label(left_frame, text="Category", bg=lf_bg, fg="white", font=lbl_font).place(x=70, y=90)
Entry(left_frame, textvariable=category, font=entry_font, width=25).place(x=30, y=120)

Label(left_frame, text="Description", bg=lf_bg, fg="white", font=lbl_font).place(x=70, y=160)
Entry(left_frame, textvariable=description, font=entry_font, width=25).place(x=30, y=190)

Label(left_frame, text="Date (YYYY-MM-DD)", bg=lf_bg, fg="white", font=lbl_font).place(x=40, y=230)
Entry(left_frame, textvariable=date, font=entry_font, width=25).place(x=30, y=260)

btn_add = Button(left_frame, text="➕ Add Record", bg=btn_bg, font=btn_font, width=20, command=add_record)
btn_add.place(x=40, y=320)
btn_clear = Button(left_frame, text="🧹 Clear Fields", bg=btn_bg, font=btn_font, width=20, command=clear_fields)
btn_clear.place(x=40, y=370)

for b in [btn_add, btn_clear]:
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)

# Right Top Frame Buttons
btn_delete = Button(RT_frame, text="❌ Delete Record", bg=btn_bg, font=btn_font, width=15, command=remove_record)
btn_update = Button(RT_frame, text="✏️ Update Record", bg=btn_bg, font=btn_font, width=15, command=update_record)
btn_delete.place(x=20, y=20)
btn_update.place(x=200, y=20)

for b in [btn_delete, btn_update]:
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)

# Right Bottom Frame Table
Label(RB_frame, text="📜 Expense Records", bg=rbf_bg, font=('Arial', 14, 'bold')).pack(side=TOP, fill=X)
tree = ttk.Treeview(RB_frame, columns=('ID', 'Amount', 'Category', 'Description', 'Date'), show='headings')
tree.heading('ID', text='ID')
tree.heading('Amount', text='Amount')
tree.heading('Category', text='Category')
tree.heading('Description', text='Description')
tree.heading('Date', text='Date')
tree.column('ID', width=30)
tree.tag_configure('even', background='#f1f2f6')
tree.tag_configure('odd', background='#dfe4ea')
tree.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = Scrollbar(RB_frame, orient=VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)

# Pie Chart
fig = Figure(figsize=(3.5, 3), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=left_frame)
canvas.get_tk_widget().place(x=10, y=420)

# Load Data
display_records()

root.mainloop()
