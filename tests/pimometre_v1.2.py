#!/usr/bin/env python3
# -*- coding: utf-8 -*-
########################################################################
# Filename    : pimometre.py
# Description : station météo de salon avec prévision
# auther      : papsdroid.fr
# creation    : 2020/09/20
# modification: 2020/09/24
########################################################################

import time, board, adafruit_dht,threading,  I2C_LCD_DRIVER
from contextlib import closing
from urllib.request import urlopen
import json, sys, unicodedata


class DHT22(threading.Thread):
    """ classe capteur de t° et humidité DHT22"""
    def __init__(self):
        """ constructeur """
        threading.Thread.__init__(self)  # appel au constructeur de la classe mère Thread
        print("Init capteur DHT22")
        self.dhtDevice = adafruit_dht.DHT22(board.D18) # catpeur T°  humidity DHT22
        self.delay = 10             # delay in s before reading a new mesure
        self.temperature_c = None
        self.humidity = None
        self.start()               # start thread 

    def run(self):
        """ exécution thread: lit T° et humidité du capteur DHT22 toutes les 5 secondes 
            valeurs stockées dans self.temperature_c et self.humidity
        """
        self.etat = True
        while self.etat:
            try:
                self.temperature_c = self.dhtDevice.temperature
                self.humidity = self.dhtDevice.humidity
            except RuntimeError as error:
                #print(error.args[0])
                continue
            except Exception as error:
                #self.dhtDevice.exit()
                continue
            time.sleep(self.delay) #wait at least 2s before reading a new mesure
        self.off()  # free dht22 device

    def off(self):
        """ arrêt thread de lecture T° DHT22 """
        print("DHT22 exit")
        self.dhtDevice.exit()

