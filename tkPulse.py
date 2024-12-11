import tkinter as tk
import customtkinter as Ctk
from customtkinter import *
from CTkMessagebox import CTkMessagebox
import cv2
import time
from PIL import Image, ImageTk
from fer import FER
from lib.interface import plotXY
from lib.processors_noopenmdao import findFaceGetPulse
from tkinter import filedialog
from datetime import datetime

udp = None
serial = None
baud = None
send_serial = False
send_udp = False
start_counter = False
if serial:
    send_serial = True
previous, count_result = -1, False
counter_angry, counter_disgust = 0, 0
counter_surprise, counter_neutral = 0, 0
counter_fear, counter_happy = 0, 0
selected_cam, counter_sad = 0, 0
count_frequency, bpm = 0, 0
index, count_pressed = -1, 0
w, h = 0, 0

if not baud:
    baud = 9600
else:
    baud = int(baud)
    serial = Serial(port=serial, baudrate=baud)

if udp:
    send_udp = True
    if ":" not in udp:
        ip = udp
        port = 5005

    else:
        ip, port = udp.split(":")
        port = int(port)
    udp = (ip, port)

emotions_frame = []
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]  # Создаем массив с эмоциями
ru_emotions = ["Злость", "Отвращение", "Страх", "Радость", "Грусть", "Удивление", "Нейтрально"]  # Переводим на русский
emotions_labels = []
procents_labels = []
count_ems = []
array_emotion = []
cap = cv2.VideoCapture(0)
emotion_detector = FER(mtcnn=True)  # Нейронная сеть

# def open_window_one():
#     window_one = ctk.CTk()
#     window_one.title("Window One")
#     window_one.geometry("300x200")
#     ctk.CTkLabel(window_one, text="This is Window One").pack(pady=20, padx=20)
#     window_one.mainloop()


def open_web():  # Переключение на камеру
    global cap, selected_cam
    cap = cv2.VideoCapture(0)


def open_webs():  # Переключение на невстроенную камеру
    global cap, selected_cam
    cap = cv2.VideoCapture(1)


def countdown(count):  # Функиция которая оперделяет средние значние эмоции и пульса
    global bpm, start_counter, count_ems, count_pressed, count_result
    global counter_happy, counter_neutral, counter_fear, counter_surprise, counter_sad, counter_angry, counter_disgust
    global count_pressed
    start_counter = True
    if count >= 0:
        bpm += processor.bpm
        label_window.configure(text=f"Осталось {count} секунд")
        window_emotions_and_buttons.after(1000, countdown, count - 1)
    else:
        label_window.configure(text=f'')
        start_counter = False
        ind = count_ems.index(max(count_ems))
        label_window_pulse.configure(text=f'{bpm // 5}')
        print()
        for j in range(len(emotions)):
            if ind == j and (array_emotion[j] == "angry" or array_emotion[j] == 'disgust'
                             or array_emotion[j] == "sad") and bpm > 78:
                count_result = True
            procents_labels[j]["foreground"] = "#c31b1c" if j == ind else "white"
            emotions_labels[j]["foreground"] = "#c31b1c" if j == ind else "white"
            emotions_labels[j]["text"] = ru_emotions[j]
            procents_labels[j]["text"] = f'{count_ems[j] * 100 / count_pressed: .0f}%'
        count_ems = []
        bpm = 0
        count_pressed = 0
        counter_happy = counter_neutral = counter_fear = counter_surprise = counter_sad = counter_angry = counter_disgust = 0
        if count_result:
            CTkMessagebox(
                title="Предупреждение",
                message="В группе риска",
                icon="cancel",
                button_color="#c31b1c",
                button_hover_color='#9d0c0d',
                font=("emoji", 16, "bold"),
            )
            count_result = False
        else:
            CTkMessagebox(
                title="Уведомление",
                message="Состояние стабильное",
                icon="check",
                button_color="#61b831",
                button_hover_color='#478a22',
                font=("emoji", 16, "bold"),
            )


def key_handler():
    cv2.waitKey(10) & 255


def restart(self):
    self.refresh()
    self.controller.show_frame("StartPage")


