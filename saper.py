import random

WIDTH=800
HEIGHT=600

WYSOKOSC_PASKA = 50

rozmiarX = 16
rozmiarY = 16
liczbaPol = rozmiarX * rozmiarY
# rozmiar pojendycznego pola w pikselach
rozmiarPola = (26, 26)
# rozmiar planszy w pikselach
rozmiarPlanszy = (rozmiarPola[0] * rozmiarX, rozmiarPola[1] * rozmiarY)
polozeniePlanszy = Rect(0, 0, rozmiarX * rozmiarPola[0], rozmiarY * rozmiarPola[1])
polozeniePlanszy.move_ip((WIDTH - rozmiarPlanszy[0]) / 2, 
        WYSOKOSC_PASKA + ((HEIGHT - WYSOKOSC_PASKA) - rozmiarPlanszy[1]) / 2)
polozeniePaska = Rect(polozeniePlanszy.x, 0, polozeniePlanszy.width, WYSOKOSC_PASKA)
# definicja plamszy
plansza = []

# aktualna pozycja kursora
pozycjaKursora = (-1, -1)

# kolory na planszy
KOLOR_POLE_ZAKRYTE = 'grey50'
KOLOR_POLE_ODKRYTE = 'grey75'
KOLOR_OBRAMOWANIA = 'grey60'
KOLOR_KURSORA = 'grey65'

BOMBA = 9
# kolory sasiadow 1 - blue, 2 - green4, ...
kolory = [ 'blue', 'green4', 'red', 'purple4', 'maroon4', 'cyan', 'tan4', 'orchid4', 'black' ]

POLE_ODKRYTE = 128
FLAGA = 64
OBEJRZANE = 32

# czas jaki minal w sekundach
czas = 0

# czy koniec gry
koniecGry = False

# czy wygrana
wygrana = False

# liczba klikniec
liczbaKlikniecLewy = 0
liczbaKlikniecPrawy = 0

# zmienna pomocnicza informujaca ze nastapilo klikniecie
klikniecie = 0

# ikonka informujaca o stanie gry
ikona_usmiech = Actor('grinning_cat', center=polozeniePaska.center)
ikona_usmiech_2 = Actor('grinning_cat_with_smiling_eyes', center=polozeniePaska.center)
ikona_smutek = Actor('pouting_cat', center=polozeniePaska.center)
ikona_usmiech_aktywny = Actor('smiling_cat_with_heart_eyes', center=polozeniePaska.center)
ikona_calus = Actor('kissing_cat', center=polozeniePaska.center)

# wygenerowanie liczby bomb na planszy
liczbaBomb = int(0.15 * rozmiarX * rozmiarY)
liczbaFlag = 0

def aktualizujCzas():
    global czas
    # aktualizacja czasu co jedna sekunde
    czas += 1
    if (czas > 999):
        czas = 999
        stop(False)

def draw():
    screen.fill('black')
    r = polozeniePlanszy.inflate(2, 2)
    for i in range(3):
        screen.draw.rect(r, KOLOR_OBRAMOWANIA)
        r = r.inflate(2, 2)
    
    kursorX = (pozycjaKursora[0] - polozeniePlanszy.x) // rozmiarPola[0]
    kursorY = (pozycjaKursora[1] - polozeniePlanszy.y) // rozmiarPola[1]
    for x in range(0, rozmiarX):
        for y in range(0, rozmiarY):
            r = Rect((x * rozmiarPola[0] + polozeniePlanszy.x, y * rozmiarPola[1] + polozeniePlanszy.y), rozmiarPola)

            kolor = KOLOR_POLE_ODKRYTE if plansza[y][x] & POLE_ODKRYTE else KOLOR_POLE_ZAKRYTE
            if (x == kursorX and y == kursorY):
                kolor = KOLOR_KURSORA

            screen.draw.filled_rect(r, kolor)
            screen.draw.rect(r, KOLOR_OBRAMOWANIA)

            # wyswietlanie zawartosci odkrytych pol
            pole = plansza[y][x] & ~(POLE_ODKRYTE | FLAGA)
            if (plansza[y][x] & POLE_ODKRYTE and pole > 0):
                if (pole < BOMBA):
                    # wyswietla liczbe sasiadow jezeli pole jest odkryte
                    screen.draw.text(str(pole), center=(r.x + r.w / 2, r.y + r.h / 2), 
                        fontsize=0.9 * r.h, color = kolory[pole - 1])
                elif (pole == BOMBA):
                    # wyswietla obrazek bomby jezeli zostala odkryta
                    size = images.bomb.get_size()
                    screen.blit(images.bomb, (r.x + (r.w - size[0]) / 2, r.y + (r.h - size[1]) / 2))

            if (plansza[y][x] & FLAGA):
                size = images.flag_filled.get_size()
                screen.blit(images.flag_filled, (r.x + (r.w - size[0]) / 2, r.y + (r.h - size[1]) / 2))

    screen.draw.text('{:03d}'.format(czas), midright=(polozeniePaska.right, polozeniePaska.centery), 
        fontsize=WYSOKOSC_PASKA, color='red', fontname = 'crashed_scoreboard')
    screen.draw.text('{:03d}'.format(liczbaBomb - liczbaFlag), midleft=(polozeniePaska.left, polozeniePaska.centery),
        fontsize=WYSOKOSC_PASKA, color='red', fontname = 'crashed_scoreboard')

    if (ikona_usmiech_aktywny.collidepoint(pozycjaKursora)):
        ikona_usmiech_aktywny.draw()
    elif (koniecGry):
        if (wygrana):
            ikona_calus.draw()
        else:
            ikona_smutek.draw()
    else:
        if (klikniecie > 0):
            ikona_usmiech_2.draw()
        else:        
            ikona_usmiech.draw()

