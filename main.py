from customtkinter import *
from tkinter import PhotoImage
from pygame import mixer, event, USEREVENT
import pygame
from random import randint

from threading import Thread
import json
import xdialog
from googletrans import Translator, LANGUAGES
import libretranslatepy
import requests
import os
import platform

pygame.init()
mixer.init()
MUSIC_END = USEREVENT+1
backsound_volume = 100
sfx_volume = 100
mixer.music.set_endevent(MUSIC_END)
mixer.music.set_volume(sfx_volume)
random_background_music = randint(1,4)
if random_background_music == 1:
    mixer.music.load('backsound/idle_music.mp3')
    mixer.music.play()
elif random_background_music == 2:
    mixer.music.load('backsound/Ever_Higher.mp3')
    mixer.music.play(loops=2)
elif random_background_music == 3:
    mixer.music.load('backsound/12am.mp3')
    mixer.music.play(loops=2)
elif random_background_music == 4:
    mixer.music.load('backsound/13am.mp3')
    mixer.music.play()

done_sfx = mixer.Sound('sound/done.wav')
done_sfx.set_volume(sfx_volume)

error_sfx = mixer.Sound('sound/error.wav')
error_sfx.set_volume(sfx_volume)

des = CTk()
des.title('Deltarune translator')
des.geometry('800x500')
des.resizable(False, False)

CTkLabel(des, image=PhotoImage(file='images/background.png'), text='').place(x=0,y=0)

action_start = 'translate'
music_looped = True
total_lines = 0
translated_lines = 0
translator = Translator()

translated_lines_math = 0

yandex_api = 'Enter'
yandex_folder_api = 'Enter'
libre_api = 'Enter'
libre_url = 'Enter'

def music_loop():
    if music_looped == True:
        for eventd in event.get():
            if eventd.type == MUSIC_END:
                des.after(500)
                random_background_music = randint(1,4)
                if random_background_music == 1:
                    mixer.music.load('backsound/idle_music.mp3')
                    mixer.music.play()
                elif random_background_music == 2:
                    mixer.music.load('backsound/Ever_Higher.mp3')
                    mixer.music.play(loops=2)
                elif random_background_music == 3:
                    mixer.music.load('backsound/12am.mp3')
                    mixer.music.play(loops=2)
                elif random_background_music == 4:
                    mixer.music.load('backsound/13am.mp3')
                    mixer.music.play()
        des.after(1000, music_loop)  
    else:
        return False
des.after(50, music_loop)

def clopen_log():
    if log_button._text == 'Log':
        vol_button.configure(state='disabled')
        log_button.configure(text='/')
        des.update()
        des.after(200)
        log_button.configure(text='-')
        main_frame.place_forget()
        des.update()
        des.after(200)
        log_button.configure(text='X')
        log_frame.place(x=20,y=20)
        des.update()
    elif log_button._text == 'X':
        log_button.configure(text='/')
        des.update()
        des.after(200)
        log_button.configure(text='-')
        log_frame.place_forget()
        des.update()
        des.after(200)
        log_button.configure(text='Log')
        vol_button.configure(state='normal')
        main_frame.place(x=20,y=20)
        des.update()

def clopen_volume():
    if vol_button._text == 'Volume':
        log_button.configure(state='disabled')
        vol_button.configure(text='/')
        des.update()
        des.after(200)
        vol_button.configure(text='-')
        main_frame.place_forget()
        des.update()
        des.after(200)
        vol_button.configure(text='X')
        setvol_frame.place(x=20,y=20)
        des.update()
    elif vol_button._text == 'X':
        vol_button.configure(text='/')
        des.update()
        des.after(200)
        vol_button.configure(text='-')
        setvol_frame.place_forget()
        des.update()
        des.after(200)
        vol_button.configure(text='Volume')
        log_button.configure(state='normal')
        main_frame.place(x=20,y=20)
        des.update()

