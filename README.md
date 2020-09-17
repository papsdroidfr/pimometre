# pimometre
Mini station météo de salon connecté équipée d'un capteur de température et d'humidité pour la température ambiante.
Récupération de prévisions météorologiques via une API Rest. 
Les données sont affichées sur un petit écran LCD de 2 lignes de 16 caractères.


## choix matériel
* Raspberry pi Zero WH avec Raspbian os lite et WIFI
* 1 capteur température et humidité: DHT22 (précision T°: 0.5°C, précision humidité: 5%)
* 1 résistance 4,7 k ohms
* 1 écran LCD 16*2 avec backpack I2C à base de PCF8574


## prototype de tests capteur et écran LCD
![fritzing_prototype_test](_docs/pimometre_test_fritzing.png)

### programmes Python

Il faut tout d'abord activer l'interface I2C du Raspberry pi avec 
```bach
sudo raspi-config
```
reboot nécessaire.

Pour le capteur DHT22, il faut instaler les dépendances et bilbiothèques circuit-python d'Adafruit en suivant [ce guide](https://circuitpython.readthedocs.io/projects/dht/en/latest/)

Pour l'afficheur LCD j'ai récupéré la bilbiothèque I2C_LCD_DRIVER.py que je trouve particulièrement bien faite et complète sur [ce site](https://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/).

Les scripts pythons ci-dessous permettent d'afficher la température et l'humidité ambiante sur le LCD:
* test_LCD_dht22.py
* I2C_LCD_DRIVER.py

Les deux fichiers sont à déposer dans un répertoire /home/pi/tests/ du raspberry pi zero.

usage: 
```bach
python3 /pimometre/tests/test_LCD_dht22.py
```

##test API météo

Pour récupérer les prévisions météorologiques locales, il faut créer un token "standard" sur https://api.meteo-concept.com/

Récupérer votre token et stockez le dans un fichier texte "tokenAPI.txt", à déposer dans le dossier /home/pimometre/tests/ , ainsi que le programme python test_meteo_api.py à récupérer parmi les sources.

usage:
```bach
python3 /pimometre/tests/test_meteo_api.py [CP] 
```
en remplaçant CP par un code postal dont vous souhaitez les prévisions météo 
