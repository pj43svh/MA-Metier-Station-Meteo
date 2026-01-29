# Guide Utilisateur - Station Météo

**Auteur:** Amin Torrisi
**Équipe:** CPNV
**Version:** 3.0
**Date:** Janvier 2026

---

Bienvenue dans le guide d'utilisation de la Station Météo ! Ce document vous accompagne pas à pas pour consulter les données météo, configurer vos capteurs et résoudre les problèmes courants.

---

## Table des Matières

1. [Présentation](#1-présentation)
2. [Accès à l'application](#2-accès-à-lapplication)
3. [Le Dashboard](#3-le-dashboard)
4. [Les Graphiques](#4-les-graphiques)
5. [L'Historique](#5-lhistorique)
6. [Configuration d'un capteur ESP32](#6-configuration-dun-capteur-esp32)
7. [Administration des capteurs](#7-administration-des-capteurs)
8. [Dépannage](#8-dépannage)
9. [Informations techniques](#9-informations-techniques)

---

## 1. Présentation

La Station Météo est un système de surveillance environnementale qui mesure en temps réel :
- **Température** (en °C)
- **Humidité** (en %)
- **Pression atmosphérique** (en hPa)

Les données sont collectées par des capteurs ESP32 et transmises à un serveur central accessible via un navigateur web.

---

## 2. Accès à l'application

### Serveur distant (Railway)

Ouvrez votre navigateur et accédez à :

```
https://nurturing-achievement-production.up.railway.app
```

### Serveur local (Raspberry Pi)

Si le serveur tourne sur un Raspberry Pi local :

```
http://[IP_DU_RASPBERRY]:5000
```

L'application est compatible avec tous les navigateurs modernes (Chrome, Firefox, Safari, Edge) sur ordinateur, tablette et smartphone.

---

## 3. Le Dashboard

Le Dashboard est la page principale. Il affiche en temps réel les données de chaque capteur.

### Ce que vous voyez

Pour chaque capteur connecté :
- **Nom du capteur** (ex: "Salon", "Extérieur") — configurable dans l'admin
- **Température** actuelle
- **Humidité** actuelle
- **Pression** atmosphérique actuelle
- **Indicateur de statut** (pastille colorée)

### Indicateurs de statut

| Pastille | Signification |
|----------|---------------|
| Verte (pulsante) | En ligne — données reçues il y a moins de 2 minutes |
| Orange | Récemment actif — données reçues il y a moins de 10 minutes |
| Rouge | Hors ligne — aucune donnée depuis plus de 10 minutes |

Les données se rafraîchissent automatiquement toutes les 20 secondes. Vous n'avez pas besoin de recharger la page.

---

## 4. Les Graphiques

Accessible via le menu **Statistical**.

### Graphiques disponibles

- **Température** : courbe d'évolution sur la journée
- **Humidité** : diagramme en barres
- **Pression** : courbe d'évolution sur la journée

### Sélection de la date

Utilisez le sélecteur de date en haut de la page pour consulter les données d'un jour précis. Par défaut, les graphiques affichent les données du jour en cours.

---

## 5. L'Historique

Accessible via le menu **History**.

L'historique présente un tableau détaillé de toutes les mesures enregistrées, avec :
- Date et heure de chaque mesure
- Température, humidité et pression

Vous pouvez filtrer par date pour retrouver les données d'un jour spécifique.

---

## 6. Configuration d'un capteur ESP32

### Premier démarrage

1. **Branchez l'ESP32** sur une alimentation USB
2. L'ESP32 crée automatiquement un réseau WiFi nommé **StationMeteo-XXXX**
3. La LED clignote = mode configuration

### Connexion au portail

4. Depuis votre téléphone ou ordinateur, connectez-vous au réseau **StationMeteo-XXXX**
5. Un portail de configuration s'ouvre automatiquement
   - Si le portail ne s'ouvre pas, ouvrez manuellement : `http://192.168.4.1`

### Configuration

6. **Réseau WiFi** : sélectionnez votre réseau dans la liste (les réseaux sont scannés automatiquement)
7. **Mot de passe** : entrez le mot de passe de votre réseau WiFi
8. **Adresse du serveur** :
   - Pour le Raspberry Pi : entrez l'adresse IP (ex: `192.168.1.100`)
   - Pour Railway : entrez `nurturing-achievement-production.up.railway.app`
9. Cliquez **Sauvegarder et connecter**
10. L'ESP32 redémarre et se connecte automatiquement

### Reconfigurer un capteur

Pour changer de réseau WiFi ou de serveur :
- **Maintenez le bouton de l'ESP32 pendant 3 secondes**
- L'ESP32 efface sa configuration et redémarre en mode portail
- Refaites les étapes ci-dessus

---

## 7. Administration des capteurs

### Accès à l'admin

```
https://nurturing-achievement-production.up.railway.app/admin
```

ou en local :

```
http://[IP_RASPBERRY]:5000/admin
```

### Configurer un capteur

1. L'ESP32 apparaît dans la liste avec son adresse MAC
2. Choisissez un **numéro de capteur** (1, 2, 3...)
3. Entrez un **nom personnalisé** (ex: "Salon", "Extérieur", "Bureau")
4. Cliquez **Configurer**

Le nom apparaîtra sur le Dashboard à la place de "Sensor 1".

### Supprimer un capteur

Pour retirer un ESP32 de la liste, cliquez sur le bouton de suppression à côté de l'appareil concerné.

---

## 8. Dépannage

### Problèmes fréquents

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| L'ESP32 ne crée pas le réseau WiFi | Code non flashé ou alimentation insuffisante | Vérifiez le flash, débranchez/rebranchez |
| Le portail captif ne s'ouvre pas | Redirection DNS bloquée | Ouvrez manuellement `http://192.168.4.1` |
| "Hors ligne" sur le dashboard | ESP32 éteint, mauvais WiFi ou mauvaise IP serveur | Vérifiez l'alimentation et la configuration |
| ESP32 connecté mais pas de données | Serveur Flask non démarré | Lancez le serveur (`python main.py`) |
| Graphiques vides | Pas de données pour la date sélectionnée | Changez la date ou vérifiez que le capteur envoie |
| Nom du capteur pas à jour | Cache du navigateur | Rafraîchissez la page (F5) |
| Pastille orange au lieu de verte | Données reçues entre 2 et 10 min | Normal, les données arrivent toutes les 20 sec |
| "connection refused" dans le moniteur série | Serveur non lancé ou mauvaise IP | Vérifiez que Flask tourne sur `0.0.0.0:5000` |

### Changer de réseau WiFi ou de serveur

Maintenez le bouton de l'ESP32 pendant **3 secondes**. L'appareil redémarre en mode portail captif et vous pouvez entrer de nouveaux paramètres.

---

## 9. Informations techniques

| Information | Valeur |
|-------------|--------|
| URL Railway | `nurturing-achievement-production.up.railway.app` |
| Port serveur local | 5000 |
| IP portail ESP32 | 192.168.4.1 |
| Intervalle d'envoi des données | 20 secondes |
| Seuil "en ligne" (vert) | < 2 minutes |
| Seuil "récent" (orange) | < 10 minutes |
| Capteur température/humidité | SHT40 (I2C 0x44) |
| Capteur pression | BMP280 (I2C 0x76 ou 0x77) |

---

## Besoin d'aide ?

Si vous rencontrez des difficultés, consultez les ressources suivantes :

- **GitHub du projet :** https://github.com/pj43svh/MA-Metier-Station-Meteo
- **Trello :** https://trello.com/b/mbKZJSjJ/station-météo-esp32-rpi
- **CPNV :** https://cpnv.ch

---

*Document rédigé par Amin Torrisi - CPNV - Janvier 2026*