class Meteo(threading.Thread):
    """ recup données API meto https://api.meteo-concept.com/ 
        thread de prevision météo mis à jour toutes les self.delay secondes 
    """
    def __init__(self, insee=None):
        """ constructeur """
        threading.Thread.__init__(self)  # appel au constructeur de la classe mère Thread
        self.delay = 60*15               # refresh delays in s
        self.insee = insee               # town code insee
        self.t_out = None                # current t° outside
        #-- get token from tokenAPI.txt file --#
        try:
            with open('tokenAPI.txt','r') as f:
                self.mytoken= f.read()
                #print('token="' + self.mytoken + '"')
        except:
            print('Créer un fichier tokenAPI.txt avec le token en 1ere ligne')
            self.mytoken = None
        self.URLAPI =    'https://api.meteo-concept.com/api'
        self.GETHOURS='/forecast/nextHours'
        self.HOURLY='&hourly=false'
        if (self.mytoken is not None and self.insee is not None):
            self.TOKEN  = '?token='+self.mytoken
            self.SEARCH = '&insee='+self.insee
            self.start() # start thread
        self.WEATHER = {
            0: "Soleil",
            1: "Peu nuageux",
            2: "Ciel voilé",
            3: "Nuageux",
            4: "Très nuageux",
            5: "Couvert",
            6: "Brouillard",
            7: "Brouillard givrant",
            10: "Pluie faible",
            11: "Pluie modérée",
            12: "Pluie forte",
            13: "Pluie faible verglaçante",
            14: "Pluie modérée verglaçante",
            15: "Pluie forte verglaçante",
            16: "Bruine",
            20: "Neige faible",
            21: "Neige modérée",
            22: "Neige forte",
            30: "Pluie et neige mêlées faibles",
            31: "Pluie et neige mêlées modérées",
            32: "Pluie et neige mêlées fortes",
            40: "Averses de pluie locales et faibles",
            41: "Averses de pluie locales",
            42: "Averses locales et fortes",
            43: "Averses de pluie faibles",
            44: "Averses de pluie",
            45: "Averses de pluie fortes",
            46: "Averses de pluie faibles et fréquentes",
            47: "Averses de pluie fréquentes",
            48: "Averses de pluie fortes et fréquentes",
            60: "Averses de neige localisées et faibles",
            61: "Averses de neige localisées",
            62: "Averses de neige localisées et fortes",
            63: "Averses de neige faibles",
            64: "Averses de neige",
            65: "Averses de neige fortes",
            66: "Averses de neige faibles et fréquentes",
            67: "Averses de neige fréquentes",
            68: "Averses de neige fortes et fréquentes",
            70: "Averses de pluie et neige mêlées localisées et faibles",
            71: "Averses de pluie et neige mêlées localisées",
            72: "Averses de pluie et neige mêlées localisées et fortes",
            73: "Averses de pluie et neige mêlées faibles",
            74: "Averses de pluie et neige mêlées",
            75: "Averses de pluie et neige mêlées fortes",
            76: "Averses de pluie et neige mêlées faibles et nombreuses",
            77: "Averses de pluie et neige mêlées fréquentes",
            78: "Averses de pluie et neige mêlées fortes et fréquentes",
            100: "Orages faibles et locaux",
            101: "Orages locaux",
            102: "Orages fort et locaux",
            103: "Orages faibles",
            104: "Orages",
            105: "Orages forts",
            106: "Orages faibles et fréquents",
            107: "Orages fréquents",
            108: "Orages forts et fréquents",
            120: "Orages faibles et locaux de neige ou grésil",
            121: "Orages locaux de neige ou grésil",
            122: "Orages locaux de neige ou grésil",
            123: "Orages faibles de neige ou grésil",
            124: "Orages de neige ou grésil",
            125: "Orages de neige ou grésil",
            126: "Orages faibles et fréquents de neige ou grésil",
            127: "Orages fréquents de neige ou grésil",
            128: "Orages fréquents de neige ou grésil",
            130: "Orages faibles et locaux de pluie et neige mêlées ou grésil",
            131: "Orages locaux de pluie et neige mêlées ou grésil",
            132: "Orages fort et locaux de pluie et neige mêlées ou grésil",
            133: "Orages faibles de pluie et neige mêlées ou grésil",
            134: "Orages de pluie et neige mêlées ou grésil",
            135: "Orages forts de pluie et neige mêlées ou grésil",
            136: "Orages faibles et fréquents de pluie et neige mêlées ou grésil",
            137: "Orages fréquents de pluie et neige mêlées ou grésil",
            138: "Orages forts et fréquents de pluie et neige mêlées ou grésil",
            140: "Pluies orageuses",
            141: "Pluie et neige mêlées à caractère orageux",
            142: "Neige à caractère orageux",
            210: "Pluie faible intermittente",
            211: "Pluie modérée intermittente",
            212: "Pluie forte intermittente",
            220: "Neige faible intermittente",
            221: "Neige modérée intermittente",
            222: "Neige forte intermittente",
            230: "Pluie et neige mêlées",
            231: "Pluie et neige mêlées",
            232: "Pluie et neige mêlées",
            235: "Averses de grêle",
            }

    def run(self):
        """ thread start """
        self.etat = True
        while self.etat:
            with closing(urlopen(self.URLAPI+self.GETHOURS+self.TOKEN+self.HOURLY+self.SEARCH)) as f:
                decoded = json.loads(f.read())
                forecast = decoded['forecast']
                #city = decoded['city']
                self.city = decoded['city']['name']
                self.update = decoded['update']
                self.t_out = forecast[0]['temp2m']  # current T° out
                self.h_out = forecast[0]['rh2m']    # current humidity out
                self.wind  = forecast[0]['wind10m'] # wind mean
                self.probarain = forecast[0]['probarain']  # rain probability
                self.weather = forecast[0]['weather']      # weather code
                print('{} prévisions météo de {} (nb:{}) {}'.format(self.update, self.city, len(forecast), self.WEATHER[self.weather]))
            time.sleep(self.delay)

