import tkinter as tk
from PIL import ImageTk, Image, ImageDraw, ImageFont
import qrcode
import os
import sys
import random
import ctypes
import getpass
from datetime import datetime

def resource_path(relative_path):
    """ Получает путь к файлу внутри скомпилированного EXE """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

QUOTES_FILE = resource_path("quotes.txt")

def get_daily_user_quote():
    """
    Выбирает фразу без создания файлов на диске.
    Использует системную дату и логин как ключ для генератора случайных чисел.
    """
    username = getpass.getuser()
    today_seed = datetime.now().strftime("%Y%m%d")
    random_seed = f"{today_seed}_{username}"

    if not os.path.exists(QUOTES_FILE):
        return "Ошибка: База данных (quotes.txt) не найдена внутри системы."

    try:
        with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
            all_quotes = [line.strip() for line in f if line.strip()]
        
        if not all_quotes: 
            return "База фраз пуста."
        
        random.seed(random_seed)
        new_quote = random.choice(all_quotes)
        return new_quote
    except Exception as e:
        return f"Ошибка доступа: {e}"

def create_close_button(size=40, is_hover=False):
    """Создаёт сглаженную кнопку закрытия через PIL"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if is_hover:
        draw.ellipse([2, 2, size-3, size-3], fill=(255, 68, 68, 230))
        cross_size = size // 6
        center = size // 2
        draw.line([center-cross_size, center-cross_size, center+cross_size, center+cross_size], 
                 fill='white', width=3)
        draw.line([center+cross_size, center-cross_size, center-cross_size, center+cross_size], 
                 fill='white', width=3)
    else:
        draw.ellipse([2, 2, size-3, size-3], fill=(200, 200, 200, 180))
        cross_size = size // 6
        center = size // 2
        draw.line([center-cross_size, center-cross_size, center+cross_size, center+cross_size], 
                 fill=(80, 80, 80, 255), width=2)
        draw.line([center+cross_size, center-cross_size, center-cross_size, center+cross_size], 
                 fill=(80, 80, 80, 255), width=2)
    
    return ImageTk.PhotoImage(img)

def create_qr_app():
    quote = get_daily_user_quote()
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    
    qr_size = 250
    bg_color = "white"
    btn_size = 40
    btn_offset = 15

    try:
        HWND = ctypes.windll.user32.GetParent(root.winfo_id())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 33, ctypes.byref(ctypes.c_int(2)), 4)
    except: 
        pass

    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(quote)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    img_qr = img_qr.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(img_qr)

    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{qr_size}x{qr_size}+{(sw-qr_size)//2}+{(sh-qr_size)//2}")
    root.configure(bg=bg_color)

    label = tk.Label(root, image=tk_img, bg=bg_color, bd=0)
    label.image = tk_img
    label.pack(expand=True, fill='both')

    btn_window = tk.Toplevel(root)
    btn_window.overrideredirect(True)
    btn_window.attributes("-topmost", True)
    btn_window.configure(bg=bg_color)
    
    if sys.platform == "win32":
        btn_window.attributes('-transparentcolor', bg_color)
    
    btn_window.geometry(f"{btn_size}x{btn_size}")
    
    btn_close = tk.Label(btn_window, cursor="hand2", bg=bg_color)
    btn_close.pack(expand=True, fill='both')
    
    btn_normal = create_close_button(btn_size, is_hover=False)
    btn_hover = create_close_button(btn_size, is_hover=True)
    
    btn_close.configure(image=btn_normal)
    btn_close.image_normal = btn_normal
    btn_close.image_hover = btn_hover

    def on_enter(e):
        btn_close.configure(image=btn_close.image_hover)
    
    def on_leave(e):
        btn_close.configure(image=btn_close.image_normal)

    btn_close.bind("<Button-1>", lambda e: root.destroy())
    btn_close.bind("<Enter>", on_enter)
    btn_close.bind("<Leave>", on_leave)

    def update_button_position():
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        # Сдвинул кнопку правее: теперь btn_offset добавляется к правому краю
        btn_x = root_x + qr_size + btn_offset
        btn_y = root_y - btn_offset * 2
        btn_window.geometry(f"+{btn_x}+{btn_y}")
        btn_window.after(50, update_button_position)

    def start_move(event):
        root.x, root.y = event.x, event.y
        
    def on_move(event):
        x = root.winfo_x() + (event.x - root.x)
        y = root.winfo_y() + (event.y - root.y)
        root.geometry(f"+{x}+{y}")

    label.bind("<ButtonPress-1>", start_move)
    label.bind("<B1-Motion>", on_move)

    update_button_position()

    def on_closing():
        btn_window.destroy()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

if __name__ == "__main__":
    create_qr_app()