def change_background_volume(value):
    global backsound_volume
    
    backsound_volume = value
    mixer.music.set_volume(backsound_volume)

    setvol_background_music_int.configure(text=int(backsound_volume*100))
    des.update()

def change_effect_volume(value):
    global sfx_volume

    done_sfx.set_volume(sfx_volume)
    error_sfx.set_volume(sfx_volume)

    sfx_volume = value
    setvol_effect_music_int.configure(text=int(sfx_volume*100))
    des.update()

def change_source_lang():
    try:
        source_file_frame_textbox.delete()
    except:
        pass
    try:
        target_file_frame_textbox.delete()
    except:
        pass
    set_lang = xdialog.open_file('Open DELTARUNE Languages file', filetypes=[("Lang file", "*.json")])
    source_file_frame_textbox.delete(0, 'end')
    target_file_frame_textbox.delete(0, 'end')
    source_file_frame_textbox.insert('end', set_lang)

    dir_name, file_name = os.path.split(set_lang)
    target_name = f"{os.path.splitext(file_name)[0]}_translated.json"

    target_file_frame_textbox.insert('end', os.path.join(dir_name, target_name))

def change_target_lang():
    try:
        target_file_frame_textbox.delete()
    except:
        pass
    set_lang = xdialog.save_file('Open DELTARUNE Languages file', filetypes=[("Lang file", "*.json")])
    target_file_frame_textbox.delete(0, 'end')
    target_file_frame_textbox.insert('end', set_lang)

def should_translate(key, value):
    if key == "date":
        return False
    if not isinstance(value, str):
        return False
    if not value.strip():
        return False
    return True

def update_progress():
    global translated_lines_math
    if total_lines > 0:
        translated_lines_math += 1
        if translated_lines_math == int(total_lines / 100):
            translated_lines_math = 0
            progress_progressbar.set(progress_progressbar.get() + 0.01)
        progress_text.configure(
            text=f"{translated_lines}/{total_lines}"
        )
        des.update_idletasks()

