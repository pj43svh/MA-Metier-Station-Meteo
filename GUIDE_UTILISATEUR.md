# Guide Utilisateur - Station Météo

**Auteur:** Amin Torrisi
**Équipe:** CPNV
**Version:** 2.0
**Date:** Janvier 2026

---

Bienvenue dans le guide d'utilisation de la Station Météo ! J'ai créé cette documentation pour vous aider à prendre en main l'application rapidement. Vous y trouverez toutes les informations nécessaires pour consulter les données météo, configurer vos capteurs et résoudre les problèmes courants.

---

## Table des Matières

1. [Présentation](#1-présentation)
2. [Accès à l'application](#2-accès-à-lapplication)
3. [Le Dashboard](#3-le-dashboard)
4. [Les Graphiques](#4-les-graphiques)
5. [L'Historique](#5-lhistorique)
6. [Administration des capteurs](#6-administration-des-capteurs)
7. [Questions fréquentes](#7-questions-fréquentes)

---

## 1. Présentation

### Qu'est-ce que la Station Météo ?

La Station Météo est une application web qui permet de visualiser en temps réel les données météorologiques collectées par des capteurs ESP32 :

- **Température** (en °C)
- **Humidité** (en %)
- **Pression atmosphérique** (en hPa)

L'application est accessible depuis n'importe quel navigateur web (ordinateur, tablette, smartphone).

---

## 2. Accès à l'application

### URL de l'application

```
https://nurturing-achievement-production.up.railway.app
```

### Menu de navigation

Le menu situé à gauche permet d'accéder aux différentes sections :

| Lien | Description |
|------|-------------|
| **Home** | Retour au dashboard principal |
| **Datas** | Tableau des données brutes |
| **about** | Informations sur le projet |
| **statistical** | Graphiques et statistiques |
| **history** | Historique des mesures |
| **Admin ESP32** | Configuration des capteurs |

---

## 3. Le Dashboard

### Vue d'ensemble

Le dashboard est la page d'accueil. Il affiche une carte pour chaque capteur actif avec :

- Le **nom du capteur** (personnalisable)
- L'**indicateur de statut** :
  - 🟢 **En ligne** : le capteur envoie des données
  - 🟠 **Vu récemment** : dernière activité il y a quelques minutes
  - 🔴 **Hors ligne** : le capteur ne répond plus
- Les **valeurs actuelles** : température, pression, humidité

### Rafraîchissement automatique

Les données se mettent à jour automatiquement toutes les **20 secondes**. Vous n'avez pas besoin de rafraîchir la page manuellement.

### Comprendre les indicateurs

| Statut | Signification |
|--------|---------------|
| En ligne | Données reçues dans les 2 dernières minutes |
| Vu il y a X min | Dernière activité entre 2 et 5 minutes |
| Hors ligne (Xh) | Aucune donnée depuis plus de 5 minutes |

---

## 4. Les Graphiques

### Accès

Cliquez sur **"statistical"** dans le menu.

### Types de graphiques

L'application génère 3 graphiques :

1. **Températures** (graphique en lignes)
   - Affiche l'évolution de la température pour chaque capteur
   - Axe X : heures de la journée
   - Axe Y : température en °C

2. **Pressions** (graphique en lignes)
   - Affiche l'évolution de la pression atmosphérique
   - Axe X : heures de la journée
   - Axe Y : pression en hPa

3. **Humidité** (graphique en barres)
   - Compare l'humidité moyenne entre capteurs
   - Une barre par capteur

### Sélectionner une date

1. Utilisez le **sélecteur de date** en haut de la page
2. Choisissez la date souhaitée
3. Cliquez sur **"Rafraîchir"**
4. Les graphiques se mettent à jour

### Pas de données ?

Si les graphiques sont vides :
- Vérifiez que des données existent pour la date sélectionnée
- Assurez-vous qu'au moins un capteur était actif ce jour-là

---

## 5. L'Historique

### Accès

Cliquez sur **"history"** dans le menu.

### Fonctionnalités

- Affiche l'historique complet des mesures
- Permet de filtrer par date
- Données présentées sous forme de tableau

### Colonnes affichées

| Colonne | Description |
|---------|-------------|
| Date | Date de la mesure |
| Heure | Heure exacte |
| Température | Valeur en °C |
| Humidité | Valeur en % |
| Pression | Valeur en hPa |

---

## 6. Administration des capteurs

### Accès

Cliquez sur **"Admin ESP32"** dans le menu.

### Interface d'administration

Cette page affiche tous les capteurs ESP32 enregistrés avec :

- **Adresse MAC** : identifiant unique du capteur
- **Statut** : en ligne (🟢) ou hors ligne (🔴)
- **Adresse IP** : adresse réseau locale
- **Nom actuel** : nom affiché sur le dashboard

### Configurer un capteur

1. Repérez le capteur à configurer (identifié par son adresse MAC)
2. Dans le menu déroulant, sélectionnez le **numéro de capteur** (Capteur 1, 2, 3...)
3. Dans le champ texte, entrez le **nom personnalisé** (ex: "Salon", "Extérieur", "Bureau")
4. Cliquez sur **"Configurer"**

Le nom apparaîtra sur le dashboard après quelques secondes.

### Supprimer un capteur

1. Cliquez sur le bouton **"Supprimer"** (rouge) sous le capteur
2. Confirmez la suppression

**Attention :** Cette action supprime uniquement l'enregistrement du capteur, pas ses données historiques.

### Actualiser la liste

Cliquez sur **"Actualiser"** en haut à droite pour recharger la liste des capteurs.

---

## 7. Questions fréquentes

### Le capteur affiche "Hors ligne"

**Causes possibles :**
- Le capteur n'est pas alimenté
- Le capteur n'est pas connecté au WiFi
- Le serveur n'a pas reçu de données depuis plus de 2 minutes

**Solutions :**
1. Vérifiez l'alimentation du capteur ESP32
2. Vérifiez la connexion WiFi
3. Redémarrez le capteur (débranchez et rebranchez)

### Le nom du capteur ne change pas

Après avoir configuré un nouveau nom dans l'admin :
1. Attendez quelques secondes
2. Rafraîchissez la page du dashboard (F5)

### Les graphiques ne s'affichent pas

**Causes possibles :**
- Aucune donnée pour la date sélectionnée
- Les capteurs n'ont pas encore envoyé de données

**Solutions :**
1. Sélectionnez une autre date
2. Attendez que les capteurs envoient des données

### Comment ajouter un nouveau capteur ?

1. Branchez et configurez l'ESP32 avec le code approprié
2. L'ESP32 s'enregistre automatiquement auprès du serveur
3. Il apparaît dans l'interface Admin avec le statut "En attente de configuration"
4. Configurez-le en lui assignant un numéro et un nom

### Les données sont-elles conservées ?

Oui, toutes les données sont stockées dans une base de données. Vous pouvez consulter l'historique complet via la page "history".

### Puis-je accéder à l'application depuis mon téléphone ?

Oui, l'interface est responsive et fonctionne sur :
- Ordinateurs (Windows, Mac, Linux)
- Tablettes (iPad, Android)
- Smartphones (iPhone, Android)

---

## Besoin d'aide ?

Si vous rencontrez des difficultés ou avez des questions, n'hésitez pas à me contacter ou à consulter les ressources suivantes :

- **GitHub du projet :** https://github.com/pj43svh/MA-Metier-Station-Meteo
- **Trello :** https://trello.com/b/mbKZJSjJ/station-météo-esp32-rpi
- **CPNV :** https://cpnv.ch

---

*Document rédigé par Amin Torrisi - CPNV - Janvier 2026*
