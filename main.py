import tkinter as tk
from tkinter import ttk
from register_data import register


class MIPSIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("MIPS IDE - Python")
        self.root.geometry("1200x700")
        
        self.data_section = {}  # .data bölümündeki değişkenleri saklamak için sözlük
        
        self.create_widgets()  # Arayüz bileşenlerini oluştur

    def create_widgets(self):
        # Sol üstteki düzenleme penceresi için bir Frame
        self.edit_frame = tk.Frame(self.root, relief='solid', borderwidth=1)
        self.edit_frame.place(x=0, y=0, width=900, height=450)

        # Satır numaraları
        self.line_numbers = tk.Text(self.edit_frame, width=4, padx=3, takefocus=0, border=0,
                                     background='lightgray', state='disabled')
        self.line_numbers.pack(side='left', fill='y')

        # Kaydırma çubuğu
        self.scrollbar = tk.Scrollbar(self.edit_frame, command=lambda *args: (self.edit_text.yview(*args), self.line_numbers.yview(*args)))
        self.scrollbar.pack(side='right', fill='y')

        # Düzenleme penceresi
        self.edit_text = tk.Text(self.edit_frame, wrap='none', yscrollcommand=self.scrollbar.set)
        self.edit_text.pack(side='right', fill='both', expand=True)

        # Düzenleme penceresindeki satır numaralarını güncelleme fonksiyonu
        self.edit_text.bind('<KeyRelease>', self.update_line_numbers)
        self.edit_text.bind("<MouseWheel>", self.on_mouse_wheel)

        # Register tablosu için sağdaki Frame
        self.register_frame = tk.Frame(self.root, relief='solid', borderwidth=1)
        self.register_frame.place(x=900, y=0, width=300, height=700)

        # Register tablosu (Treeview)
        self.columns = ("Name", "Number", "Value")
        self.tree = ttk.Treeview(self.register_frame, columns=self.columns, show='headings')

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor='center')

        # Alternatif renklendirme için stil tanımları
        self.tree.tag_configure('evenrow', background='lightgray')  # Çift satırlar için
        self.tree.tag_configure('oddrow', background='white')  # Tek satırlar için

        # Verilerin eklenmesi
        for index, reg in enumerate(register):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'  # Çift/Tek satır kontrolü
            self.tree.insert("", "end", values=(reg["name"], reg["number"], reg["value"]), tags=(tag,))

        self.tree.pack(fill='both', expand=True)

        # Alt kısımdaki mesaj ve konsol penceresi
        self.console_frame = tk.Frame(self.root, relief='solid', borderwidth=1)
        self.console_frame.place(x=0, y=450, width=900, height=250)

        self.console_output = tk.Text(self.console_frame, height=8, bg='black', fg='white')
        self.console_output.pack(fill='both', expand=True)

        clear_button = tk.Button(self.console_frame, text="Clear", command=lambda: self.console_output.delete('1.0', 'end'))
        clear_button.pack(side='left')

        # Konsol çerçevesine 'Run' butonu ekle
        run_button = tk.Button(self.console_frame, text="Run", command=self.read_mips_code)
        run_button.pack(side='left')

    def update_line_numbers(self, event=None):
        lines = self.edit_text.get('1.0', 'end-1c').split('\n')
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', "\n".join(str(i + 1) for i in range(len(lines))))
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.edit_text.yview()[0])

    def on_mouse_wheel(self, event):
        self.edit_text.yview_scroll(-1 * (event.delta // 120), "units")
        self.line_numbers.yview_scroll(-1 * (event.delta // 120), "units")
        return "break"

    def get_register_value(self, register_name):
        """Register'ın hexadecimal value değerini döndürür."""
        for item in self.tree.get_children():
            name = self.tree.item(item, 'values')[0]
            if name == register_name:
                return int(self.tree.item(item, 'values')[2], 16)  # Hex değeri integer olarak döndür

    def update_register_value(self, register_name, new_value):
        """Register tablosunda verilen register'ın value değerini günceller."""
        for item in self.tree.get_children():
            name = self.tree.item(item, 'values')[0]
            if name == register_name:
                hex_value = f"0x{new_value:08X}"  # Yeni değer hexadecimal formatta
                self.tree.set(item, column="Value", value=hex_value)

    def to_hex(self, value):
        """Verilen değeri hexadecimal formata dönüştürür."""
        return f"0x{int(value):08X}"

    def execute_add_command(self, dest, src1, src2):
        """ADD komutunu işler ve sonucu hedef register'a yazar."""
        val1 = self.get_register_value(src1)  # Kaynak 1'in değeri
        val2 = self.get_register_value(src2)  # Kaynak 2'nin değeri
        result = val1 + val2  # Değerleri topla
        self.update_register_value(dest, result)  # Sonucu hedef register'a yaz

    def execute_sub_command(self, dest, src1, src2):
        """SUB komutunu işler ve sonucu hedef register'a yazar."""
        val1 = self.get_register_value(src1)  # Kaynak 1'in değeri
        val2 = self.get_register_value(src2)  # Kaynak 2'nin değeri
        result = val1 - val2  # Çıkarma işlemi
        self.update_register_value(dest, result)  # Sonucu hedef register'a yaz

    def execute_div_command(self, dest, src1, src2):
        """DIV komutunu işler ve sonucu hedef register'a yazar."""
        val1 = self.get_register_value(src1)  # Kaynak 1'in değeri
        val2 = self.get_register_value(src2)  # Kaynak 2'nin değeri
        if val2 != 0:  # Sıfıra bölmeyi kontrol et
            result = val1 // val2  # Bölme işlemi
            self.update_register_value(dest, result)  # Sonucu hedef register'a yaz
        else:
            self.console_output.insert('end', "Error: Division by zero!\n")

    def execute_mul_command(self, dest, src1, src2):
        """MUL komutunu işler ve sonucu hedef register'a yazar."""
        val1 = self.get_register_value(src1)  # Kaynak 1'in değeri
        val2 = self.get_register_value(src2)  # Kaynak 2'nin değeri
        result = val1 * val2  # Çarpma işlemi
        self.update_register_value(dest, result)  # Sonucu hedef register'a yaz

    def read_mips_code(self):
        self.console_output.delete('1.0', 'end')  # Önceki konsol çıktısını temizler
        code = self.edit_text.get('1.0', 'end-1c')  # Düzenleme alanındaki tüm kodu al
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
                var_value = self.to_hex(parts[-1])  # Değeri hexadecimal'e çevir
                self.data_section[var_name] = var_value  # Değişkeni sözlüğe kaydet

        self.console_output.insert('end', f"Data Section: {self.data_section}\n")

        # Main içindeki komutları işleme
        in_main = False
        for line in lines:
            if line.startswith("main:"):
                in_main = True
                continue
            if in_main:
                parts = [part.strip() for part in line.replace(",", " ").split()]
                if parts[0] == "add":  # ADD komutunu bulduk
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    self.execute_add_command(dest, src1, src2)
                elif parts[0] == "sub":  # SUB komutunu bulduk
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    self.execute_sub_command(dest, src1, src2)
                elif parts[0] == "div":  # DIV komutunu bulduk
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    self.execute_div_command(dest, src1, src2)
                elif parts[0] == "mul":  # MUL komutunu bulduk
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    self.execute_mul_command(dest, src1, src2)
                elif parts[0] == "lw":  # LW komutunu bulduk
                    register, var_name = parts[1], parts[2]
                    if var_name in self.data_section:
                        self.update_register_value(register, int(self.data_section[var_name], 16))

        self.console_output.insert('end', f"Registers Updated.\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = MIPSIDE(root)
    root.mainloop()