def toggle_display_plot():
    if processor.find_faces:
        state = processor.find_faces_toggle()
    make_bpm_plot()


def make_bpm_plot():
    plotXY(
        [[processor.times, processor.samples], [processor.freqs, processor.fft]],
        labels=[False, True],
        showmax=[False, "bpm"],
        label_ndigits=[0, 0],
        showmax_digits=[0, 1],
        skip=[3, 3],
        bg=processor.slices[0],
    )


def open_file():  # Загружаем видео
    global cap, selected_cam
    filepath = filedialog.askopenfilename()
    cap = cv2.VideoCapture(f'{filepath}')


processor = findFaceGetPulse(
    bpm_limits=[70, 160],
    data_spike_limit=2500.0,
    face_detector_smoothness=10.0
)


def Pulse():
    timee = datetime.now()
    ret, frame = cap.read()
    if ret:
        processor.frame_in = frame
        processor.run(selected_cam)
        toggle_display_plot()
        key_handler()


app = Ctk.CTk()  # Создаем окно Ctk
app.title('Tkinter.com - CustomTkinter Light Dark Modes')
width = app.winfo_screenwidth()
width_indent = width / 2.7
height = app.winfo_screenheight()
app.geometry("%dx%d" % (width, height))  # Растягиваем его на весь экран

window_primary = Ctk.CTkFrame(app)
window_secondary = Ctk.CTkFrame(app)

window_menu = Ctk.CTkFrame(  # Создаем верхнее меню
    app,
    width=width,
    fg_color="#c31b1c",
)
window_menu.pack(side=TOP)

window_menu_text = Ctk.CTkLabel(  # Пишем в нем текст
    window_menu,
    width=width,
    text="Детектор состояния человека",
    font=("emoji", 35, "bold"),
)
window_menu_text.pack(side=LEFT, pady=15)

window_footer = Ctk.CTkFrame(  # Cоздаем нижнее меню
    app,
    width=width,
    height=60,
    fg_color="#c31b1c",
)
window_footer.pack(side=BOTTOM)

window_footer_text = Ctk.CTkLabel(  # Пишем в нем текст
    window_footer,
    text="Российские железные дороги",
    text_color="white",
    width=width,
    font=("emoji", 25, "bold"),
)
window_footer_text.pack(side=LEFT, pady=5)

window_menu_download = Ctk.CTkFrame(  # Создаем левое меню с видео
    app,
    width=250,
    height=800,
    fg_color="gray13",
)
window_menu_download.pack(side=LEFT, padx=100, pady=20)

window_web = Ctk.CTkFrame(  # Добавляем фон для видео
    window_menu_download,
    width=200,
    height=300,
)
window_web.pack(side=TOP, padx=20, pady=40)

label = tk.Label(
    window_web,
    width=600,
    height=400,
)
label.pack()

window_download = Ctk.CTkButton(  # Добавляем кнопку для загрузки
    window_menu_download,
    width=360,
    height=40,
    text="Загрузить видео",
    fg_color="gray33",
    hover_color="gray43",
    font=("Arial", 20, "bold"),
    command=open_file,
)
window_download.pack(pady=10, ipadx=2, ipady=1)

window_open_web = Ctk.CTkButton(  # Добавляем кнопку для загрузки
    window_menu_download,
    width=360,
    height=40,
    text="Открыть встроенную веб-камерy",
    fg_color="gray33",
    hover_color="gray43",
    font=("Arial", 20, "bold"),
    command=open_web,
)
window_open_web.pack(pady=20, ipadx=2, ipady=1)

window_open_web_pulse = Ctk.CTkButton(  # Добавляем кнопку для загрузки
    window_menu_download,
    width=360,
    height=40,
    text="Открыть невстроенную веб-камерy",
    fg_color="gray33",
    hover_color="gray43",
    font=("Arial", 20, "bold"),
    command=open_webs,
)
window_open_web_pulse.pack(pady=(10, 20), ipadx=2, ipady=1)

