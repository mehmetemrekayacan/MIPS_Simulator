# mips_commands.py

class MIPSCommands:
    def __init__(self, tree):
        self.tree = tree

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
    
    def clear_registers(self):
        """Tüm register'ları sıfırlamak için fonksiyon."""
        for item in self.tree.get_children():
            self.tree.set(item, column="Value", value="0x00000000")  # Tüm register'ların değerini sıfırla

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
            return "Error: Division by zero!"  # Hata mesajı döndür

    def execute_mul_command(self, dest, src1, src2):
        """MUL komutunu işler ve sonucu hedef register'a yazar."""
        val1 = self.get_register_value(src1)  # Kaynak 1'in değeri
        val2 = self.get_register_value(src2)  # Kaynak 2'nin değeri
        result = val1 * val2  # Çarpma işlemi
        self.update_register_value(dest, result)  # Sonucu hedef register'a yaz


#LOGİCAL INSTRUCTIONS

    def execute_and_command(self, dest, src1, src2):
        """AND komutunu işler ve sonucu hedef register'a yazar (Bitwise AND)."""
        val1 = self.get_register_value(src1)
        val2 = self.get_register_value(src2)
        result = val1 & val2  # Bitwise AND
        self.update_register_value(dest, result)

    def execute_or_command(self, dest, src1, src2):
        """OR komutunu işler ve sonucu hedef register'a yazar (Bitwise OR)."""
        val1 = self.get_register_value(src1)
        val2 = self.get_register_value(src2)
        result = val1 | val2  # Bitwise OR
        self.update_register_value(dest, result)

    def execute_andi_command(self, dest, src1, immediate):
        """ANDI komutunu işler ve sonucu hedef register'a yazar (Bitwise AND with immediate)."""
        val1 = self.get_register_value(src1)
        result = val1 & immediate  # Bitwise AND with immediate
        self.update_register_value(dest, result)

    def execute_ori_command(self, dest, src1, immediate):
        """ORI komutunu işler ve sonucu hedef register'a yazar (Bitwise OR with immediate)."""
        val1 = self.get_register_value(src1)
        result = val1 | immediate  # Bitwise OR with immediate
        self.update_register_value(dest, result)

    def execute_sll_command(self, dest, src1, shift_amount):
        """SLL komutunu işler ve sonucu hedef register'a yazar (Shift left logical)."""
        val1 = self.get_register_value(src1)
        result = val1 << shift_amount  # Shift left by constant number of bits
        self.update_register_value(dest, result)

    def execute_srl_command(self, dest, src1, shift_amount):
        """SRL komutunu işler ve sonucu hedef register'a yazar (Shift right logical)."""
        val1 = self.get_register_value(src1)
        result = val1 >> shift_amount  # Shift right by constant number of bits
        self.update_register_value(dest, result)
