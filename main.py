import tkinter as tk  # Tkinter kütüphanesini içe aktararak GUI uygulamaları geliştirmek için gerekli olan bileşenleri kullanabilmemizi sağlar.
from tkinter import ttk  # ttk modülünü içe aktararak daha gelişmiş ve modern görünümlü widget'lar (arayüz bileşenleri) kullanmamıza olanak tanır.

# Ana pencereyi oluştur
root = tk.Tk()  # Tkinter uygulamasının ana penceresini oluşturur.
root.title("MIPS IDE - Python")  # Pencerenin başlığını "MIPS IDE - Python" olarak ayarlar.
root.geometry("1200x700")  # Pencerenin boyutunu 1200x700 piksel olarak ayarlar.

# Sol üstteki düzenleme penceresi için bir Frame oluştur
edit_frame = tk.Frame(root, relief='solid', borderwidth=1)  # Ana pencerede bir çerçeve (Frame) oluşturur; kenarlarında 1 piksel kalınlığında bir sınır vardır.
edit_frame.place(x=0, y=0, width=900, height=450)  # Frame'in konumunu (x=0, y=0) ve boyutunu (900x450) ayarlar.

# Satır numaraları için bir Text widget oluştur
line_numbers = tk.Text(edit_frame, width=4, padx=3, takefocus=0, border=0,
                       background='lightgray', state='disabled')  # Satır numaralarını gösterecek bir Text widget oluşturur.
# - width=4: Genişliğini 4 karakterle sınırlar.
# - padx=3: İçerideki yazı ile kenar arasına 3 piksel boşluk ekler.
# - takefocus=0: Kullanıcı bu alanı seçtiğinde, diğer widget'lara geçiş yapabilir.
# - border=0: Kenar çerçevesini kaldırır.
# - background='lightgray': Arka plan rengini açık gri yapar.
# - state='disabled': Başlangıçta bu alan yazılabilir durumda değildir.

line_numbers.pack(side='left', fill='y')  # Satır numaraları widget'ını sol tarafa yerleştirir ve dikey olarak doldurur.

# Kaydırma çubuğu için bir Scrollbar oluştur
scrollbar = tk.Scrollbar(edit_frame, command=lambda *args: (edit_text.yview(*args), line_numbers.yview(*args)))  
# - command parametresi: Kaydırma çubuğunun hareket ettiğinde ne olacağını belirler. edit_text ve line_numbers'ı aynı anda kaydıracak şekilde ayarlanmıştır.
scrollbar.pack(side='right', fill='y')  # Scrollbar'ı sağ tarafa yerleştirir ve dikey olarak doldurur.

# Düzenleme penceresi için bir Text widget oluştur
edit_text = tk.Text(edit_frame, wrap='none', yscrollcommand=scrollbar.set)  
# - wrap='none': Satır kaydırma olmadan metni aynı satırda tutar.
# - yscrollcommand=scrollbar.set: Kaydırma çubuğu ile bağlantılı olarak yukarı ve aşağı kaydırma yapmasını sağlar.
edit_text.pack(side='right', fill='both', expand=True)  # Text widget'ını sağ tarafa yerleştirir ve hem yatay hem de dikey olarak genişler.

# Düzenleme penceresindeki satır numaralarını güncelleme fonksiyonu
def update_line_numbers(event=None):  # Herhangi bir olay gerçekleştiğinde satır numaralarını güncellemek için fonksiyon tanımlanır.
    lines = edit_text.get('1.0', 'end-1c').split('\n')  # Tüm metni alır, son satır karakterini hariç tutarak ayırır.
    line_numbers.config(state='normal')  # Satır numarası alanını normal (yazılabilir) moda geçirir.
    line_numbers.delete('1.0', 'end')  # Eski satır numaralarını siler.
    line_numbers.insert('1.0', "\n".join(str(i + 1) for i in range(len(lines))))  
    # Yeni satır numaralarını oluşturur ve ekler. Örneğin, 1, 2, 3 şeklinde.
    line_numbers.config(state='disabled')  # Satır numarası alanını tekrar pasif (yazılamaz) yapar.
    line_numbers.yview_moveto(edit_text.yview()[0])  # Satır numarası alanının kaydırmasını, metin alanıyla senkronize eder.

