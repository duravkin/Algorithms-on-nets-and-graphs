import tkinter as tk
from tkinter import messagebox
import heapq

# --- Реализация алгоритма Хаффмана ---
class HuffmanNode:
    def __init__(self, freq, symbol, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq

def huffman_encoding(symbols):
    heap = [HuffmanNode(freq, symbol) for symbol, freq in symbols.items()]
    heapq.heapify(heap)
    
    if not heap:
        return {}
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(left.freq + right.freq, None, left, right)
        heapq.heappush(heap, merged)
    
    root = heap[0]
    codes = {}
    def generate_codes(node, current_code=""):
        if node is None:
            return
        if node.symbol is not None:
            codes[node.symbol] = current_code or "0"
        else:
            generate_codes(node.left, current_code + "0")
            generate_codes(node.right, current_code + "1")
    generate_codes(root)
    return codes

# --- Реализация алгоритма Шеннона–Фанно ---
def shannon_fano(symbols):
    symbols_sorted = sorted(symbols.items(), key=lambda x: x[1], reverse=True)
    codes = {symbol: '' for symbol, _ in symbols_sorted}
    def recursive(symbols_list):
        if len(symbols_list) <= 1:
            return
        total = sum(freq for _, freq in symbols_list)
        acc = 0
        partition_index = 0
        for i, (_, freq) in enumerate(symbols_list):
            acc += freq
            if acc >= total / 2:
                partition_index = i
                break
        left = symbols_list[:partition_index + 1]
        right = symbols_list[partition_index + 1:]
        for symbol, _ in left:
            codes[symbol] += '0'
        for symbol, _ in right:
            codes[symbol] += '1'
        recursive(left)
        recursive(right)
    recursive(symbols_sorted)
    return codes

# --- Основное приложение на Tkinter ---
class CompressionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Сжатие текста: Хаффман vs Шеннон–Фанно")
        self.geometry("700x700")
        
        # Переключатель режимов: кодирование или дешифрование
        self.mode_var = tk.StringVar(value="encode")
        tk.Label(self, text="Выберите режим:").pack(pady=5)
        mode_frame = tk.Frame(self)
        mode_frame.pack(pady=5)
        tk.Radiobutton(mode_frame, text="Кодирование", variable=self.mode_var,
                       value="encode", command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Дешифрование", variable=self.mode_var,
                       value="decode", command=self.update_mode).pack(side=tk.LEFT, padx=5)
        
        # Поле для ввода исходного текста (используется только в режиме кодирования)
        tk.Label(self, text="Введите текст для сжатия:").pack(pady=5)
        self.text_input = tk.Text(self, height=5)
        self.text_input.pack(padx=10, fill=tk.BOTH)
        
        # Переключатель методов сжатия (актуален только для кодирования)
        self.method_var = tk.StringVar(value="Huffman")
        methods_frame = tk.Frame(self)
        methods_frame.pack(pady=5)
        tk.Label(methods_frame, text="Выберите метод:").pack(side=tk.LEFT)
        tk.Radiobutton(methods_frame, text="Код Хаффмана", variable=self.method_var,
                       value="Huffman").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(methods_frame, text="Код Шеннона–Фанно", variable=self.method_var,
                       value="Shannon-Fano").pack(side=tk.LEFT, padx=5)
        
        # Кнопки для кодирования/дешифрования и сброса
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        self.action_button = tk.Button(button_frame, text="Сжать текст", command=self.compress_text)
        self.action_button.pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Сброс", command=self.reset_text).pack(side=tk.LEFT, padx=5)
        
        # Область для вывода закодированного текста
        tk.Label(self, text="Закодированный текст:").pack(pady=5)
        self.encoded_output = tk.Text(self, height=10, state=tk.DISABLED)
        self.encoded_output.pack(padx=10, fill=tk.BOTH)
        
        # Область для вывода списка кодов
        tk.Label(self, text="Список кодов:").pack(pady=5)
        self.codes_output = tk.Text(self, height=10, state=tk.DISABLED)
        self.codes_output.pack(padx=10, fill=tk.BOTH, expand=True)
        
        self.update_mode()  # Устанавливаем начальное состояние виджетов

    def update_mode(self):
        mode = self.mode_var.get()
        if mode == "encode":
            # Режим кодирования: поле ввода активно, а поля результатов недоступны для редактирования.
            self.text_input.config(state=tk.NORMAL)
            self.encoded_output.config(state=tk.DISABLED)
            self.codes_output.config(state=tk.DISABLED)
            self.action_button.config(text="Сжать текст", command=self.compress_text)
        else:
            # Режим дешифрования: поля для закодированного текста и списка кодов доступны для ввода,
            # а исходное поле для текста недоступно.
            self.text_input.config(state=tk.DISABLED)
            self.encoded_output.config(state=tk.NORMAL)
            self.codes_output.config(state=tk.NORMAL)
            self.action_button.config(text="Дешифровать текст", command=self.decompress_text)
    
    def compress_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите текст для сжатия.")
            return
        
        # Подсчёт частот символов
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        
        # Выбор метода кодирования
        method = self.method_var.get()
        if method == "Huffman":
            codes = huffman_encoding(freq)
        elif method == "Shannon-Fano":
            codes = shannon_fano(freq)
        else:
            codes = {}
        
        # Формирование закодированного текста
        try:
            encoded_text = ''.join(codes[char] for char in text)
        except KeyError:
            messagebox.showerror("Ошибка", "Не удалось закодировать текст. Проверьте входные данные.")
            return
        
        # Формирование строки с таблицей кодов
        mapping_str = ""
        for char, code in codes.items():
            display_char = char # if char != " " else "[space]"
            mapping_str += f"'{display_char}': {code}\n"
        
        # Вывод результатов
        self.encoded_output.config(state=tk.NORMAL)
        self.encoded_output.delete("1.0", tk.END)
        self.encoded_output.insert(tk.END, encoded_text)
        self.encoded_output.config(state=tk.DISABLED)
        
        self.codes_output.config(state=tk.NORMAL)
        self.codes_output.delete("1.0", tk.END)
        self.codes_output.insert(tk.END, mapping_str)
        self.codes_output.config(state=tk.DISABLED)
    
    def decompress_text(self):
        # Получение данных из полей для дешифрования
        encoded_text = self.encoded_output.get("1.0", tk.END).strip()
        mapping_str = self.codes_output.get("1.0", tk.END).strip()
        if not encoded_text or not mapping_str:
            messagebox.showwarning("Предупреждение", "Введите закодированный текст и список кодов.")
            return
        
        # Парсинг списка кодов (ожидается формат: 'a': 010)
        mapping = {}
        for line in mapping_str.splitlines():
            if ":" not in line:
                continue
            parts = line.split(":", 1)
            key_part = parts[0].strip()
            code_part = parts[1].strip()
            if (key_part.startswith("'") and key_part.endswith("'")) or \
               (key_part.startswith('"') and key_part.endswith('"')):
                key = key_part[1:-1]
            else:
                key = key_part
            # if key == "[space]":  # Если ключ равен "[space]", заменяем его на пробел
            #     key = " "
            mapping[key] = code_part
        
        # Создание обратного отображения: код -> символ
        reverse_mapping = {v: k for k, v in mapping.items()}
        
        # Дешифрование сообщения
        decoded_text = ""
        current_code = ""
        for bit in encoded_text:
            current_code += bit
            if current_code in reverse_mapping:
                decoded_text += reverse_mapping[current_code]
                current_code = ""
        if current_code:
            messagebox.showwarning("Предупреждение", "Некорректный код: остаток не может быть декодирован.")
            return
        
        # Вывод результата дешифрования (например, в отдельном окне)
        # messagebox.showinfo("Результат дешифрования", f"Декодированный текст:\n{decoded_text}")

        # Разблокируем поле ввода, очистим его и вставим декодированный текст
        # self.text_input.config(state=tk.NORMAL)
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, decoded_text)

    
    def reset_text(self):
        # Сброс всех полей и восстановление исходного состояния
        self.text_input.config(state=tk.NORMAL)
        self.text_input.delete("1.0", tk.END)
        
        self.encoded_output.config(state=tk.NORMAL)
        self.encoded_output.delete("1.0", tk.END)
        if self.mode_var.get() == "encode":
            self.encoded_output.config(state=tk.DISABLED)
        
        self.codes_output.config(state=tk.NORMAL)
        self.codes_output.delete("1.0", tk.END)
        if self.mode_var.get() == "encode":
            self.codes_output.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = CompressionApp()
    app.mainloop()