def translate_process():
    global total_lines, translated_lines, music_looped, yandex_api, yandex_folder_api, libre_api, libre_url

    source_lang = lang_frame_source_combo.get()
    target_lang = lang_frame_target_combo.get()
    source_path = source_file_frame_textbox.get()
    target_path = target_file_frame_textbox.get()

    if translator_api.get() == 1:
        inputer_api = CTkInputDialog(text="Yandex Translate API", title="Deltarune Translator")
        yandex_api = inputer_api.get_input()
        folder_id_api = CTkInputDialog(text="Yandex Translate Folder ID", title="Deltarune Translator")
        yandex_folder_api = folder_id_api.get_input()
    elif translator_api.get() == 2:
        inputer_api = CTkInputDialog(text="LibreTranslate instances URL", title="Deltarune Translator")
        libre_url = inputer_api.get_input()
        api_inputer = CTkInputDialog(text="LibreTranslate API", title="Deltarune Translator")
        libre_api = api_inputer.get_input()
        libretrans = libretranslatepy.LibreTranslateAPI(libre_url, libre_api)

    try:
        progress_text.configure(text='Checking lines from source file')
        des.update()
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_lines = 0
        translated_lines = 0

        for key, value in data.items():
            if should_translate(key, value):
                total_lines += 1

        log_textbox.insert("0.0", f"Found {total_lines} lines to translate\n")
        update_progress()
        des.update()

        for key, value in data.items():
            if should_translate(key, value):
                if translator_api.get() == 0:
                    try:
                        translated = translator.translate(
                        value,
                        src=source_lang,
                        dest=target_lang
                        ).text
                        data[key] = translated
                        translated_lines += 1

                        log_textbox.insert("0.0", f"{value} > {translated}\n")
                    except Exception as e:
                        error_sfx.play()
                        log_textbox.insert("0.0", f"Error translating {key}: {str(e)}\n")
                        translated_lines += 1
                elif translator_api.get() == 1:
                    try:
                        body = {
                            "targetLanguageCode": target_path,
                            "texts": value,
                            "folderId": yandex_folder_api,
                        }
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Api-Key {0}".format(yandex_api),
                        }
                        response = requests.post(
                            "https://translate.api.cloud.yandex.net/translate/v2/translate",
                            json=body,
                            headers=headers,
                        )
                        data[key] = response.text

                        translated_lines += 1

                        log_textbox.insert("0.0", f"{value} > {translated}\n")
                    except Exception as e:
                        error_sfx.play()
                        log_textbox.insert("0.0", f"Error translating {key}: {str(e)}\n")
                        translated_lines += 1
                elif translator_api.get() == 2:
                    try:
                        translated = libretrans.translate(value, source_lang, target_lang)

                        data[key] = translated

                        translated_lines += 1

                        log_textbox.insert("0.0", f"{value} > {translated}\n")
                    except Exception as e:
                        error_sfx.play()
                        log_textbox.insert("0.0", f"Error translating {key}: {str(e)}\n")
                        translated_lines += 1
                update_progress()
                des.update()

        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        log_textbox.insert("0.0", "Translation completed successfully!\n")
        done_sfx.play()
        progress_text.configure(text="Translation completed!\n")
        des.after(500)
        mixer.music.pause()
        des.update()
        start_translate_button.configure(state='normal')
        lang_frame_source_combo.configure(state='normal')
        lang_frame_target_combo.configure(state='normal')
        source_file_frame_button.configure(state='normal')
        target_file_frame_button.configure(state='normal')
        source_file_frame_textbox.configure(state='normal')
        target_file_frame_textbox.configure(state='normal')
        tarnslator_frame_radio_google.configure(state='normal')
        tarnslator_frame_radio_yandex.configure(state='normal')
        tarnslator_frame_radio_libre.configure(state='normal')
        des.update()
        des.after(1000)
        music_looped = True
        music_loop()
    except:
        mixer.music.pause()
        error_sfx.play()
        progress_text.configure(text='Read file error!!!')
        des.update()
        start_translate_button.configure(state='normal')
        lang_frame_source_combo.configure(state='normal')
        lang_frame_target_combo.configure(state='normal')
        source_file_frame_button.configure(state='normal')
        target_file_frame_button.configure(state='normal')
        source_file_frame_textbox.configure(state='normal')
        target_file_frame_textbox.configure(state='normal')
        tarnslator_frame_radio_google.configure(state='normal')
        tarnslator_frame_radio_yandex.configure(state='normal')
        tarnslator_frame_radio_libre.configure(state='normal')
        des.update()
        des.after(1000)
        music_looped = True
        music_loop()

def start_translate():
    global music_looped
    if action_start == 'translate':
        progress_text.configure(text='Translate Started')
        des.update()
        des.after(300)
        music_looped = False
        mixer.music.stop()
        mixer.music.load('sound/progress_music.ogg')
        mixer.music.play(-1)
        start_translate_button.configure(state='disabled')
        lang_frame_source_combo.configure(state='disabled')
        lang_frame_target_combo.configure(state='disabled')
        source_file_frame_button.configure(state='disabled')
        target_file_frame_button.configure(state='disabled')
        source_file_frame_textbox.configure(state='disabled')
        target_file_frame_textbox.configure(state='disabled')
        tarnslator_frame_radio_google.configure(state='disabled')
        tarnslator_frame_radio_yandex.configure(state='disabled')
        tarnslator_frame_radio_libre.configure(state='disabled')

        Thread(target=translate_process).start()

main_frame = CTkFrame(des, width=760, height=400, fg_color='#1c1c1c',bg_color='#1c1c1c')

