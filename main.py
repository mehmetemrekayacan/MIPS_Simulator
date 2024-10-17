import tkinter as tk
from tkinter import ttk

# Ana pencere
root = tk.Tk()
root.title("MIPS IDE - Python")
root.geometry("1200x700")

# Sol üstteki düzenleme penceresi için bir Frame
edit_frame = tk.Frame(root, relief='solid', borderwidth=1)
edit_frame.place(x=0, y=0, width=900, height=450)

# Satır numaraları
line_numbers = tk.Text(edit_frame, width=4, padx=3, takefocus=0, border=0,
                       background='lightgray', state='disabled')
line_numbers.pack(side='left', fill='y')

# Kaydırma çubuğu
scrollbar = tk.Scrollbar(edit_frame, command=lambda *args: (edit_text.yview(*args), line_numbers.yview(*args)))
scrollbar.pack(side='right', fill='y')

# Düzenleme penceresi 
edit_text = tk.Text(edit_frame, wrap='none', yscrollcommand=scrollbar.set)
edit_text.pack(side='right', fill='both', expand=True)

# Düzenleme penceresindeki satır numaralarını güncelleme fonksiyonu
def update_line_numbers(event=None):
    lines = edit_text.get('1.0', 'end-1c').split('\n')
    line_numbers.config(state='normal')
    line_numbers.delete('1.0', 'end')
    line_numbers.insert('1.0', "\n".join(str(i + 1) for i in range(len(lines))))
    line_numbers.config(state='disabled')
    line_numbers.yview_moveto(edit_text.yview()[0])

edit_text.bind('<KeyRelease>', update_line_numbers)

# Fare tekerleği ile kaydırma olayı
def on_mouse_wheel(event):
    edit_text.yview_scroll(-1 * (event.delta // 120), "units")
    line_numbers.yview_scroll(-1 * (event.delta // 120), "units")
    return "break"

edit_text.bind("<MouseWheel>", on_mouse_wheel)

# Register tablosu için sağdaki Frame
register_frame = tk.Frame(root, relief='solid', borderwidth=1)
register_frame.place(x=900, y=0, width=300, height=700)

# Register tablosu (Treeview)
columns = ("Name", "Number", "Value")
tree = ttk.Treeview(register_frame, columns=columns, show='headings')

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=80, anchor='center')

# Alternatif renklendirme için stil tanımları
tree.tag_configure('evenrow', background='lightgray')  # Çift satırlar için
tree.tag_configure('oddrow', background='white') # Tek satırlar için    

# Verilerin eklenmesi
register = [
    {"name": "$zero", "number": 0, "value": "0x00000000"},
    {"name": "$at", "number": 1, "value": "0x00000000"},
    {"name": "$v0", "number": 2, "value": "0x00000000"},
    {"name": "$v1", "number": 3, "value": "0x00000000"},
    {"name": "$a0", "number": 4, "value": "0x00000000"},
    {"name": "$a1", "number": 5, "value": "0x00000000"},
    {"name": "$a2", "number": 6, "value": "0x00000000"},
    {"name": "$a3", "number": 7, "value": "0x00000000"},
    {"name": "$t0", "number": 8, "value": "0x00000000"},
    {"name": "$t1", "number": 9, "value": "0x00000000"},
    {"name": "$t2", "number": 10, "value": "0x00000000"},
    {"name": "$t3", "number": 11, "value": "0x00000000"},
    {"name": "$t4", "number": 12, "value": "0x00000000"},
    {"name": "$t5", "number": 13, "value": "0x00000000"},
    {"name": "$t6", "number": 14, "value": "0x00000000"},
    {"name": "$t7", "number": 15, "value": "0x00000000"},
    {"name": "$s0", "number": 16, "value": "0x00000000"},
    {"name": "$s1", "number": 17, "value": "0x00000000"},
    {"name": "$s2", "number": 18, "value": "0x00000000"},
    {"name": "$s3", "number": 19, "value": "0x00000000"},
    {"name": "$s4", "number": 20, "value": "0x00000000"},
    {"name": "$s5", "number": 21, "value": "0x00000000"},
    {"name": "$s6", "number": 22, "value": "0x00000000"},
    {"name": "$s7", "number": 23, "value": "0x00000000"},
    {"name": "$t8", "number": 24, "value": "0x00000000"},
    {"name": "$t9", "number": 25, "value": "0x00000000"},
    {"name": "$k0", "number": 26, "value": "0x00000000"},
    {"name": "$k1", "number": 27, "value": "0x00000000"},
    {"name": "$gp", "number": 28, "value": "0x00000000"},
    {"name": "$sp", "number": 29, "value": "0x00000000"},
    {"name": "$fp", "number": 30, "value": "0x00000000"},
    {"name": "$ra", "number": 31, "value": "0x00000000"},
]

for index, reg in enumerate(register):
    tag = 'evenrow' if index % 2 == 0 else 'oddrow'  # Çift/Tek satır kontrolü
    tree.insert("", "end", values=(reg["name"], reg["number"], reg["value"]), tags=(tag,))

tree.pack(fill='both', expand=True)

# Alt kısımdaki mesaj ve konsol penceresi
console_frame = tk.Frame(root, relief='solid', borderwidth=1)
console_frame.place(x=0, y=450, width=900, height=250)

console_output = tk.Text(console_frame, height=8, bg='black', fg='white')
console_output.pack(fill='both', expand=True)

clear_button = tk.Button(console_frame, text="Clear", command=lambda: console_output.delete('1.0', 'end'))
clear_button.pack(side='left')

# .data bölümündeki değişkenleri saklamak için sözlük
data_section = {}

# Register tablosunu güncelleme fonksiyonu
def update_register_value(register_name, new_value):
    for item in tree.get_children():
        name = tree.item(item, 'values')[0]
        if name == register_name:
            tree.set(item, column="Value", value=new_value)

# MIPS kodunu parçalayan ve işleyen fonksiyon
def read_mips_code():
    console_output.delete('1.0', 'end')  # Önceki konsol çıktısını temizler
    code = edit_text.get('1.0', 'end-1c')  # Düzenleme alanındaki tüm kodu al
    lines = [line.strip() for line in code.split('\n') if line.strip()]  # Satırları temizle

    # .data bölümündeki değişkenleri toplama
    in_data_section = False
    for line in lines:
        if line == ".data":
            in_data_section = True
            continue
        elif line == ".text":
            in_data_section = False
            break
        if in_data_section:
            parts = line.replace(",", " ").split()
            var_name = parts[0].replace(":", "")
            var_value = parts[-1]
            data_section[var_name] = var_value  # Değişkeni sözlüğe kaydet

    console_output.insert('end', f"Data Section: {data_section}\n")

    # Main içindeki değişkenleri bulup register değerlerini güncelleme
    in_main = False
    for line in lines:
        if line.startswith("main:"):
            in_main = True
            continue
        if in_main and line.startswith("li"):  # li komutunu es geçiyoruz
            continue
        if in_main:
            parts = [part.strip() for part in line.replace(",", " ").split()]
            for part in parts:
                if part in data_section:  # Değişken ismi bulundu
                    register = parts[1]  # Örneğin lw $t0, num1 -> parts[1] = $t0
                    new_value = data_section[part]  # Değişkenin değeri
                    update_register_value(register, new_value)  # Register'ı güncelle

    console_output.insert('end', f"Registers Updated.\n")

# Konsol çerçevesine 'Run' butonu ekle
run_button = tk.Button(console_frame, text="Run", command=read_mips_code)
run_button.pack(side='left')




root.mainloop()