class LCD:
    """ classe gestion du LCD """
    def __init__(self):
        """ constructeur """
        self.lcd =  I2C_LCD_DRIVER.lcd()        # LCD 16*2
        self.lcd.backlight(1)                   # turn LCD backligth on
        fontdata = [ [0b00100,0b01010,0b01010,0b01010,0b11011,0b10111,0b11111,0b01110], #0 = thermometre
                     [0b00000,0b00100,0b11110,0b11111,0b01010,0b01001,0b00100,0b00000], #1 = rain
                     [0b00000,0b00000,0b00100,0b00010,0b11111,0b00010,0b00100,0b00000], #2 = ->
                   ]
        self.lcd.lcd_load_custom_chars(fontdata)

    def off(self):
        """ extinction LCD """
        self.lcd.lcd_clear()     # clear LCD 
        self.lcd.backlight(0)    # turn LCD backligth off

    def display_string(self, s, lig=1, col=0):
        """ display string s at (lig,col) """
        self.lcd.lcd_display_string(s, lig, col)

    def display_char(self, n, lig=1, col=0):
        """ display special char(n) loaded from fontdata at (lig,col) """
        if lig==1:
            self.lcd.lcd_write(0x80+col)  # position lig1 @col
        else:
            self.lcd.lcd_write(0xC0+col)  # position lig2 @col
        self.lcd.lcd_write_char(n)

    def scroll_string(self, s, lig=1, col=0):
        """ scroll string s rigth to left at (lig, col) """
        padding = " " * (16-col)
        padded_s = padding + s
        for i in range(len(padded_s)):
            lcd_text = padded_s[i:(i+16-col)]
            self.lcd.lcd_display_string(lcd_text, lig, col)
            time.sleep(0.3)
            self.lcd.lcd_display_string(padding, lig,col)

class Application:
    """ classe d'application principale """
    def __init__(self):
        print("démarrage pimometre")
        self.dht22 = DHT22()                    # dht22 device (thread)
        self.meteo = Meteo(insee=sys.argv[1])   # meteo API (thread)
        self.lcd = LCD()                        # LCD 16*2

    def destroy(self):
        """ quitter l'appli"""
        print("bye")
        self.lcd.off()     # clear LCD
        #-- stop threads
        self.dht22.etat = False
        self.meteo.etat = False

    def loop(self):
        """ boucle principale de l'appli """
        self.lcd.display_string('In  ...',1)
        self.lcd.display_string('Ex  ...',2)
        self.lcd.display_char(0,1,3) # thermometre symbol
        self.lcd.display_char(0,2,3) # thermometre symbol
        self.lcd.scroll_string("initialisation ...",1,4)
        while True:
            #temperature  inside
            if (self.dht22.temperature_c is not None and self.dht22.humidity is not None):
                self.lcd.display_string("{:.1f}{}C {:.1f}%".format(self.dht22.temperature_c,chr(223),self.dht22.humidity),1,4)
            # meteo outside
            if self.meteo.t_out is not None:
                #temperature 
                self.lcd.display_char(0,2,3) # thermometre symbol
                self.lcd.display_string("{:.1f}{}C {:.1f}%".format(self.meteo.t_out, chr(223), self.meteo.h_out), 2,4)
                time.sleep(2)
                # wind, proba rain
                self.lcd.display_char(1,2,3) # rain symbol
                self.lcd.display_string("{:.0f}km/h {:.1f}%".format(self.meteo.wind, self.meteo.probarain),2,4)
                time.sleep(2)
                # scroll meteo long string
                self.lcd.display_char(2,2,3) # narrow symbol
                s = self.meteo.WEATHER[self.meteo.weather]                     # label correponding to weather code
                s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')    # remove "accent"
                self.lcd.scroll_string(s,2,4)
            else:
                time.sleep(2)

if __name__ == '__main__':
    if len(sys.argv) == 1 :
        print("Iniquez un code INSEE --> usage: python3 pimometre.py [INSEE]")
        exit(0)
    appl=Application()
    try:
        appl.loop()
    except KeyboardInterrupt:  # interruption clavier CTRL-C: appel à la méthode destroy() de appl.
        appl.destroy()