#Основной фрейм с файлами и прогрессами
source_file_frame = CTkFrame(main_frame, width=720, height=60, fg_color='#2e2e2e')
source_file_frame_header = CTkLabel(source_file_frame, text='Source file:', text_color='white', font=('Arial', 15))
source_file_frame_header.place(x=20,y=1)
source_file_frame_textbox = CTkEntry(source_file_frame, width=600, height=20, text_color='white', bg_color='#2e2e2e', fg_color="#2e2e2e", font=('Arial', 17))
source_file_frame_textbox.place(x=10, y=25)
source_file_frame_button = CTkButton(source_file_frame, text='File', height=30, width=90, text_color='white', bg_color='#1c1c1c', fg_color='#1c1c1c', hover_color='grey', font=('Arial', 15), command=change_source_lang)
source_file_frame_button.place(x=620, y=25.5)

target_file_frame = CTkFrame(main_frame, width=720, height=60, fg_color='#2e2e2e')
target_file_frame_header = CTkLabel(target_file_frame, text='Target file:', text_color='white', font=('Arial', 15))
target_file_frame_header.place(x=20,y=1)
target_file_frame_textbox = CTkEntry(target_file_frame, width=600, bg_color='#2e2e2e', fg_color="#2e2e2e", height=20, text_color='white', font=('Arial', 17))
target_file_frame_textbox.place(x=10, y=25)
target_file_frame_button = CTkButton(target_file_frame, text='File', height=30, width=90, text_color='white', bg_color='#1c1c1c', fg_color='#1c1c1c', hover_color='grey', font=('Arial', 15), command=change_target_lang)
target_file_frame_button.place(x=620, y=25.5)

source_file_frame.place(x=20, y=20)
target_file_frame.place(x=20, y=100)

lang_frame = CTkFrame(main_frame, width=350, height=100, bg_color='#2e2e2e', fg_color="#2e2e2e")
lang_frame_header = CTkLabel(lang_frame, text='Language', text_color='white', font=('Arial', 15))
lang_frame_header.place(x=20,y=1)

lang_frame_source_file = CTkLabel(lang_frame, text='Source language:', text_color='white', font=('Arial', 15))
lang_frame_source_file.place(x=10,y=30)
lang_frame_source_combo = CTkComboBox(lang_frame, text_color='white', bg_color='#2e2e2e', fg_color='#2e2e2e', width=190, values=list(LANGUAGES.keys()), variable=StringVar(lang_frame, value='en'), font=('Arial', 15))
lang_frame_source_combo.place(x=135,y=31)

lang_frame_target_file = CTkLabel(lang_frame, text='Target language:', text_color='white', font=('Arial', 15))
lang_frame_target_file.place(x=10,y=65)
lang_frame_target_combo = CTkComboBox(lang_frame, text_color='white', bg_color='#2e2e2e', fg_color='#2e2e2e', width=190, values=list(LANGUAGES.keys()), variable=StringVar(lang_frame, value='ru'), font=('Arial', 15))
lang_frame_target_combo.place(x=135,y=66)
lang_frame.place(x=20, y=175)


tarnslator_frame = CTkFrame(main_frame, width=350, height=100, bg_color='#2e2e2e', fg_color="#2e2e2e")
translator_api = IntVar(tarnslator_frame, value=0)

tarnslator_frame_header = CTkLabel(tarnslator_frame, text='Translate API', text_color='white', font=('Arial', 15))
tarnslator_frame_header.place(x=130,y=1)

tarnslator_frame_radio_google = CTkRadioButton(tarnslator_frame, text='Google', text_color='white', font=('Arial', 20), fg_color='white', value=0, variable=translator_api, hover_color='grey')
tarnslator_frame_radio_google.place(x=15, y=50)

tarnslator_frame_radio_yandex = CTkRadioButton(tarnslator_frame, text='Yandex', text_color='white', font=('Arial', 20), fg_color='white', value=1, variable=translator_api, hover_color='grey')
tarnslator_frame_radio_yandex.place(x=125, y=50)

tarnslator_frame_radio_libre = CTkRadioButton(tarnslator_frame, text='Libre', text_color='white', font=('Arial', 20), fg_color='white', value=2, variable=translator_api, hover_color='grey')
tarnslator_frame_radio_libre.place(x=240, y=50)
tarnslator_frame.place(x=390, y=175)