window_emotions_and_buttons = Ctk.CTkFrame(  # Создаем меню с эмоциями и кнопками
    app,
    width=300,
    height=700,
    fg_color="gray13",
)
window_emotions_and_buttons.pack(side=RIGHT, padx=70, pady=70)

page_one = Ctk.CTkFrame(window_emotions_and_buttons)

text_emotion = Ctk.CTkLabel(
    window_emotions_and_buttons,
    text='Ваши средние эмоции',
    font=("Arial", 25, "bold"),
)
text_emotion.pack(side=TOP, pady=(20, 0))

button_start = Ctk.CTkButton(
    window_emotions_and_buttons,
    width=320,
    height=55,
    text="Определить состояние",
    fg_color="gray33",
    hover_color="gray43",
    font=("Arial", 25, "bold"),
    command=lambda: countdown(5),
)
button_start.pack(side=BOTTOM, padx=20, pady=20)

label_window = Ctk.CTkLabel(
    window_emotions_and_buttons,
    text="",
)
label_window.pack(side=BOTTOM, padx=10, pady=10)

text_pulse = Ctk.CTkLabel(
    window_emotions_and_buttons,
    text="Ваш средний пульс",
    font=("Arial", 25, "bold"),
)
text_pulse.pack(side=BOTTOM)

label_window_pulse = Ctk.CTkLabel(
    window_emotions_and_buttons,
    text="",
    font=("Arial", 15, "bold")
)
label_window_pulse.pack(side=BOTTOM, padx=10, pady=10)

window_emotions = Ctk.CTkFrame(  # Создаем меню с эмоциями
    window_emotions_and_buttons,
    width=300,
    height=800,
    fg_color="gray13",
)
window_emotions.pack(side=TOP, pady=30, padx=20)

for i in range(len(emotions)):
    emotions_frame.append(Ctk.CTkFrame(window_emotions))
    emotions_frame[i]["height"] = 400
    emotions_frame[i]["width"] = 300
    emotions_frame[i].pack(side=TOP, padx=5, pady=5)
for i in range(len(emotions)):
    emotions_labels.append(tk.Label(emotions_frame[i]))
    emotions_labels[i]["font"] = ("Arial", 20, "bold")
    emotions_labels[i]["background"] = "gray17"
    emotions_labels[i]["foreground"] = "red" if i == index else "white"
    emotions_labels[i]["width"] = 10
    emotions_labels[i].pack(side=LEFT, padx=(40, 350))


def updateFrame():  # Пишем эмоции
    global cap, index, counter_angry, counter_disgust, counter_fear, counter_happy, counter_sad, previous
    global counter_surprise, counter_neutral, count_ems, count_pressed, array_emotion

    ret, frame = cap.read()
    start_timee = datetime.now()
    if ret:
        frame = cv2.resize(frame, (600, 400))  # Уменьшенный размер
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)
        captured_emotions = emotion_detector.detect_emotions(img)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        for _ in range(len(captured_emotions)):
            for j in range(len(emotions)):
                str_emotions = str(emotions[j])
                array_emotion.append(str_emotions)
                if start_counter:  # Определяем среднее значение всех эмоций
                    if str_emotions == "angry":
                        counter_angry += captured_emotions[0]["emotions"][str_emotions]
                        count_pressed += 1
                    if str_emotions == "disgust":
                        counter_disgust += captured_emotions[0]["emotions"][str_emotions]
                    if str_emotions == "fear":
                        counter_fear += captured_emotions[0]["emotions"][str_emotions]
                    if str_emotions == "happy":
                        counter_happy += captured_emotions[0]["emotions"][str_emotions]
                    if str_emotions == "sad":
                        counter_sad += captured_emotions[0]["emotions"][str_emotions]
                    if str_emotions == "surprise":
                        counter_surprise += captured_emotions[0]["emotions"][str_emotions]
                    if str_emotions == "neutral":
                        counter_neutral += captured_emotions[0]["emotions"][str_emotions]
                if previous < captured_emotions[0]["emotions"][str_emotions]:  # Определяем эмоцию, которая выделяется
                    index = j
                    previous = captured_emotions[0]["emotions"][str_emotions]
            for j in range(7):
                procents_labels.append(tk.Label(emotions_frame[j]))
                procents_labels[j]["font"] = ("Arial", 20, "bold")
                procents_labels[j]["background"] = "gray17"
                procents_labels[j]["width"] = 40
                procents_labels[j].pack(side=RIGHT, padx=0)

        if start_counter:
            count_ems = [counter_angry, counter_disgust, counter_fear, counter_happy, counter_sad, counter_surprise,
                         counter_neutral]
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
    app.after(50, Pulse)
    app.after(50, updateFrame)


