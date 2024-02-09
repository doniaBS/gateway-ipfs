# Techoney - Solution de Traçabilité pour la Chaîne d'Approvisionnement du Miel
<br>
** Partie 1 : Iot devices ( broker ) , et gateway **

Bienvenue dans le référentiel (repo) de Techoney, un projet dédié à la création d'une solution décentralisée pour garantir la traçabilité dans la courte chaîne d'approvisionnement du miel.

## Objectif du Projet

L'objectif principal de Techoney est de renforcer la transparence et la sécurité au sein de l'industrie apicole en utilisant des technologies telles que la blockchain et l'Internet des Objets (IoT). 
Nous nous concentrons sur la traçabilité, de la ruche au consommateur, pour assurer l'authenticité et la qualité du miel.

## Composants Principaux

- **Broker (HiveMQ):** Point de départ pour la collecte des données de température.
- **Gateway (Script Python):** Centralise la collecte et la transmission des données d'un reseau a un autre.
- **IPFS (Infura):** Stockage décentralisé des données avec génération de hash pour l'immuabilité.
- **Blockchain (Ganache):** Utilisation de la blockchain pour garantir la traçabilité.
- **Smart Contract (avec le framework Truffle):** Gère l'interaction avec la blockchain et le stockage des hash.

## Guide d'Installation et d'Utilisation

1. **Installer le broker HiveMQ :**
   -Tout d'abord, installez HiveMQ. Pour ce faire, suivez les étapes suivantes :
      - **Téléchargez le dosier .zip d'installation depuis le site officiel de HiveMQ :** https://www.hivemq.com/download/
      - **Extrayez le dossier téléchargé à l'emplacement de votre choix sur votre système.**
      - **Accédez au dossier bin dans le répertoire extrait.**
      - **Faites un clic droit sur le fichier run.bat, puis sélectionnez "Exécuter en tant qu'administrateur".**
