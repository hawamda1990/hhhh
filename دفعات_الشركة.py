
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, timedelta
import os

# تحميل بيانات الدفعات
data_path = "payments_data.json"
if not os.path.exists(data_path):
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

with open(data_path, "r", encoding="utf-8") as f:
    payments = json.load(f)

# تحويل التواريخ
for p in payments:
    p["تاريخ_الدفع"] = datetime.strptime(p["تاريخ_الدفع"], "%Y-%m-%d")

def save_data():
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump([
            {**p, "تاريخ_الدفع": p["تاريخ_الدفع"].strftime("%Y-%m-%d")} for p in payments
        ], f, ensure_ascii=False, indent=2)

def mark_as_paid(index):
    payment = payments[index]
    payment["تم_الدفع"] = True
    new_date = payment["تاريخ_الدفع"] + timedelta(days=30)
    payments.append({
        "الاسم": payment["الاسم"],
        "تاريخ_الدفع": new_date,
        "قيمة_الدفع": payment["قيمة_الدفع"],
        "لصالح": payment["لصالح"],
        "تم_الدفع": False
    })
    save_data()
    refresh_table()

def refresh_table():
    for widget in frame.winfo_children():
        widget.destroy()

    columns = ["الاسم", "تاريخ_الدفع", "قيمة_الدفع", "لصالح", "تم_الدفع", "إجراء"]
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    for col in columns[:-1]:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.heading("إجراء", text="")

    for i, row in enumerate(payments):
        tree.insert("", "end", iid=str(i), values=[
            row["الاسم"],
            row["تاريخ_الدفع"].strftime("%Y-%m-%d"),
            row["قيمة_الدفع"],
            row["لصالح"],
            "✔" if row["تم_الدفع"] else "✘",
            "تم الدفع" if not row["تم_الدفع"] else ""
        ])
    tree.pack(fill="both", expand=True)

    def on_click(event):
        item = tree.identify_row(event.y)
        if not item:
            return
        col = tree.identify_column(event.x)
        if col == "#6":  # عمود الإجراء
            index = int(item)
            if not payments[index]["تم_الدفع"]:
                mark_as_paid(index)

    tree.bind("<Button-1>", on_click)

def add_payment():
    def save():
        try:
            name = name_var.get()
            date = datetime.strptime(date_var.get(), "%Y-%m-%d")
            amount = float(amount_var.get())
            target = target_var.get()
            payments.append({
                "الاسم": name,
                "تاريخ_الدفع": date,
                "قيمة_الدفع": amount,
                "لصالح": target,
                "تم_الدفع": False
            })
            save_data()
            top.destroy()
            refresh_table()
        except Exception as e:
            messagebox.showerror("خطأ", f"تأكد من صحة البيانات: {e}")

    top = tk.Toplevel(root)
    top.title("إضافة دفعة جديدة")

    tk.Label(top, text="الاسم:").grid(row=0, column=0)
    tk.Label(top, text="تاريخ الدفعة (YYYY-MM-DD):").grid(row=1, column=0)
    tk.Label(top, text="قيمة الدفعة:").grid(row=2, column=0)
    tk.Label(top, text="لصالح:").grid(row=3, column=0)

    name_var = tk.StringVar()
    date_var = tk.StringVar()
    amount_var = tk.StringVar()
    target_var = tk.StringVar()

    tk.Entry(top, textvariable=name_var).grid(row=0, column=1)
    tk.Entry(top, textvariable=date_var).grid(row=1, column=1)
    tk.Entry(top, textvariable=amount_var).grid(row=2, column=1)
    tk.Entry(top, textvariable=target_var).grid(row=3, column=1)

    tk.Button(top, text="حفظ", command=save).grid(row=4, column=0, columnspan=2)

root = tk.Tk()
root.title("دفعات الشركة - مجموعة الحوامدة القانونية")
root.geometry("900x500")

menubar = tk.Menu(root)
menubar.add_command(label="إضافة دفعة", command=add_payment)
root.config(menu=menubar)

frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

refresh_table()

root.mainloop()
