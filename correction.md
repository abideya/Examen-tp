# Correction — Examen TP Docker

Cette correction correspond à l'application fonctionnelle fournie dans ce répertoire. Depuis la racine `Docker-Exam/`, créez les images et démarrez les conteneurs dans l'ordre indiqué.

## 1. Dockerfile Nginx

`nginx/Dockerfile` :
```dockerfile
FROM nginx:alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY frontend/index.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 2. Dockerfile Login

`login/Dockerfile` :
```dockerfile
FROM python:3.12-slim
WORKDIR /logindir
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 3. Dockerfile Sign Up

`signup/Dockerfile` :
```dockerfile
FROM python:3.12-slim
WORKDIR /signupdir
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 4. Dockerfile MySQL

`database/Dockerfile` :
```dockerfile
FROM mysql:8.0
COPY init.sql /docker-entrypoint-initdb.d/init.sql
EXPOSE 3306
```

## 5. Construire les images

Depuis la racine du projet :
```bash
docker build -f nginx/Dockerfile -t exam-frontend:1.0 .
docker build -t exam-login:1.0 ./login
docker build -t exam-signup:1.0 ./signup
docker build -t exam-database:1.0 ./database
```

## 6. Créer le réseau et lancer les conteneurs

```bash
docker network create exam-network

docker run -d --name database --network exam-network \
  -e MYSQL_ROOT_PASSWORD='RootPass123!' \
  -e MYSQL_DATABASE='appdb' \
  -e MYSQL_USER='appuser' \
  -e MYSQL_PASSWORD='AppPass123!' \
  exam-database:1.0
```

Attendez que MySQL soit prêt :
```bash
docker logs database
```

Puis lancez les deux backends :
```bash
docker run -d --name login --network exam-network \
  -e DB_HOST='database' -e DB_PORT='3306' \
  -e DB_NAME='appdb' -e DB_USER='appuser' \
  -e DB_PASSWORD='AppPass123!' \
  exam-login:1.0

docker run -d --name signup --network exam-network \
  -e DB_HOST='database' -e DB_PORT='3306' \
  -e DB_NAME='appdb' -e DB_USER='appuser' \
  -e DB_PASSWORD='AppPass123!' \
  exam-signup:1.0
```

Enfin, lancez Nginx :
```bash
docker run -d --name frontend --network exam-network \
  -p 8000:80 exam-frontend:1.0
```

## 7. Vérifications

```bash
docker ps
docker images
docker network ls
docker exec frontend nginx -t
docker exec frontend nginx -T
docker logs frontend
docker logs login
docker logs signup
docker logs database
```

Ouvrez `http://localhost:8000`, créez un compte puis connectez-vous.

## 8. Dépannage

| Erreur | Cause possible |
|---|---|
| `502 Bad Gateway` | Backend arrêté, mauvais nom ou port, problème réseau |
| `403 Forbidden` | Règles d'accès ou permissions |
| `404 Not Found` | URI ou route inexistante |
| `Connection refused` | Service pas démarré ou mauvais port |
| `Host is unreachable` | Problème de connectivité réseau |
| Erreur MySQL | Identifiants incorrects, DB non prête ou schéma absent |

Les mots de passe de cet exemple sont réservés à un environnement de laboratoire. Ne les réutilisez pas en production.
