# Application web « find my Alex » - Rapport

# But du projet

Créer une application web affichant sur une carte les dernières locations de mon téléphone, à la manière des services «* find my *» d'Apple. Le challenge était d'utiliser un Raspberry Pi pour déployer ce service.

Pour atteindre ce but, voici ce qui a été accompli :

-   Développement d'une application Svelte[^1]

-   Raspberry Pi :
    -   Docker : base de données Redis pour stocker les locations
        envoyées par mon téléphone.
    -   Docker : REST API sécurisé par JWT avec le framework python
        [FastAPI](https://fastapi.tiangolo.com/).
    -   Nginx : reverse-proxy et serveur web.

-   Téléphone : script envoyant périodiquement sa position au REST API
    avec l'application
    [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm).

-   Routeur : ouverture de ports, redirection vers Raspberry Pi, ajout
    de règles NAT

-   M5 Stack : mise en place d'un script lui permettant d'interagir avec
    le réseau simulé de Packet Tracer / obtenir la dernière location en
    faisant une requête à l'API.

-   Packet Tracer : petite simulation d'IoT contenant une porte de
    garage, une machine à café et une lumière.

Un schéma de mon réseau disponible en dernière page de ce rapport.

# Éléments en détails

## Application web -- Svelte

Ce projet m'a paru être la parfaite opportunité pour apprendre à utiliser le framework JavaScript Svelte, sa promesse d'ajouter une réactivité à JavaScript standard sans utiliser de boilerplates comme React m'a beaucoup intéressé.

Un autre avantage est que Svelte rend du code JavaScript standard dans le dossier `public`, c'est le contenu de ce dossier qui est servi par un serveur web Nginx sur mon Raspberry Pi.

Voici les paquets Node.js et frameworks JavaScripts utilisés :

-   Svelte (<https://www.npmjs.com/package/svelte>).
-   Leaflet (<https://leafletjs.com/>), libraire JavaScript utilisée
    pour gérer l'affichage de la carte et des marqueurs.
-   Svelte-router-spa
    (<https://www.npmjs.com/package/svelte-router-spa>), paquet utilisé
    pour créer une application monopage[^2] avec Svelte.

Voici comment sont organisés les fichiers de ce projet -- le dossier `node_modules` ne s'affichera qu'après installation des paquets Node.js :

```
Svelte app
├── node_modules \# paquets installé par Node.js
│ └── [...]
├── src
│ ├── routes \# Utilisé par svelte-router-spa pour gèrer routes
│ │ ├── Map.svelte \# Contient la page principale du site
│ │ └── Sources.svelte \# Contient les sources utilisées
│ ├── App.svelte \# S'occupe du routing et de la barre de navigation
│ └── main.js
├── public \# fichiers exportés par Svelte à la compilation
├── packages.json
└── rollup.config.js
```

Map.svelte

Fichier responsable de ce qui s'affiche à la racine du site, voici les principales variables utilisées :

-   **apiServer** -- permet de spécifier l'URL de l'API utilisé
-   **markerLocations** -- contiendra la liste des marqueurs GPS.
-   map -- objet carte de Leaflet qui sera affiché.
-   initialView -- coordonnées initiales affichées sur la carte.
-   **svgIcon --** image en format vectoriel pour représenter les
    marqueurs affichés sur la carte.

À l'affichage de la page, la fonction **mapAction()** se déclenche, appelant elle-même la fonction **init()** qui envoie une requête à l'API pour obtenir la liste de toutes les coordonnées stockées par Redis. Un tri par timestamp se fait ensuite, Redis stockant les coordonnées géospatiales par distance, et non pas par ordre d'ajout. Les coordonnées ne sont pas stockées dans le même ordre pour Redis et Leaflet, des objets Leaflet LatLng sont donc créées pour chaque coordonnée.

mapAction() créer ensuite une carte Leaflet sur le conteneur qui l'a lancé (ici la div HTML ayant comme id « map »), puis ajoute toutes les coordonnées à la carte nouvellement créée.

Le bouton « Show last know location » appelle finalement la fonction flyToLastCoordinates(), qui comme son nom l'indique vole vers la dernière location ajoutée et ajoute un cercle bleu symbolisant la précision de la localisation.

En bonus, j'ai mis un bouton supplémentaire « Travel to Mexico City » appelant flyToMexico() pour me donner l'impression de partir dans un endroit chaud.

---

Le projet peut être trouvé dans le dossier `Svelte app`. Pour tester en local, il faut installer Node.JS, puis lancer les commandes suivantes dans le dossier extrait :

```bash
npm install
npm run dev
```

Cela crée un serveur web local à l'adresse [http://localhost:5000](http://localhost:5000/). Pour que l'application soit fonctionnelle, il faudra encore configurer Redis, ainsi que l'API communiquant avec ce dernier.

Lorsque je souhaite compiler mon code Svelte en JavaScript standard, j'utilise la commande :

```bash
npm run build
```

Le code compilé se trouve ensuite dans le sous-dossier `public`.

## Base de donnée - Redis

Ayant travaillé avec Redis dans un projet d'un autre cours, j'avais beaucoup apprécié sa simplicité et rapidité, deux éléments qui m'ont fait penser à l'utiliser sur mon Raspberry Pi. Redis supporte également nativement les structures de données géospatiales, ce qui m'a bien simplifié la tâche (au début en tout cas... à suivre dans la section « Difficultés rencontrées »).

C'est un conteneur Docker utilisant l'image Redis officielle (<https://hub.docker.com/_/redis>) qui a été utilisé, avec l'option du stockage persistant afin de garder les données même si le conteneur devrait être stoppé, pour effectuer une mise à jour par exemple.

Voici les commandes utilisées pour configurer Redis avec Docker :

```bash
docker pull redis

docker run --name redis -d redis redis-server --save 60 1 --loglevel warning
```

Le serveur Redis utilisé par mon application a assigné l'adresse IP
172.17.0.2 et le port 6379 sur le réseau Docker. Durant le
développement, j'ai également utilisé un serveur Redis installé
localement sur mon ordinateur portable en utilisant directement la
commande suivante :

```bash
redis-server
```

## REST API -- FastAPI

Afin d'avoir un endroit central où les données seraient accessibles par
l'application ou par mon téléphone lorsqu'il envoie sa position, j'ai
fini par choisir de faire un REST API.

Après quelques recherches, j'ai fini par décider d'utiliser le framework
Python FastAPI (<https://fastapi.tiangolo.com/>). C'est un framework qui
se veut très performant, simple d'utilisation, qui respecte le standard
OpenAPI, entre autres.

Une autre plus-value était sa fonctionnalité de générer automatiquement
une documentation interactive depuis le code de l'utilisateur. Je me
suis dit que cela facilitera la collaboration avec des tiers, ainsi que
la présentation de ce projet en classe.

Afin de tester le serveur localement, exécuter à la racine du projet la
commande suivante :

```bash
uvicorn main:app --reload
```

La documentation interactive peut donc être trouvée à
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
(pour la version en ligne : <https://api.zurcher.digital/docs>).

### Points d'accès

[https://api.zurcher.digital](https://api.zurcher.digital/) (GET) -- permet de tester si l'API fonctionne - « *It's alive !* »

```bash
curl -X 'GET' \
    'https://api.zurcher.digital/' \
    -H 'accept: application/json'
```

---

[https://api.zurcher.digital](https://api.zurcher.digital/user/login)[/](https://api.zurcher.digital/user/login)[user](https://api.zurcher.digital/user/login)[*/*](https://api.zurcher.digital/user/login)[login](https://api.zurcher.digital/user/login) (GET) - méthode d'authentification, un *request body *est nécessaire à cette requête[^3]:

```bash
curl -X 'POST' \
    'https://api.zurcher.digital/user/login' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        "username": "dev",
        "password": "1234",
        "email": "dev@localhost"
    }'
```

Cette requête retourne un JSON Web Token (JWT), utilisé pour
l'authentification du point d'accès
[https://api.zurcher.digital/](https://api.zurcher.digital/coordinates/add)[coordinates/add](https://api.zurcher.digital/coordinates/add)
au format suivant :

`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

Ce token est constitué d'un en-tête indiquant l'algorithme de hashage
utilisé pour sa signature, une* *charge utile contenant le *request
body* envoyé plus tôt, et finalement une signature permettant au serveur
de vérifier l'authenticité du token. Plus d'informations ici :
<https://jwt.io/>.

---

[https://api.zurcher.digital/](https://api.zurcher.digital/coordinates)[coordinates](https://api.zurcher.digital/coordinates)(GET) - Obtient toutes les coordonnées stockées dans la base de données Redis, dans l'ordre chronologique.

```bash
curl -X 'GET' \
    'https://api.zurcher.digital/coordinates' \
    -H 'accept: application/json'
```

Cette requête retournera :

```
[
  [
    "1641569567",
    [
      6.143157184123993,
      46.20439151055383
    ]
  ],
(...)
  ]
]
```

---

[https://api.zurcher.digital/](https://api.zurcher.digital/coordinates/add)[coordinates/add](https://api.zurcher.digital/coordinates/add) (POST) - Ajoute une paire de coordonnées dans Redis avec un timestamp UNIX comme membre (identifiant unique).

Cette requête doit s'accompagner d'un token valide :

```bash
curl -X 'POST' \
  'https://api.zurcher.digital/coordinates/add?longitude=1111111111111&latitude=1&timestamp=1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
```

Un message de confirmation suivra si la requête est valide. L'API
vérifie si les coordonnées sont valides, et donne un message d'erreur si
elles ne le sont pas.

## Nginx

Nginx est utilisé pour deux choses :

-   Un reverse-proxy permettant de rediriger le trafic en destination de
    [https://api.zurcher.digital](https://api.zurcher.digital/) vers
    [http://localhost:1234](http://localhost:1234/) (l'adresse IP locale
    sur laquelle l'API est disponible).
-   Servir le site
    [https://findmyalex.zurcher.digital](https://findmyalex.zurcher.digital/),
    c'est-à-dire le code JavaScript standard produit par Svelte.

Le script python certbot a été utilisé pour obtenir des certificats
HTTPS depuis Let's Encrypt pour le site et le reverse-proxy. Les deux
fichiers de configuration utilisés peuvent être trouvés dans le dossier
« Nginx ».

## Téléphone -- ajout de données

Grâce à l'application Tasker, mon téléphone envoie toutes les
demi-heures (lorsque cela est possible bien sûr) ses coordonnées GPS
accompagnées d'un timestamp UNIX à l'API :

1.  L'utilisateur se connecte et obtient un token.
2.  La localisation du téléphone est obtenue.
3.  Un timestamp UNIX est généré.
4.  Une dernière requête est envoyée, comportant token pour
    authentification, longitude et latitude et finalement, le timestamp.

Vous trouverez joint à ce rendu dans le dossier « Scripts » le fichier
« test_send_coordinates.sh » qui suit cette même logique utilisant les
coordonnées de la HEG, je l'ai beaucoup utilisé pour tester
l'application, n'hésitez pas à faire de même !

## Routeur

Afin de donner accès à l'application à l'extérieur de mon réseau local,
j'ai ajouté des ouvertures des ports 80 et 443 en destination de
192.168.2.2 (adresse IP de mon Raspberry Pi), ainsi que quelques règles
NAT. Ces dernières m'ont permis de rediriger le trafic provenant de mes
appareils locaux en direction de mon adresse IP publique (84.74.113.11)
vers mon Raspberry Pi, afin de pouvoir travailler sur le site en ligne
depuis chez moi.

Une ouverture du port 22 redirigeant vers mon Raspberry Pi a également
été ajoutée pour la démonstration en classe.

## M5 Stack

![](Pictures/100000000000092800000928F6EA43EBEE8DF7C2.png){width="7.001cm"
height="7.001cm"}Voici ce que fait le code python de mon M5 Stack lors
de son exécution :

1.  Se connecte à mon wifi (dans le code rendu le SSID et le mot de
    passe ont été modifiés).
2.  La fonction **show_label()** est ensuite appelée, affichant sur
    l'écran une légende pour chacun des trois boutons physique du M5,
    indiquant leur utilité.

Ensuite l'utilisateur peut choisir sur quel bouton cliquer :

-   Bouton A, « coordinates » -- envoie une requête à l'API
    [https://api.zurcher.digital](https://api.zurcher.digital/), obtient
    les coordonnées stockées, puis affiche les plus récentes obtenues
    sur l'écran. Le texte « loading » est affiché en attendant la
    réception d'une réponse.
-   Bouton B, « IoT on » -- envoie à Packet Tracer une requête TCP avec
    le message « on »→ cela allume la lumière, ouvre la porte du garage
    et prépare du café (virtuellement bien sûr). La réponse de Paquet
    Tracer est ensuite affichée à l'écran.
-   Bouton C, « IoT off » -- envoie à Packet Tracer une requête TCP avec
    le message « off » → pour éteindre la lumière, fermer la porte du
    garage et éteindre la machine à café. La réponse de Paquet Tracer
    est ensuite affichée à l'écran.

Packet Tracer est installé sur mon laptop avec l'adresse IP 192.168.1.4.
Le port utilisé pour communiquer entre le M5 Stack et Packet Tracer est
12345

Vous pouvez trouver le code joint à ce rendu dans le dossier « M5
Stack ».

## Packet Tracer

![](Pictures/10000000000001BC000001E92F49273BDE7CDF74.png){width="4.001cm"
height="4.399cm"}Le SBC du projet a un serveur TCP avec le port 12345
utilisant le template « Real TCP Server - Python », qui selon les
requêtes reçues du M5 Stack enverra des signaux on/off aux objets IoT.

voir dossier « Packet Tracer » pour le fichier du projet.

# Difficultés rencontrées

### Apprentissage de JavaScript et Svelte

Il m'a fallu un certain temps pour comprendre le fonctionnement de base
de JavaScript puis de l'appliquer dans le framework de Svelte.
Heureusement, j'ai trouvé certains guides en ligne qui m'ont beaucoup
aidé (voir section Bibliographie).

### Configuration du routeur

Utilisant VyOS (un fork de Vyatta, sur lequel est basé RouterOS d'Ubiquiti), il était parfois compliqué à trouver comment ouvrir le firewall, effectuer une redirection NAT vers le Raspberry Pi, que ce soit depuis l'extérieur ou le réseau local.

La base de connaissance VyOS m'a été très utile à ces fins.

### Ordre des coordonnées géographiques

Redis et Leaflet ne stocke pas les latitudes et longitudes dans le même ordre : Redis stocke d'abord longitude, puis latitude, et Leaflet fait le contraire. J'ai pu régler ce problème en renversant l'ordre des coordonnées dans l'application Svelte -- *voir fonction **init()** dans « Svelte App/src/Map.svelte »*

### Sécuriser FastAPI

Il m'a fallu un certain temps pour adapter mon code afin de le rendre sécurisé, en effet le concept de JWT était nouveau pour moi, je n'avais donc pas l'habitude de travailler dessus.

La base de connaissance FastAPI ainsi qu'un article très détaillé (voir Bibliographie) m'a permis d'arriver au bout de cette étape.

### Déploiement sur Raspberry Pi

Beaucoup plus lent que mes autres ordinateurs, il était parfois un peu fastidieux de travailler sur mon Raspberry Pi. Afin de me simplifier la vie, j'ai créé des scripts sur mon ordinateur portable pour envoyer
rapidement le code produit sur le Raspberry Pi via SSH, et des scripts
de déploiement pour l'application web (qui copie simplement les nouveaux
fichiers vers la racine du site), et pour le conteneur Docker (qui
remplace à chaque fois automatiquement l'ancienne image par la nouvelle
générée, arrête l'ancien conteneur et lance un nouveau utilisant la
nouvelle image).

# Bibliographie

### FastAPI

FastAPI in Containers - Docker - FastAPI.
<https://fastapi.tiangolo.com/deployment/docker/>. Consulté le 3 janvier
2022.

Securing FastAPI with JWT Token-Based Authentication.
<https://testdriven.io/blog/fastapi-jwt-auth/>. Consulté le 6 janvier
2022.

### JWT

auth0.com. JWT.IO. <http://jwt.io/>. Consulté le 7 janvier 2022.

### Svelte et Leaflet

Interactive Maps with Leaflet and Svelte.
<https://imfeld.dev/writing/leaflet_with_svelte>. Consulté le 3 janvier
2022.

« Svelte-Router-Spa ». Npm,
https://www.npmjs.com/package/svelte-router-spa. Consulté le 9 janvier
2022.

« Using SVG Icons for Leaflet Js Markers ». One Step! Code, 6 juin 2021,
<https://onestepcode.com/leaflet-markers-svg-icons/>.

### M5 Stack

« MicroPython: Networking ». MicroPython Tutorial,
http://mpy-tut.zoic.org/tut/network.html. Consulté le 8 janvier 2022.

# Schéma Réseau

[^1]: <https://svelte.dev/> - un framework JavaScript connu pour sa vitesse, produisant du JavaScript natif lors de la compilation.

[^2]:  <https://developer.mozilla.org/fr/docs/Glossary/SPA> -  « Implémentation d\'application web qui ne charge qu'un seul document web, puis met à jour le contenu du corps de ce document via des API JavaScript (...) lorsqu'un contenu différent doit être affiché. »

[^3]: Utiliser le corps renseigné fonctionnera pour le code joint à ce rendu, mais pas pour l'API actuellement en ligne sur https://api.zurcher.digital. Les utilisateurs sont stockés dans une liste dans le code Python par simplicité.