edit_text.bind('<KeyRelease>', update_line_numbers)  # Klavyeden tuş bırakıldığında update_line_numbers fonksiyonunu çağır.

# Fare tekerleği ile kaydırma olayı
def on_mouse_wheel(event):  # Fare tekerleği olayı için bir fonksiyon tanımlanır.
    edit_text.yview_scroll(-1 * (event.delta // 120), "units")  # Text widget'ını yukarı veya aşağı kaydırır.
    line_numbers.yview_scroll(-1 * (event.delta // 120), "units")  # Satır numaralarını da aynı miktarda kaydırır.
    return "break"  # Olayın daha fazla işlenmesini engeller.

edit_text.bind("<MouseWheel>", on_mouse_wheel)  # Fare tekerleği olayı edit_text widget'ına bağlanır.

# Register tablosu için sağdaki Frame oluştur
register_frame = tk.Frame(root, relief='solid', borderwidth=1)  
register_frame.place(x=900, y=0, width=300, height=700)  # Frame'in konumunu (x=900, y=0) ve boyutunu (300x700) ayarlar.

# Register tablosu (Treeview) oluştur
columns = ("Name", "Number", "Value")  # Treeview için başlıkları tanımla.
tree = ttk.Treeview(register_frame, columns=columns, show='headings')  
# Treeview widget'ını oluştur, başlıklar görünür olacak şekilde ayarlanır.

# Sütun başlıklarını ve genişliklerini ayarla
for col in columns:  # Her bir sütun için döngü başlatılır.
    tree.heading(col, text=col)  # Sütun başlığını ayarlama.
    tree.column(col, width=80, anchor='center')  # Sütun genişliğini 80 piksel olarak ayarla ve içerikleri ortala.

# Register verilerini tanımla
register = [  
    {"name": "$zero", "number": 0, "value": "0x00000000"},  # Her register için bir sözlük tanımlanır; ismi, numarası ve değeri içerir.
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

# Register verilerini Treeview'a ekle
for reg in register:  # Her bir register için döngü başlatılır.
    tree.insert("", "end", values=(reg["name"], reg["number"], reg["value"]))  
    # Treeview'a yeni bir satır ekler, her bir register'ın adı, numarası ve değeri ile.

tree.pack(fill='both', expand=True)  # Treeview'i doldurur ve genişletir.

# Alt kısımdaki mesaj ve konsol penceresi için bir Frame oluştur
console_frame = tk.Frame(root, relief='solid', borderwidth=1)  
console_frame.place(x=0, y=450, width=900, height=250)  # Frame'in konumunu (x=0, y=450) ve boyutunu (900x250) ayarlar.

# Konsol çıktısı için bir Text widget oluştur
console_output = tk.Text(console_frame, height=8, bg='white', fg='white')  
# - height=8: Konsolun yüksekliğini 8 satır olarak ayarlar.
# - bg='white': Arka plan rengini beyaz yapar.
# - fg='white': Yazı rengini beyaz yapar (görünmez, bu yüzden düzenlenmeli).
console_output.pack(fill='both', expand=True)  # Konsol widget'ını doldurur ve genişletir.

# Clear butonunu oluştur
clear_button = tk.Button(console_frame, text="Clear", command=lambda: console_output.delete('1.0', 'end'))  
# - text="Clear": Buton üzerinde görünen metni "Clear" olarak ayarlar.
# - command=lambda: console_output.delete('1.0', 'end'): Butona basıldığında konsoldaki tüm metni siler.
clear_button.pack(side='left')  # Clear butonunu sola yerleştirir.

# Uygulama döngüsünü başlat
root.mainloop()  # Tkinter uygulamasının döngüsünü başlatır; bu sayede uygulama açık kalır ve kullanıcı etkileşimlerine yanıt verir.