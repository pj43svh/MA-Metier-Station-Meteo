## 1. Cloner le répertoire git

``` bash
git clone https://github.com/pj43svh/MA-Metier-Station-Meteo.git
```
## 2. Installer les dépendence

vous aurez besoin de :
- Flask
- matplotlib
- Numpy

``` bash
pip install flask
pip install matplotlib
pip install numpy
```

## 3. Modifier le programme pour connecter les différents modules

- Changer les accès internet

    __important__

    ``` C++
    // ==================== CONFIGURATION WiFi ====================
    const char* WIFI_SSID = "Wifi_ssid";
    const char* WIFI_PASSWORD = "wifi_password";

    // ==================== CONFIGURATION Serveur Local (Raspberry Pi) ====================
    const char* RASPBERRY_IP = "10.244.96.106";  // A modifier selon votre Raspberry Pi
    const int RASPBERRY_PORT = 5000;
    const bool USE_LOCAL_SERVER = true;  // Mettre false pour desactiver
    ```

- Le nom de l'appareil connecté
    __Ces chamgement sont optionnels__

    ligne 26
    ``` python
    if name == "Atom_001": # changer avec le nom de votre esp
            name = "esp1"
        elif name == "Atom_002": # pareil ici avec un autre esp
            name = "esp2"
        else :
            print("Wrong device name : ", name)
            return
    ```
    qui doit être identique au C++ :

    ligne 44
    ``` C++
    // ==================== CONFIGURATION Capteur ====================
    const char* CAPTEUR_ID = "ATOM_001";  // Identifiant unique de ce capteur
    ```

[<-- retour au début](home)