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
import json, sys


class DHT22(threading.Thread):
    """ classe capteur de t° et humidité DHT22"""
    def __init__(self):
        """ constructeur """
        threading.Thread.__init__(self)  # appel au constructeur de la classe mère Thread
        print("Init capteur DHT22")
        self.dhtDevice = adafruit_dht.DHT22(board.D18) # catpeur T°  humidity DHT22
        self.delay = 5             # delay in s before reading a new mesure
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
                print(error.args[0])
            except Exception as error:
                self.dhtDevice.exit()
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
                print('token="' + self.mytoken + '"')
        except:
            print('Créer un fichier tokenAPI.txt avec le token en 1ere ligne')
            self.mytoken = None
        self.URLAPI =    'https://api.meteo-concept.com/api'
        self.GETHOURS='/forecast/nextHours'
        self.HOURLY='&hourly=true'
        if (self.mytoken is not None and self.insee is not None):
            self.TOKEN =     '?token='+self.mytoken
            self.SEARCH = '&insee='+self.insee
            self.start() #start thread

    def run(self):
        """ thread start """
        self.etat = True
        while self.etat:
            with closing(urlopen(self.URLAPI+self.GETHOURS+self.TOKEN+self.HOURLY+self.SEARCH)) as f:
                forecast = json.loads(f.read())['forecast']
                if len(forecast)>0:
                    self.t_out = forecast[0]['temp2m'] # current T° out
                    self.h_out = forecast[0]['rh2m']   # current humidity out
            time.sleep(self.delay)

class Application:
    """ classe d'application principale """
    def __init__(self):
        print("démarrage pimometre")
        self.dht22 = DHT22()                    # dht22 device (thread)
        self.meteo = Meteo(insee=sys.argv[1])   # meteo API (thread)
        self.lcd = I2C_LCD_DRIVER.lcd()         # LCD 16*2
        self.lcd.backlight(1)                   # turn LCD backligth on

    def destroy(self):
        print("bye")
        self.lcd.lcd_clear()    # clear LCD
        self.lcd.backlight(0)   # turn LCD backligth off
        #-- stop threads
        self.dht22.etat = False
        self.meteo.etat = False

    def loop(self):
        """ boucle principale de l'appli """
        self.lcd.lcd_display_string("In  ...         ", 1)
        self.lcd.lcd_display_string("Out ...         ", 2)
        while True:
            if (self.dht22.temperature_c is not None and self.dht22.humidity is not None):
                self.lcd.lcd_display_string("In : {:.1f}C {:.1f}%".format(self.dht22.temperature_c,self.dht22.humidity), 1)
            if self.meteo.t_out is not None:
                self.lcd.lcd_display_string("Out: {:.1f}C {:.1f}%".format(self.meteo.t_out, self.meteo.h_out), 2)
            time.sleep(2)

if __name__ == '__main__':
    appl=Application()
    try:
        appl.loop()
    except KeyboardInterrupt:  # interruption clavier CTRL-C: appel à la méthode destroy() de appl.
        appl.destroy()


