# pimometre
Mini station météo de salon connecté équipée d'un capteur de température et d'humidité pour la température ambiante.
Récupération de prévisions météorologiques via une API Rest. 
Les données sont affichées sur un petit écran LCD de 2 lignes de 16 caractères.


## prototype de test avec capteur et écran LCD

#### choix matériel

* Raspberry pi Zero WH avec Raspbian os lite et WIFI
* 1 capteur température et humidité: DHT22 (précision T°: 0.5°C, précision humidité: 5%)
* 1 résistance 4,7 k ohms
* 1 écran LCD 16*2 avec backpack I2C à base de PCF8574

![fritzing_prototype_test](_docs/pimometre_test_fritzing.png)

#### test capteur DHT22

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

Les deux fichiers sont à déposer dans un répertoire /home/pi/pimometre/tests/ du raspberry pi zero.

usage: 
```bach
python3 pimometre/tests/test_LCD_dht22.py
```

#### test API météo

Pour récupérer les prévisions météorologiques locales, il faut d'abord créer un token "standard" sur https://api.meteo-concept.com/

Récupérer votre token, et stockez le dans un fichier texte "tokenAPI.txt", à déposer dans le dossier /home/pimometre/tests, ainsi que le programme python test_meteo_api.py à récupérer parmi les sources.

usage:
```python
cd pimometre/tests
python3 test_meteo_api.py [CP] 
```
en remplaçant [CP] par un code postal dont vous souhaitez les prévisions météo
![test_api](_docs/Capture_test_api.png)

Pour un même code postal il peut y avoir plusieurs villes: identifiez le code INSEE de la ville pour laquelle vous souhaitez avoir les prévisions météo: ce code sera utilisé pour la suite du projet.

#### première version test du projet: météo interne (capteur) et externe (api).

le programme **pimometre_v1.1.py** dans le répertoire **/tests** permet d'afficher la météo interne capté par le capteur DHT22 (T° et taux d'humidité), ainsi que la température et taux d'humidité exterieure fournie par l'API.

usage: 
```python
cd pimometre/tests
python3 pimometre_v1.1.py [INSEE]
```

remplacer [INSEE] par le code INSEE de votre ville (récupérée via le programme **test_meteo_api.py**) 
![test_v1.1](_docs/pimometre_v1.1.jpg)

Pour pouvoir afficher des informations asynchrones sur un écran (LCD 16*2 en l'occurence), la meilleure solution est de confier la lecture des capteurs à des Threads indépendants. L'application principale consiste à afficher en boucle infinie avec un temps de repos pour ne pas saturer les processeurs ce que les Threads de lecture ont enregistrés la dernière fois qu'ils ont capté quelquechose. Grâce aux Threads On peut ainsi afficher de manière régulière des informations captées par des capteurs qui ne sont absolument pas synchronisés.

Ce programme (orienté objet) contient 3 classes pour gérer l'application:
* Classe **Application**, avec sa boucle principale **loop()** qui affiche en boucle infinie toutes les 2 secondes sur l'écran LCD les lectures faites par le DHT22 et l'appel à l'API météo.
* Classe **DHT22**: capteur interne de T° et humidité. Ce capteur est capricieux et provoque souvent des erreurs de lecture qu'il faut ignorer, et il est conseillé d'attendre au minimum 2 secondes avant de retenter une lecture: un Thread qui lit et enregistre en boucle infinie ce capteur toutes les 2 secondes est particulièrement bien adapté.
* Classe **Meteo**: Thread de lecture de prévision météo via l'api https://api.meteo-concept.com. Ce thread va interroger l'API toutes les 15 mn (60*15 secondes) pour enregistrer la T° et le taux d'humidité de la ville correspondant au code [INSEE] fourni en paramètre lors de l'appel au programme. Attention l'appel à cette API nécessite que vous aillez au préalable **déclaré votre propre token dans le fichier de configuration tokenAPI.txt**

Une seconde version du programme **pimometre_v1.2.py** va permettre de faire défiler plusieurs informations sur la ligne des prévisions météos: température et humidité extérieure, puis vitesse du vent et probabilité de pluie, et enfin le buletin météo qui apparaît en scrolling de la droite vers la gauche.

## projet complet

#### matériel nécessaire

* 1 Raspberry pi Zero WH avec Raspbian os lite et WIFI
* 1 capteur température et humidité: DHT22 (précision T°: 0.5°C, précision humidité: 5%)
* 1 résistance 4,7 k ohms
* 1 écran LCD 16*2 avec backpack I2C à base de PCF8574
* 2 condensateur céramique 100nf
* 4 résistance 10 k ohms
* 2 bouton poussoirs 6mm 4 pattes
* 1 jack Barrel DC
* 1 barette femelle 2*20pin pas 2,54mm pour raspberry pi
* 1 connecteur 4 pin header coudé mâle 2,54mm (pour brancher le LCD)
* 1 connecteur 3 pin header coudé mâle 2,54mm (popur brancher le capteur DHT22)
* des câbles dupond souples femelle/femelle pour racorder le LCD et le DHT22 à la carte
* un jeux d'entretoises nylons M2.5 pour fixer le LCD et surélever le PCB.

![fritzing_prototype](_docs/pimometre_fritzing.png)

#### circuit imprimé

utilisez le fichier zippé **GERBER_pimometre.zip** pour commander le circuit imprimé auprès de n'importe quel fabriquant de PCB.
Vous pourrez y souder tous les composants: les indications claires sont sérigraphiées.
Le raspberry pi se loge par dessous le PCB.
Le LCD et le DHT22 sont connectés à la carte avec des cables souple femelle/femelle qui se retrouvent entre le circuit imprimé et l'afficheur LCD. 
Il est important de maintenir le capteur DHT22 éloigné du système, pour ne pas que la chaleur dégagée par le raspberry ne perturbe les mesures.

![PCB_3D](_docs/kicad_pimometre_3D_recto.jpg)

#### installation du programme python

Dans le répertoire **/home/pi/pimometre** déposer le fichier **tokenAPI.txt** et **pymometre.py** 
Il faut enregistrer son propre token déclarés préalablement dans https://api.meteo-concept.com/ dans le fichier tokenAPI.txt
Installez bien toutes les dépendances comme expliqué dans la partie tests.




