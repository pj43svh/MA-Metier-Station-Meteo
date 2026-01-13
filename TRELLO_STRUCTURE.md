# Structure Trello - Station Météo

## Créer un nouveau board Trello

1. Aller sur [trello.com](https://trello.com)
2. Créer un nouveau board : **"Station Météo - ESP32/RPi"**

---

## Colonnes à créer

| Colonne | Description |
|---------|-------------|
| 📋 **Backlog** | Toutes les tâches à faire |
| 🎯 **Sprint actuel** | Tâches du sprint en cours |
| 🔄 **En cours** | Tâches en développement |
| 👀 **En revue** | Tâches à valider par l'équipe |
| ✅ **Terminé** | Tâches validées |

---

## Labels (étiquettes)

| Couleur | Label | Usage |
|---------|-------|-------|
| 🔴 Rouge | **Urgent** | Bloquant pour la suite |
| 🟠 Orange | **Bug** | Correction de bug |
| 🟡 Jaune | **ESP32** | Tâches côté capteurs |
| 🟢 Vert | **Raspberry Pi** | Tâches côté centrale |
| 🔵 Bleu | **Interface** | Frontend / UI |
| 🟣 Violet | **Documentation** | Docs, README, etc. |

---

## Cartes à créer pour le Sprint 1

### 📋 Backlog → 🎯 Sprint 1

#### ESP32 & Capteurs (🟡)
- [ ] **Configurer l'environnement Arduino/PlatformIO**
  - Installer Arduino IDE ou VS Code + PlatformIO
  - Ajouter le support ESP32
  - Checklist: IDE installé, board ESP32 reconnu

- [ ] **Brancher et tester le capteur DHT22**
  - Câblage: VCC→3.3V, DATA→GPIO4, GND→GND
  - Installer la librairie DHT
  - Afficher température/humidité sur Serial

- [ ] **Brancher et tester le capteur de luminosité (LDR)**
  - Câblage avec résistance de pull-down
  - Lire la valeur analogique

#### Communication (🔵)
- [ ] **Connecter l'ESP32 au WiFi**
  - Code de connexion WiFi
  - Afficher l'IP sur Serial

- [ ] **Envoyer une requête HTTP POST au Raspberry Pi**
  - Format JSON
  - Test avec données factices

#### Raspberry Pi (🟢)
- [ ] **Installer le serveur Flask**
  - Clone du repo
  - Environnement virtuel
  - Lancer le serveur

- [ ] **Tester l'API avec Postman/curl**
  - POST /api/capteurs (créer un capteur)
  - POST /api/mesures (envoyer des mesures)
  - GET /api/mesures/latest (vérifier)

#### Documentation (🟣)
- [ ] **Créer le schéma d'architecture**
  - Diagramme ESP32 ↔ WiFi ↔ Raspberry Pi
  - Outil: draw.io, Excalidraw, ou papier

- [ ] **Documenter le câblage des capteurs**
  - Photos + schémas
  - Liste du matériel

---

## Cartes pour Sprint 2 (à mettre dans Backlog)

- [ ] Lire plusieurs capteurs simultanément (ESP32)
- [ ] Envoyer les données en JSON structuré
- [ ] Affichage temps réel sur l'interface web
- [ ] Gestion de plusieurs ESP32
- [ ] Ajouter/supprimer un capteur depuis l'interface
- [ ] Tests d'intégration complets

---

## Cartes pour Sprint 3 (à mettre dans Backlog)

- [ ] Gestion des erreurs (capteur hors ligne)
- [ ] Amélioration du design de l'interface
- [ ] Historique graphique (bonus)
- [ ] Alertes de seuil (bonus)
- [ ] Documentation finale
- [ ] Préparation de la démo

---

## Membres de l'équipe

Ajouter les 4 membres au board et assigner les cartes:

| Membre | Rôle principal | Étiquettes |
|--------|---------------|------------|
| Élève 1 | ESP32 & Capteurs | 🟡 |
| Élève 2 | Communication réseau | 🟡🟢 |
| Élève 3 | Interface Raspberry Pi | 🟢🔵 |
| Élève 4 | Intégration, tests, docs | 🟣 |

---

## Bonnes pratiques

1. **Daily standup** : Chaque jour, répondre à :
   - Qu'est-ce que j'ai fait hier ?
   - Qu'est-ce que je fais aujourd'hui ?
   - Est-ce que j'ai des blocages ?

2. **Déplacer les cartes** : Toujours garder le board à jour

3. **Checklist** : Utiliser les checklists dans les cartes pour les sous-tâches

4. **Commentaires** : Documenter les décisions et problèmes rencontrés

5. **Pièces jointes** : Ajouter les schémas, photos, liens utiles
