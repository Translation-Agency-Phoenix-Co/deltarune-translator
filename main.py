import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel, Text, Scrollbar
from googletrans import Translator, LANGUAGES
import threading
import pygame

class DeltaruneTranslator:
    def __init__(self, root):
        # основное окно
        self.root = root
        self.root.title("Deltarune Translator")
        self.root.geometry("700x500")

        pygame.mixer.init()
        self.music_volume = tk.DoubleVar(value=0.5)
        self.sound_volume = tk.DoubleVar(value=0.5)
        self.music_enabled = tk.BooleanVar(value=True)

        # пути к музыке
        self.idle_music_path = "idle_music.mp3"
        self.translation_music_path = "translation_music.mp3"
        self.chord_sound_path = "chord.mp3"

        # загрузка звуков
        self.chord_sound = pygame.mixer.Sound(self.chord_sound_path)
        self.chord_sound.set_volume(self.sound_volume.get())

        self.source_file = tk.StringVar()
        self.target_file = tk.StringVar()
        self.source_lang = tk.StringVar(value='en')
        self.target_lang = tk.StringVar(value='ru')
        self.progress_var = tk.IntVar()
        self.total_lines = 0
        self.translated_lines = 0

        self.create_widgets()

        self.translator = Translator()

        # окно для логов
        self.log_window = Toplevel(root)
        self.log_window.title("Translation Log")
        self.log_window.geometry("500x400")
        self.setup_log_window()

        # запуск фоновой музяки :3
        self.play_idle_music()

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="Translation")

        sound_tab = ttk.Frame(notebook)
        notebook.add(sound_tab, text="Sound Settings")
        self.create_sound_widgets(sound_tab)

        file_frame = ttk.LabelFrame(main_tab, text="File Selection")
        file_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(file_frame, text="Source JSON:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(file_frame, textvariable=self.source_file, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_source).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(file_frame, text="Target JSON:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(file_frame, textvariable=self.target_file, width=50).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(file_frame, text="Save As", command=self.browse_target).grid(row=1, column=2, padx=5, pady=2)

        lang_frame = ttk.LabelFrame(main_tab, text="Language Settings")
        lang_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(lang_frame, text="Source Language:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        source_combo = ttk.Combobox(lang_frame, textvariable=self.source_lang, state="readonly")
        source_combo['values'] = list(LANGUAGES.keys())
        source_combo.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(lang_frame, text="Target Language:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        target_combo = ttk.Combobox(lang_frame, textvariable=self.target_lang, state="readonly")
        target_combo['values'] = list(LANGUAGES.keys())
        target_combo.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Button(main_tab, text="Translate", command=self.start_translation_thread).pack(pady=10)

        progress_frame = ttk.Frame(main_tab)
        progress_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(progress_frame, text="Progress:").pack(anchor="w")
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )
        self.progress_bar.pack(fill="x", pady=5)
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack(anchor="w")

    def create_sound_widgets(self, tab):
        ttk.Checkbutton(tab, text="Enable Background Music", variable=self.music_enabled, command=self.toggle_music).pack(pady=10)
        ttk.Label(tab, text="Music Volume:").pack(anchor="w")
        ttk.Scale(tab, from_=0, to=1, variable=self.music_volume, command=self.update_music_volume).pack(fill="x", padx=10, pady=5)
        ttk.Label(tab, text="Sound Effects Volume:").pack(anchor="w")
        ttk.Scale(tab, from_=0, to=1, variable=self.sound_volume, command=self.update_sound_volume).pack(fill="x", padx=10, pady=5)

    def toggle_music(self):
        if self.music_enabled.get():
            if not pygame.mixer.music.get_busy():
                self.play_idle_music()
        else:
            self.stop_music()

    def update_music_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume))

    def update_sound_volume(self, volume):
        self.chord_sound.set_volume(float(volume))

    def setup_log_window(self):
        log_frame = ttk.Frame(self.log_window)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_text = Text(log_frame, height=20, wrap="word")
        scrollbar = Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(state="disabled")

    def browse_source(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.source_file.set(file_path)
            dir_name, file_name = os.path.split(file_path)
            target_name = f"{os.path.splitext(file_name)[0]}_translated.json"
            self.target_file.set(os.path.join(dir_name, target_name))

    def browse_target(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.target_file.set(file_path)

    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.log_window.update_idletasks()
        # проигрываем звук при появлении окна
        if "Error" in message or "completed" in message:
            self.play_chord()

    def update_progress(self):
        if self.total_lines > 0:
            progress = int((self.translated_lines / self.total_lines) * 100)
            self.progress_var.set(progress)
            self.status_label.config(
                text=f"Translated {self.translated_lines}/{self.total_lines} lines"
            )
            self.root.update_idletasks()

    def should_translate(self, key, value):
        if key == "date":
            return False
        if not isinstance(value, str):
            return False
        if not value.strip():
            return False
        return True

    # музыка
    def play_idle_music(self):
        if self.music_enabled.get():
            pygame.mixer.music.load(self.idle_music_path)
            pygame.mixer.music.set_volume(self.music_volume.get())
            pygame.mixer.music.play(-1)

    def play_translation_music(self):
        if self.music_enabled.get():
            pygame.mixer.music.load(self.translation_music_path)
            pygame.mixer.music.set_volume(self.music_volume.get())
            pygame.mixer.music.play(-1)

    def stop_music(self):
        pygame.mixer.music.stop()

    def play_chord(self):
        self.chord_sound.set_volume(self.sound_volume.get())
        self.chord_sound.play()

    # перевод
    def start_translation(self):
        source_path = self.source_file.get()
        target_path = self.target_file.get()

        if not source_path or not target_path:
            self.log_message("Error: Please select source and target files")
            self.play_chord()
            messagebox.showerror("Error", "Please select source and target files")
            return

        try:
            # останавливаем ожидание, врубаем перевод
            self.stop_music()
            self.play_translation_music()

            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.total_lines = 0
            self.translated_lines = 0

            for key, value in data.items():
                if self.should_translate(key, value):
                    self.total_lines += 1

            self.log_message(f"Found {self.total_lines} lines to translate")
            self.update_progress()

            for key, value in data.items():
                if self.should_translate(key, value):
                    try:
                        translated = self.translator.translate(
                            value,
                            src=self.source_lang.get(),
                            dest=self.target_lang.get()
                        ).text
                        data[key] = translated
                        self.translated_lines += 1
                        self.log_message(f"Translated: {value[:50]}... → {translated[:50]}...")
                    except Exception as e:
                        self.log_message(f"Error translating {key}: {str(e)}")
                        self.translated_lines += 1
                    self.update_progress()

            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            self.log_message("Translation completed successfully!")
            self.stop_music()
            self.play_idle_music()
            self.play_chord()
            messagebox.showinfo("Success", "Translation completed!")

        except Exception as e:
            self.stop_music()
            self.play_idle_music()
            self.log_message(f"Critical error: {str(e)}")
            self.play_chord()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def start_translation_thread(self):
        translation_thread = threading.Thread(target=self.start_translation)
        translation_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DeltaruneTranslator(root)
    root.mainloop()