progress_header = CTkLabel(main_frame, text='Translate Progress:', text_color='white', font=('Arial', 15))
progress_header.place(x=20,y=300)
progress_text = CTkLabel(main_frame, text='Ready', text_color='white', font=('Arial', 15))
progress_text.place(x=335,y=300)
progress_var = IntVar(main_frame, value=0)
progress_progressbar = CTkProgressBar(main_frame, progress_color='white', fg_color='#2e2e2e', variable=progress_var, width=600, height=10)
progress_progressbar.place(x=20, y=330)
start_translate_button = CTkButton(main_frame, text='Translate!', height=30, width=100, text_color='white', bg_color='#2e2e2e', fg_color='#2e2e2e', hover_color='grey', font=('Arial', 15), command=start_translate)
start_translate_button.place(x=630, y=310)

#Логи
log_frame = CTkFrame(des, width=760, height=400, fg_color="#3A3838",bg_color="#353535")
log_textbox = CTkTextbox(log_frame, width=720, height=360, bg_color='#2e2e2e', fg_color="#1c1c1c", text_color='white', font=('Arial', 20))
log_textbox.place(x=20,y=20)


option_frame = CTkFrame(des, width=140, height=50, fg_color='black', bg_color='black')
log_button = CTkButton(option_frame, text='Log', height=50, width=50, text_color='white', bg_color='black', fg_color='black', hover_color='#2e2e2e', font=('Arial', 20), command=clopen_log)
log_button.place(x=0, y=0)

vol_button = CTkButton(option_frame, text='Volume', height=50, width=50, text_color='white', bg_color='black', fg_color='black', hover_color='#2e2e2e', font=('Arial', 20), command=clopen_volume)
vol_button.place(x=60, y=0)

#Настройка громкости
setvol_frame = CTkFrame(des, width=760, height=400, fg_color="#3A3838",bg_color="#353535")
setvol_content = CTkFrame(setvol_frame, width=720, height=360, bg_color='#2e2e2e', fg_color="#1c1c1c")
setvol_content.place(x=20,y=20)

background_volume_var = IntVar(setvol_content, backsound_volume)
sfx_volume_var = IntVar(setvol_content, sfx_volume)

setvol_background_music = CTkLabel(setvol_content, text='Background music volume:', text_color='white', font=('Arial', 20))
setvol_background_music.place(x=250, y=15)
setvol_background_music_int = CTkLabel(setvol_content, text=backsound_volume, text_color='white', font=('Arial', 20))
setvol_background_music_int.place(x=500, y=15)
setvol_background_music_slider = CTkSlider(setvol_content, width=700, height=25, progress_color='white', variable=background_volume_var, button_color='#1c1c1c', button_hover_color='grey', command=change_background_volume)
setvol_background_music_slider.place(x=12.5, y=45)

setvol_effect_music = CTkLabel(setvol_content, text='Effect music volume:', text_color='white', font=('Arial', 20))
setvol_effect_music.place(x=270, y=80)
setvol_effect_music_int = CTkLabel(setvol_content, text=sfx_volume, text_color='white', font=('Arial', 20))
setvol_effect_music_int.place(x=500, y=80)
setvol_effect_music_slider = CTkSlider(setvol_content, width=700, height=25, progress_color='white', button_color='#1c1c1c', variable=sfx_volume_var, button_hover_color='grey', command=change_effect_volume)
setvol_effect_music_slider.place(x=12.5, y=120)

des.after(1000, lambda: option_frame.place(x=610, y=440))
des.after(1000, lambda: main_frame.place(x=20,y=20))

if platform.system() == 'Windows':
    des.iconbitmap('images/logo.ico')
elif platform.system() == 'Linux':
    icon = PhotoImage(file='images/logo.png')
    des.iconphoto(False, icon)

des.protocol("WM_DELETE_WINDOW", lambda: os._exit(2))

des.mainloop()