window_emotions_secondary = Ctk.CTkFrame(  # Создаем меню с эмоциями
    window_secondary,
    width=300,
    height=800,
    fg_color="gray13",
)
window_emotions.pack(side=TOP, pady=30, padx=20)

for i in range(len(emotions)):
    emotions_frame.append(Ctk.CTkFrame(window_emotions_secondary))
    emotions_frame[i]["height"] = 400
    emotions_frame[i]["width"] = 300
    emotions_frame[i].pack(side=TOP, padx=5, pady=5)
for i in range(len(emotions)):
    emotions_labels.append(tk.Label(emotions_frame[i]))
    emotions_labels[i]["font"] = ("Arial", 20, "bold")
    emotions_labels[i]["background"] = "gray17"
    emotions_labels[i]["foreground"] = "red" if i == index else "white"
    emotions_labels[i]["width"] = 10
    emotions_labels[i].pack(side=LEFT, padx=(40, 350))


# def updateFrame():  # Пишем эмоции
#     global cap, index, counter_angry, counter_disgust, counter_fear, counter_happy, counter_sad, previous
#     global counter_surprise, counter_neutral, count_ems, count_pressed, array_emotion
#
#     ret, frame = cap.read()
#     start_timee = datetime.now()
#     if ret:
#         frame = cv2.resize(frame, (600, 400))  # Уменьшенный размер
#         img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#         faces = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)
#         captured_emotions = emotion_detector.detect_emotions(img)
#         for (x, y, w, h) in faces:
#             cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         for _ in range(len(captured_emotions)):
#             for j in range(len(emotions)):
#                 str_emotions = str(emotions[j])
#                 array_emotion.append(str_emotions)
#                 if start_counter:  # Определяем среднее значение всех эмоций
#                     if str_emotions == "angry":
#                         counter_angry += captured_emotions[0]["emotions"][str_emotions]
#                         count_pressed += 1
#                     if str_emotions == "disgust":
#                         counter_disgust += captured_emotions[0]["emotions"][str_emotions]
#                     if str_emotions == "fear":
#                         counter_fear += captured_emotions[0]["emotions"][str_emotions]
#                     if str_emotions == "happy":
#                         counter_happy += captured_emotions[0]["emotions"][str_emotions]
#                     if str_emotions == "sad":
#                         counter_sad += captured_emotions[0]["emotions"][str_emotions]
#                     if str_emotions == "surprise":
#                         counter_surprise += captured_emotions[0]["emotions"][str_emotions]
#                     if str_emotions == "neutral":
#                         counter_neutral += captured_emotions[0]["emotions"][str_emotions]
#                 if previous < captured_emotions[0]["emotions"][str_emotions]:  # Определяем эмоцию, которая выделяется
#                     index = j
#                     previous = captured_emotions[0]["emotions"][str_emotions]
#             for j in range(7):
#                 procents_labels.append(tk.Label(emotions_frame[j]))
#                 procents_labels[j]["font"] = ("Arial", 20, "bold")
#                 procents_labels[j]["background"] = "gray17"
#                 procents_labels[j]["width"] = 40
#                 procents_labels[j].pack(side=RIGHT, padx=0)
#
#         if start_counter:
#             count_ems = [counter_angry, counter_disgust, counter_fear, counter_happy, counter_sad, counter_surprise,
#                          counter_neutral]
#         img = Image.fromarray(img)
#         imgtk = ImageTk.PhotoImage(image=img)
#         label.imgtk = imgtk
#         label.configure(image=imgtk)
#     app.after(50, Pulse)
#     app.after(50, updateFrame)



updateFrame()
app.mainloop()
