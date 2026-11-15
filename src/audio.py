import datetime
import random


def sound_alert():
    try:
        import winsound
        check_sound = [
            (1046, 50),
            (1318, 50),
            (1568, 50),
            (2093, 120)
        ]
        for freq, duration in check_sound:
            winsound.Beep(freq, duration)
    except Exception:
        pass


def christmas_melody():
    try:
        import winsound

        jingle_bells = [
            (659, 300), (661, 300), (659, 600), (661, 300), (659, 300), (661, 600),
            (659, 300), (784, 300), (523, 450), (587, 150), (659, 1200),
            (698, 300), (700, 300), (698, 450), (700, 150), (698, 300), (659, 300), (661, 300), (659, 150), (661, 150),
            (784, 300), (786, 300), (698, 300), (587, 300), (523, 1200)
        ]

        we_wish_you = [
            (523, 550), (698, 550), (700, 280), (784, 280), (698, 280), (659, 280),
            (587, 550), (589, 550), (587, 550), (784, 550), (786, 280), (880, 280),
            (784, 280), (698, 280), (659, 550), (523, 550), (525, 550), (880, 550),
            (882, 280), (932, 280), (880, 280), (784, 280), (698, 550), (587, 550),
            (523, 280), (525, 280), (587, 550), (784, 550), (659, 550), (698, 1100)
        ]

        noche_de_paz = [
            (784, 950), (880, 320), (784, 650), (659, 1400),
            (784, 950), (880, 320), (784, 650), (659, 1400),
            (1174, 650), (1176, 650), (987, 1400),
            (1046, 650), (1048, 650), (784, 1400),
            (880, 650), (882, 650), (1046, 950), (987, 320), (880, 650),
            (784, 950), (880, 320), (784, 650), (659, 1400),
            (784, 650), (786, 650), (1174, 950), (987, 320), (1046, 650),
            (1318, 1400), (1046, 650), (784, 650), (587, 650), (523, 1800)
        ]

        christmas_mdy = [jingle_bells, we_wish_you, noche_de_paz]
        choosen_chrmdy = random.choice(christmas_mdy)

        for freq, duration in choosen_chrmdy:
            winsound.Beep(freq, duration)
    except Exception:
        pass


def birthday_melody():
    try:
        import winsound
        notes = [
            (262, 280), (263, 280), (294, 500), (262, 500), (349, 500), (330, 900),
            (262, 280), (263, 280), (294, 500), (262, 500), (392, 500), (349, 900),
            (262, 280), (263, 280), (523, 500), (440, 500), (349, 500), (330, 500), (294, 500),
            (466, 280), (467, 280), (440, 500), (349, 500), (392, 500), (349, 1000)
        ]
        for freq, duration in notes:
            winsound.Beep(freq, int(duration * 1.25))
    except Exception:
        pass


def check_and_play_event_melody(birth_d: int, birth_m: int):
    now = datetime.datetime.now()
    if now.day == birth_d and now.month == birth_m:
        birthday_melody()
    elif now.month == 12:
        christmas_melody()
