import fitz  # PyMuPDF
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog

class MangaReader:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#1e1e1e")
        self.root.geometry("800x600")
        self.root.title("PDF Reader")
        self.root.iconbitmap("")
        self.root.overrideredirect(False)
     
        self.doc = None
        self.page_num = 0
        self.original_image = None
        self.tk_img = None
        self._resize_after = None
        self.is_fullscreen = False

        self.canvas = tk.Label(root, bg="black")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.page_label = tk.Label(root, text="", font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e")
        self.page_label.grid(row=0, column=0, sticky="ne", padx=10, pady=10)

        self.control_frame = tk.Frame(root, bg="#1e1e1e")
        self.control_frame.grid(row=1, column=0, pady=5, sticky="ew")

        btn_cfg = {"bg": "#333", "fg": "#e0e0e0", "activebackground": "#444", "activeforeground": "#ffffff"}

        self.open_btn = tk.Button(self.control_frame, text="Open PDF", command=self.open_pdf, **btn_cfg)
        self.prev_btn = tk.Button(self.control_frame, text="<< Prev", command=self.prev_page, **btn_cfg)
        self.next_btn = tk.Button(self.control_frame, text="Next >>", command=self.next_page, **btn_cfg)

        self.open_btn.grid(row=0, column=0, padx=5, sticky="ew")
        self.prev_btn.grid(row=0, column=1, padx=5, sticky="ew")
        self.next_btn.grid(row=0, column=2, padx=5, sticky="ew")

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        root.bind("<KeyPress>", self.keypress_handler)
        root.bind("<Configure>", self.on_resize)

    def keypress_handler(self, event):
        ctrl = (event.state & 0x4) != 0

        if ctrl and event.keycode == 79:
            self.open_pdf()
        elif event.keycode == 37:
            self.prev_page()
        elif event.keycode == 39:
            self.next_page()
        elif event.keysym == "F11":
            self.toggle_fullscreen()
        elif event.keysym == "Escape" and self.is_fullscreen:
            self.toggle_fullscreen()

    def open_pdf(self, event=None):
        filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if filepath:
            self.doc = fitz.open(filepath)
            self.page_num = 0
            self.show_page()
            self.root.title(f"PDF Reader - {filepath.split('/')[-1]}")

    def show_page(self):
        if not self.doc:
            return

        page = self.doc.load_page(self.page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        self.original_image = img
        self.update_resized_image()
        self.page_label.config(text=f"Страница {self.page_num + 1} из {len(self.doc)}")

    def update_resized_image(self, event=None):
        if not self.original_image:
            return

        win_width = self.canvas.winfo_width()
        win_height = self.canvas.winfo_height()

        img_ratio = self.original_image.width / self.original_image.height
        win_ratio = win_width / win_height

        if img_ratio > win_ratio:
            new_width = win_width
            new_height = int(win_width / img_ratio)
        else:
            new_height = win_height
            new_width = int(win_height * img_ratio)

        resized = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(resized)
        self.canvas.config(image=self.tk_img)

    def on_resize(self, event):
        if event.widget == self.root:
            if self._resize_after:
                try:
                    self.root.after_cancel(self._resize_after)
                except Exception:
                    pass
            self._resize_after = self.root.after(100, self.update_resized_image)

    def next_page(self):
        if self.doc and self.page_num < len(self.doc) - 1:
            self.page_num += 1
            self.show_page()

    def prev_page(self):
        if self.doc and self.page_num > 0:
            self.page_num -= 1
            self.show_page()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

        if self.is_fullscreen:
            self.root.overrideredirect(True)
            self.control_frame.grid_forget()
        else:
            self.root.overrideredirect(False)
            self.control_frame.grid(row=1, column=0, pady=5, sticky="ew")
            self.root.configure(bg="#1e1e1e")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    app = MangaReader(root)

    root.deiconify()
    root.mainloop()