def update():
    # policz liczbe wszystkich odkrytych pol
    liczbaOdkrytychPol = 0
    liczbaBombzFlaga = 0
    for y in range(0, rozmiarY):
        for x in range(0, rozmiarX):
            liczbaOdkrytychPol += (plansza[y][x] & POLE_ODKRYTE != 0)
            liczbaBombzFlaga += (plansza[y][x] & FLAGA != 0 and plansza[y][x] & ~FLAGA == BOMBA)
    if ((liczbaPol - liczbaOdkrytychPol) == liczbaBomb or liczbaBombzFlaga == liczbaBomb):
        # wygrana
        stop(True)
        odkryjWszystkieBomby()        

    return

def on_mouse_move(pos):
    global pozycjaKursora
    pozycjaKursora = pos

def on_mouse_down(pos, button):
    global liczbaKlikniecLewy, liczbaKlikniecPrawy, klikniecie, liczbaFlag
    if (ikona_usmiech_aktywny.collidepoint(pos) and button == mouse.LEFT):
        stop(False)
        start()
        return

    if (koniecGry):
        return

    x = (pos[0] - polozeniePlanszy.x) // rozmiarPola[0]
    y = (pos[1] - polozeniePlanszy.y) // rozmiarPola[1]
    if (x >= 0 and y >= 0 and x < rozmiarX and y < rozmiarY):        
        klikniecie = 1
                
        if (button == mouse.LEFT):
            liczbaKlikniecLewy += 1
            if (liczbaKlikniecLewy == 1):
                wygenerujPlansze(Rect(x - 1, y - 1, 3, 3))

            if (plansza[y][x] == BOMBA):
                # przegrales
                odkryjWszystkieBomby()
                stop(False)
            elif (plansza[y][x] & POLE_ODKRYTE == 0 and plansza[y][x] & FLAGA == 0):
                # odkryj wszystkie pola o wartosci zero                
                odkryjPola(x, y)
                resetujStatusPol()

        elif (button == mouse.RIGHT and plansza[y][x] & POLE_ODKRYTE == 0):
            liczbaKlikniecPrawy += 1
            if (liczbaFlag < liczbaBomb and plansza[y][x] & FLAGA == 0):
                plansza[y][x] |= FLAGA
                liczbaFlag += 1
            elif (plansza[y][x] & FLAGA):
                plansza[y][x] &= ~FLAGA
                liczbaFlag -= 1

def on_mouse_up(pos, button):
    global klikniecie
    klikniecie = 0
            
def odkryjWszystkieBomby():
    for y in range(0, rozmiarY):
        for x in range(0, rozmiarX):
            if (plansza[y][x] & ~FLAGA == BOMBA):
                plansza[y][x] |= POLE_ODKRYTE

def odkryjPola(x, y):
    if (x < 0 or x >= rozmiarX or y < 0 or y >= rozmiarY):
        return

    if (plansza[y][x] & (POLE_ODKRYTE | OBEJRZANE)):
        return
        
    pole = plansza[y][x] & ~FLAGA
    if (pole > 0):        
        if (pole < BOMBA):
            if (plansza[y][x] & FLAGA == 0):
                plansza[y][x] |= POLE_ODKRYTE
            plansza[y][x] |= OBEJRZANE
        return

    if (plansza[y][x] & FLAGA == 0):
        plansza[y][x] |= POLE_ODKRYTE
    plansza[y][x] |= OBEJRZANE

    odkryjPola(x + 1, y)
    odkryjPola(x - 1, y)
    odkryjPola(x, y + 1)    
    odkryjPola(x, y - 1)

def resetujStatusPol():
    for y in range(0, rozmiarY):
        for x in range(0, rozmiarX):
            plansza[y][x] &= ~OBEJRZANE

def zerujPlansze():
    global plansza
    # utworzenie planszy
    # wartosc 9 oznacza bombe
    # wartosc 0-8 oznacza liczbe sasiadujacych bomb
    # powyzsze wartosci powiekszone o 128 oznaczaja pola odkryte
    plansza = [[0]*rozmiarX for i in range(rozmiarY)]

def wygenerujPlansze(poleWykluczone):

    # wygenerowanie bomb na planszy
    i = liczbaBomb
    while(i > 0):
        x = random.randint(0, rozmiarX - 1)
        y = random.randint(0, rozmiarY - 1)
        if (not poleWykluczone.collidepoint(x, y)  and plansza[y][x] & ~FLAGA == 0):
            plansza[y][x] |= BOMBA
            i -= 1

    # wyliczenie sasiadow
    for y in range(0, rozmiarY):
        for x in range(0, rozmiarX):
            if (plansza[y][x] & ~FLAGA != BOMBA):
                liczbaBombSasiednich = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        x1 = x + j
                        y1 = y + i
                        if (x1 >= 0 and y1 >= 0 and x1 < rozmiarX and y1 < rozmiarY):
                            liczbaBombSasiednich += (plansza[y1][x1] & ~FLAGA == BOMBA)
                plansza[y][x] |= liczbaBombSasiednich

def stop(_wygrana):
    global wygrana, koniecGry
    clock.unschedule(aktualizujCzas)
    koniecGry = True
    wygrana = _wygrana

def start():
    global czas, wygrana, koniecGry, liczbaFlag, liczbaKlikniecLewy, liczbaKlikniecPrawy
    czas = 0
    wygrana = False
    koniecGry = False
    liczbaFlag = 0
    liczbaKlikniecLewy = 0
    liczbaKlikniecPrawy = 0

    zerujPlansze()

    clock.schedule_interval(aktualizujCzas, 1.0)

start()


