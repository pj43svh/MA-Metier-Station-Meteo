Parfait, le sujet est **très bon pédagogiquement** et bien dimensionné pour **3 semaines plein temps / 4 élèves**, surtout avec une **architecture distribuée Raspberry Pi + ESP32**.
Je te propose ci-dessous un **cahier des charges complet**, structuré comme tu pourrais réellement le donner aux élèves, suivi d’un **découpage en 3 sprints d’une semaine** avec livrables, rôles et critères de validation.

------

# 📘 Cahier des charges

## Projet : Station météorologique connectée (Raspberry Pi & ESP32)

### 1. Contexte du projet

Ce projet est proposé par un élève et validé par l’équipe pédagogique.
Il vise à concevoir une **station météorologique modulaire**, composée de plusieurs capteurs distribués et d’une centrale de supervision.

Le projet se déroule sur **3 semaines à plein temps**, en équipe de **4 élèves**, selon une **méthodologie de type agile (sprints hebdomadaires)**.

------

### 2. Objectifs pédagogiques

Le projet doit permettre aux élèves de :

- Concevoir une **architecture IoT complète**
- Travailler avec des **microcontrôleurs (ESP32)** et un **ordinateur embarqué (Raspberry Pi)**
- Mettre en place une **communication réseau**
- Lire, traiter et afficher des **données issues de capteurs**
- Concevoir une **interface graphique tactile**
- Travailler en équipe avec **répartition des rôles**
- Documenter un projet technique de manière professionnelle

------

### 3. Description générale du système

Le système est divisé en **deux grandes parties indépendantes mais interconnectées** :

#### 3.1 Centrale météo (Raspberry Pi)

- Basée sur un **Raspberry Pi**
- Équipée d’un **écran tactile**
- Sert de **point central de gestion**
- Fonctions principales :
  - Visualisation des données des capteurs
  - Ajout / suppression de capteurs distants
  - Identification des capteurs (nom, type, localisation)
  - Historique simple des mesures
  - Affichage en temps réel

#### 3.2 Modules capteurs (ESP32)

- Basés sur des **ESP32**
- Chaque module peut contenir **un ou plusieurs capteurs**
- Capteurs envisagés (au minimum 2 obligatoires) :
  - Température
  - Humidité
  - Luminosité
  - (optionnel) vitesse du vent / pression / pluie
- Envoi périodique des données vers la centrale
- Communication sans fil (Wi-Fi)

------

### 4. Contraintes techniques

#### 4.1 Matériel

- Raspberry Pi (modèle au choix selon disponibilité)
- Écran tactile compatible Raspberry Pi
- ESP32
- Capteurs courants (DHT22, BME280, LDR, etc.)
- Alimentation stable pour chaque module

#### 4.2 Logiciel

- Langages autorisés :
  - ESP32 : C/C++ (Arduino ou ESP-IDF)
  - Raspberry Pi : Python (recommandé)
- Système d’exploitation : Raspberry Pi OS
- Interface graphique libre (Tkinter, PyQt, Kivy, web local, etc.)
- Communication réseau :
  - HTTP REST **ou**
  - MQTT (bonus)

#### 4.3 Organisation

- Utilisation d’un **dépôt Git**
- Documentation obligatoire
- Code commenté et structuré

------

### 5. Fonctionnalités attendues

#### 5.1 Fonctionnalités obligatoires

- Lecture de données depuis au moins **2 capteurs différents**
- Envoi des données des ESP32 vers le Raspberry Pi
- Affichage des données sur l’écran tactile
- Ajout manuel d’un nouveau capteur/module depuis la centrale
- Identification de chaque module (ID, nom)
- Rafraîchissement automatique des données

#### 5.2 Fonctionnalités optionnelles (bonus)

- Historique graphique
- Alertes (seuil température, humidité, etc.)
- Reconnexion automatique des capteurs
- Mise à jour de la fréquence d’envoi
- Boîtier imprimé en 3D

------

### 6. Répartition des rôles (indicative)

- **Élève 1** : ESP32 & capteurs
- **Élève 2** : Communication réseau
- **Élève 3** : Interface graphique Raspberry Pi
- **Élève 4** : Intégration, tests, documentation

*(Les rôles peuvent évoluer au fil des sprints)*

------

# 🧩 Organisation du projet – Sprints

------

## 🟦 Sprint 1 – Conception & bases techniques (Semaine 1)

### Objectifs

- Comprendre le projet
- Concevoir l’architecture globale
- Avoir une **première communication fonctionnelle**

### Tâches

- Analyse du besoin
- Schéma d’architecture (ESP32 ↔ Raspberry Pi)
- Choix des protocoles de communication
- Mise en place du dépôt Git
- Test d’un capteur sur ESP32
- Envoi d’une valeur simple vers le Raspberry Pi
- Réception et affichage en console

### Livrables

- Diagramme d’architecture
- Dépôt Git initialisé
- Code ESP32 lisant un capteur
- Communication réseau fonctionnelle
- Journal de bord

### Critères de validation

- Un ESP32 envoie une valeur lisible au Raspberry Pi
- Le code compile et est documenté
- Architecture clairement expliquée

------

## 🟦 Sprint 2 – Fonctionnalités principales (Semaine 2)

### Objectifs

- Rendre le système **utilisable**
- Développer la **centrale météo**

### Tâches

- Lecture de plusieurs capteurs sur ESP32
- Structuration des données (JSON)
- Développement de l’interface tactile
- Affichage temps réel des mesures
- Gestion de plusieurs modules capteurs
- Identification des capteurs

### Livrables

- Interface graphique fonctionnelle
- Données affichées en temps réel
- Code ESP32 finalisé (v1)
- Documentation technique intermédiaire

### Critères de validation

- Données visibles sur l’écran tactile
- Plusieurs capteurs reconnus
- Interface compréhensible et stable

------

## 🟦 Sprint 3 – Finalisation & qualité (Semaine 3)

### Objectifs

- Stabiliser
- Améliorer l’expérience utilisateur
- Documenter le projet

### Tâches

- Gestion des erreurs (capteur hors ligne)
- Amélioration de l’interface
- Ajout de fonctionnalités bonus (si temps)
- Tests complets
- Nettoyage du code
- Rédaction de la documentation finale
- Préparation de la démonstration

### Livrables

- Projet fonctionnel complet
- Documentation utilisateur
- Documentation technique
- Présentation finale

### Critères de validation

- Système stable
- Projet compréhensible par un tiers
- Démonstration fluide
- Respect du cahier des charges

------

# 📊 Évaluation (indicatif)

- Fonctionnalité : 40 %
- Qualité du code : 20 %
- Architecture & communication : 15 %
- Interface utilisateur : 15 %
- Documentation & travail d’équipe : 10 %

------

Si tu veux, au prochain message je peux :

- 📄 te fournir une **version PDF prête à distribuer**
- 🧑‍🏫 adapter le niveau (CFC / ES / bachelor)
- 🧩 proposer une **grille d’évaluation détaillée**
- 📅 ajouter un **planning journalier précis**

Dis-moi ce que tu veux affiner 👍