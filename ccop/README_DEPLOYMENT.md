# 🚀 Déploiement Rapide de Praxis

## Option 1 : Test local avec Docker (Recommandé pour débuter)

```bash
cd praxis

# Démarrer tous les services (backend, frontend, DB, Redis)
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps

# Voir les logs
docker-compose logs -f
```

**Accès :**
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Documentation API : http://localhost:8000/docs
- PostgreSQL : localhost:5432

**Arrêter :**
```bash
docker-compose down
```

---

## Option 2 : Développement local sans Docker

### Backend
```bash
cd praxis

# Installer les dépendances Python
python -m pip install -r requirements.txt

# Copier le fichier d'environnement
cp .env.example .env

# Modifier .env avec vos configurations

# Lancer le backend
python -m uvicorn src.api.main:app --reload --port 8000
```

### Frontend
```bash
cd praxis

# Installer les dépendances Node
npm install

# Copier le fichier d'environnement
cp .env.local.example .env.local

# Modifier .env.local (mettre NEXT_PUBLIC_API_URL=http://localhost:8000)

# Lancer le frontend
npm run dev
```

**Accès :**
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000

---

## Option 3 : Déploiement en Production

### Architecture cible
- **Frontend** → Vercel (gratuit, optimisé Next.js)
- **Backend** → Google Cloud Run (scalable, pay-per-use)
- **Database** → Cloud SQL ou Render PostgreSQL

### Étapes rapides

#### 1. Base de données (Render - plus simple)
- Aller sur https://render.com
- Créer une base PostgreSQL gratuite
- Copier l'URL de connexion

#### 2. Backend sur Cloud Run
```bash
# Configurer gcloud
gcloud auth login
gcloud config set project VOTRE_PROJECT_ID

# Activer les APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Créer un registre
gcloud artifacts repositories create praxis-repo \
  --repository-format=docker \
  --location=europe-west1

# Build et push
docker build -f docker/Dockerfile.backend \
  -t europe-west1-docker.pkg.dev/VOTRE_PROJECT_ID/praxis-repo/praxis-backend:latest \
  .

docker push europe-west1-docker.pkg.dev/VOTRE_PROJECT_ID/praxis-repo/praxis-backend:latest

# Déployer
gcloud run deploy praxis-backend \
  --image europe-west1-docker.pkg.dev/VOTRE_PROJECT_ID/praxis-repo/praxis-backend:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=votre-url-postgres,SECRET_KEY=votre-clé-secrète
```

#### 3. Frontend sur Vercel
```bash
# Installer Vercel CLI
npm install -g vercel

# Se connecter
vercel login

# Déployer
cd praxis
vercel --prod
```

**Dans Vercel, ajouter la variable :**
- `NEXT_PUBLIC_API_URL` = URL du backend Cloud Run

---

## Option 4 : CI/CD Automatique (GitHub Actions)

Les workflows sont déjà configurés dans `.github/workflows/`.

### Secrets GitHub à ajouter
Allez dans `Settings → Secrets and variables → Actions` :

| Nom | Description |
|-----|-------------|
| `GCP_PROJECT_ID` | Votre projet Google Cloud |
| `GCP_SA_KEY` | Clé JSON du compte de service |
| `DATABASE_URL` | URL PostgreSQL complète |
| `SECRET_KEY` | Clé secrète (32+ caractères) |
| `VERCEL_TOKEN` | Token Vercel depuis vercel.com/account/tokens |

### Déclenchement
- Push sur `main` modifiant le backend → déploiement automatique sur Cloud Run
- Push sur `main` modifiant le frontend → déploiement automatique sur Vercel

---

## Vérification

### Tester le backend
```bash
curl http://localhost:8000/api/health
# ou en prod : curl https://praxis-backend-xxxx.run.app/api/health
```

### Tester le frontend
Ouvrez http://localhost:3000 (ou votre URL Vercel)

### Tester l'API
```bash
# Liste des tâches
curl http://localhost:8000/api/tasks

# Créer une tâche
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Mon test", "objective": "Tester"}'
```

---

## Problèmes courants

### "Connection refused" vers la DB
- Vérifiez que le container DB est démarré : `docker-compose ps`
- Vérifiez le `DATABASE_URL` dans `.env`

### Erreur CORS
- Assurez-vous que `CORS_ORIGINS` inclut l'URL du frontend
- Redémarrez le backend après modification

### Frontend ne se connecte pas au backend
- Vérifiez `NEXT_PUBLIC_API_URL` dans `.env.local` ou Vercel
- Redéployez le frontend après changement

### Migration DB nécessaire
```bash
# Avec Alembic
alembic upgrade head

# Avec Prisma
npx prisma migrate deploy
```

---

## Coûts estimés (production)

| Service | Coût mensuel |
|---------|--------------|
| Vercel Hobby | Gratuit |
| Cloud Run (usage faible) | 0-5 € |
| Cloud SQL db-f1-micro | ~8 € |
| **Total** | **~8-13 €/mois** |

**Astuce :** Utilisez Render PostgreSQL (gratuit) pour réduire les coûts.

---

## Pour aller plus loin

Consultez `README_DEPLOIEMENT_COMPLET.md` pour :
- Configuration détaillée de chaque service
- Gestion des secrets et sécurité
- Sauvegardes automatiques
- Surveillance et logs
- Authentification utilisateur
