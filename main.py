import tkinter as tk
from tkinter import ttk
from register_data import register
from mips_commands import MIPSCommands

class MIPSIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("MIPS IDE - Python")
        self.root.geometry("1200x700")

        self.data_section = {}  # .data bölümündeki değişkenleri saklamak için sözlük
        self.current_line = 0  # Step-by-step için adım sayacı
        self.instructions = []  # İşlenecek MIPS komutlarını depolamak için liste
        
        self.create_widgets()  # Arayüz bileşenlerini oluştur
        self.commands = MIPSCommands(self.tree)  # Komut sınıfını başlat

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

        clear_button = tk.Button(self.console_frame, text="Clear", command=self.clear_registers)
        clear_button.pack(side='left')

        run_button = tk.Button(self.console_frame, text="Run", command=self.read_mips_code)
        run_button.pack(side='left')

        # Step butonu ekle
        step_button = tk.Button(self.console_frame, text="Step", command=self.step_execution)
        step_button.pack(side='left')

    def clear_registers(self):
        self.commands.clear_registers()  # MIPSCommands sınıfındaki clear_registers fonksiyonunu çağırır
        self.console_output.insert('end', "Registers cleared.\n")  # Konsola mesaj yazdır

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

    def to_hex(self, value):
        """Verilen değeri hexadecimal formata dönüştürür."""
        return f"0x{int(value):08X}"

    def read_mips_code(self):
        self.console_output.delete('1.0', 'end')  # Önceki konsol çıktısını temizler
        code = self.edit_text.get('1.0', 'end-1c')  # Düzenleme alanındaki tüm kodu al
        lines = [line.strip() for line in code.split('\n') if line.strip()]  # Satırları temizle
        self.instructions = []  # Komutları temizle

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

        # .text bölümünden komutları topla
        in_main = False
        for line in lines:
            if line.startswith("main:"):
                in_main = True
                continue
            if in_main:
                self.instructions.append(line.strip())

        self.current_line = 0  # Adım sayacını sıfırla
        self.console_output.insert('end', "Loaded instructions. Ready to step through.\n")

    def step_execution(self):
        """Bir sonraki komutu çalıştırır."""
        if self.current_line < len(self.instructions):
            line = self.instructions[self.current_line]
            parts = [part.strip() for part in line.replace(",", " ").split()]
            command = parts[0]

            match command:
                #Register instructions
                case "lw":
                    register, var_name = parts[1], parts[2]
                    if var_name in self.data_section:
                        self.commands.update_register_value(register, int(self.data_section[var_name], 16))
                #Arithmetic instructions
                case "add":
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    self.commands.execute_add_command(dest, src1, src2)
                case "sub":
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    self.commands.execute_sub_command(dest, src1, src2)
                case "div":
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    error_message = self.commands.execute_div_command(dest, src1, src2)
                    if error_message:
                        self.console_output.insert('end', f"{error_message}\n")
                case "mul":
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    self.commands.execute_mul_command(dest, src1, src2)
                #Logical instructions
                case "and":
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    self.commands.execute_and_command(dest, src1, src2)
                case "or":
                    dest, src1, src2 = parts[1], parts[2], parts[3]
                    self.commands.execute_or_command(dest, src1, src2)
                case "andi":
                    dest, src1, immediate = parts[1], parts[2], int(parts[3])
                    self.commands.execute_andi_command(dest, src1, immediate)
                case "ori":
                    dest, src1, immediate = parts[1], parts[2], int(parts[3])
                    self.commands.execute_ori_command(dest, src1, immediate)
                case "sll":
                    dest, src1, shift_amount = parts[1], parts[2], int(parts[3])
                    self.commands.execute_sll_command(dest, src1, shift_amount)
                case "srl":
                    dest, src1, shift_amount = parts[1], parts[2], int(parts[3])
                    self.commands.execute_srl_command(dest, src1, shift_amount)

            self.console_output.insert('end', f"Executed: {line}\n")
            self.current_line += 1
        else:
            self.console_output.insert('end', "No more instructions to execute.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = MIPSIDE(root)
    root.mainloop()
