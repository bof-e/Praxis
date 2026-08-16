# Guide de Déploiement Praxis - Architecture Séparée

## Vue d'ensemble

Praxis est déployé avec une architecture séparée :
- **Frontend Next.js** → Hébergé sur **Vercel** (optimisé pour Next.js, CDN, SSL automatique)
- **Backend Python (FastAPI)** → Hébergé sur **Google Cloud Run** (container scalable)
- **Base de données** → **PostgreSQL managé** (Cloud SQL ou Render PostgreSQL)

Cette séparation offre scalabilité, maintenabilité et coût optimisé.

---

## Prérequis

### Comptes nécessaires
1. Compte GitHub (déjà configuré)
2. Compte Vercel (gratuit pour usage personnel)
3. Compte Google Cloud Platform
4. Service de base de données PostgreSQL managé (Cloud SQL ou Render)

### Variables d'environnement à configurer

#### Dans GitHub Secrets (Settings → Secrets and variables → Actions)
```
GCP_PROJECT_ID=votre-project-id
GCP_SA_KEY={clé JSON du compte de service GCP}
DATABASE_URL=postgresql://user:password@host:5432/praxis
SECRET_KEY=votre-clé-secrète-pour-sessions-jwt
VERCEL_TOKEN=votre-token-Vercel
```

#### Dans Vercel (Project Settings → Environment Variables)
```
NEXT_PUBLIC_API_URL=https://praxis-backend-xxxx.run.app
```

---

## Étape 1 : Configuration de la base de données PostgreSQL

### Option A : Cloud SQL (Google Cloud)
```bash
# Créer une instance Cloud SQL
gcloud sql instances create praxis-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=europe-west1 \
  --root-password=votre-mot-de-pass-root

# Créer la base de données
gcloud sql databases create praxis --instance=praxis-db

# Créer un utilisateur
gcloud sql users create praxis_user \
  --instance=praxis-db \
  --password=votre-mot-de-passe
```

Récupérer le `DATABASE_URL` :
```
postgresql://praxis_user:votre-mot-de-passe@/praxis?host=/cloudsql/project:europe-west1:praxis-db
```

### Option B : Render PostgreSQL (plus simple)
1. Aller sur https://render.com
2. Créer une nouvelle base PostgreSQL (plan gratuit disponible)
3. Copier l'URL de connexion fournie

---

## Étape 2 : Configuration du backend sur Google Cloud Run

### 2.1 Activer les APIs nécessaires
```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2.2 Créer un registre Artifact Registry
```bash
gcloud artifacts repositories create praxis-repo \
  --repository-format=docker \
  --location=europe-west1 \
  --description="Registre Docker pour Praxis"
```

### 2.3 Créer un compte de service pour le déploiement
```bash
gcloud iam service-accounts create praxis-deployer \
  --display-name="Praxis Deployer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:praxis-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:praxis-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud iam service-accounts keys create gcp-sa-key.json \
  --iam-account=praxis-deployer@$PROJECT_ID.iam.gserviceaccount.com
```

Le fichier `gcp-sa-key.json` doit être encodé en base64 et ajouté aux secrets GitHub :
```bash
cat gcp-sa-key.json | base64 -w 0
```

### 2.4 Déploiement manuel initial (optionnel, avant CI/CD)
```bash
cd praxis

# Build de l'image
docker build -f docker/Dockerfile.backend \
  -t europe-west1-docker.pkg.dev/$PROJECT_ID/praxis-repo/praxis-backend:latest \
  .

# Push
docker push europe-west1-docker.pkg.dev/$PROJECT_ID/praxis-repo/praxis-backend:latest

# Déploiement
gcloud run deploy praxis-backend \
  --image europe-west1-docker.pkg.dev/$PROJECT_ID/praxis-repo/praxis-backend:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL,SECRET_KEY=$SECRET_KEY \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

Notez l'URL du backend : `https://praxis-backend-xxxx.run.app`

---

## Étape 3 : Configuration du frontend sur Vercel

### 3.1 Installer Vercel CLI localement
```bash
npm install -g vercel
```

### 3.2 Se connecter à Vercel
```bash
vercel login
```

### 3.3 Initialiser le projet Vercel
```bash
cd praxis
vercel init
```

Suivez les instructions :
- Framework preset : Next.js
- Root directory : `.` (ou laissez par défaut)
- Build Command : `npm run build`
- Output Directory : `.next`

### 3.4 Configurer les variables d'environnement dans Vercel
```bash
# Dans l'interface Vercel ou via CLI
vercel env add NEXT_PUBLIC_API_URL production
# Entrez l'URL de votre backend Cloud Run
```

### 3.5 Premier déploiement manuel
```bash
cd praxis
vercel --prod
```

---

## Étape 4 : Configuration du CI/CD GitHub Actions

Les workflows sont déjà créés dans `.github/workflows/` :

### `deploy-backend.yml`
Se déclenche lors des pushes sur `main` modifiant le backend.
- Build l'image Docker
- Push vers Artifact Registry
- Dé dé dé dé dé deploie sur Cloud Run

### `deploy-frontend.yml`
Se déclenche lors des pushes sur `main` modifiant le frontend.
- Installe Vercel CLI
- Pull les configs Vercel
- Build et déploie sur Vercel

### Ajouter les secrets GitHub
Allez dans `Settings → Secrets and variables → Actions` et ajoutez :

| Nom | Valeur |
|-----|--------|
| `GCP_PROJECT_ID` | Votre projet GCP |
| `GCP_SA_KEY` | Contenu JSON de `gcp-sa-key.json` |
| `DATABASE_URL` | URL PostgreSQL complète |
| `SECRET_KEY` | Clé secrète aléatoire (32+ caractères) |
| `VERCEL_TOKEN` | Token depuis https://vercel.com/account/tokens |

---

## Étape 5 : Migration de la base de données

### Avec Alembic (recommandé pour Python/FastAPI)
```bash
cd praxis

# Installer alembic si pas déjà fait
pip install alembic

# Initialiser alembic (une seule fois)
alembic init alembic

# Configurer alembic.ini avec DATABASE_URL

# Créer une migration
alembic revision --autogenerate -m "Initial schema"

# Appliquer les migrations
alembic upgrade head
```

### Avec Prisma (si utilisé côté Node)
```bash
cd praxis
npx prisma migrate deploy
npx prisma db seed
```

---

## Étape 6 : Vérification du déploiement

### Backend
```bash
curl https://praxis-backend-xxxx.run.app/api/health
# Doit retourner : {"status": "ok"}
```

### Frontend
Ouvrez https://votre-app.vercel.app dans un navigateur.

### Tests API
```bash
# Liste des tâches
curl https://praxis-backend-xxxx.run.app/api/tasks

# Créer une tâche
curl -X POST https://praxis-backend-xxxx.run.app/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "objective": "Tester le déploiement"}'
```

---

## Dépannage

### Le backend ne démarre pas sur Cloud Run
1. Vérifiez les logs : `gcloud run services logs read praxis-backend`
2. Vérifiez que `DATABASE_URL` est correcte
3. Testez localement avec Docker : `docker run -p 8000:8000 -e DATABASE_URL=... praxis-backend`

### Le frontend ne se connecte pas au backend
1. Vérifiez `NEXT_PUBLIC_API_URL` dans Vercel
2. Assurez-vous que le backend autorise les CORS (voir `src/api/main.py`)
3. Redéployez le frontend après changement de variable

### Erreurs de migration DB
1. Connectez-vous à la DB en local pour déboguer
2. Vérifiez que les extensions nécessaires sont activées
3. Exécutez les migrations manuellement

---

## Coûts estimés (usage personnel)

| Service | Plan | Coût mensuel estimé |
|---------|------|---------------------|
| Vercel | Hobby (gratuit) | 0 € |
| Cloud Run | Pay-per-use | 0-5 € (selon usage) |
| Cloud SQL | db-f1-micro | ~5-10 € |
| **Total** | | **~5-15 €/mois** |

Pour réduire les coûts :
- Utiliser Render PostgreSQL (gratuit avec limitations)
- Cloud Run avec `min-instances=0` (pas de coût à l'arrêt)
- Fly.io comme alternative à Cloud Run (offre gratuite généreuse)

---

## Alternatives de déploiement

### Backend sur Render (sans Docker)
1. Créer un nouveau service Web sur Render
2. Connecter le repo GitHub
3. Build command : `pip install -r requirements.txt`
4. Start command : `gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
5. Ajouter les variables d'environnement

### Backend sur Fly.io
```bash
flyctl launch --image europe-west1-docker.pkg.dev/$PROJECT_ID/praxis-repo/praxis-backend:latest
flyctl secrets set DATABASE_URL=... SECRET_KEY=...
```

### Tout-en-un sur Fly.io (frontend + backend)
Voir `docker-compose.yml` pour une approche monolithique (moins scalable mais plus simple).

---

## Maintenance

### Mettre à jour le backend
```bash
git push origin main
# Le workflow GitHub Actions se déclenche automatiquement
```

### Mettre à jour le frontend
```bash
git push origin main
# Le workflow GitHub Actions se déclenche automatiquement
```

### Voir les logs
```bash
# Backend Cloud Run
gcloud run services logs read praxis-backend

# Frontend Vercel
vercel logs <deployment-url>
```

### Sauvegarder la base de données
```bash
# Cloud SQL
gcloud sql backups create --instance=praxis-db

# Ou exporter vers Cloud Storage
gcloud sql export sql praxis-db gs://votre-bucket/backup-$(date +%Y%m%d).sql
```

---

## Sécurité

- ✅ HTTPS automatique (Vercel + Cloud Run)
- ✅ Variables d'environnement sécurisées (GitHub Secrets, Vercel Env)
- ✅ Compte de service avec permissions minimales
- ✅ Base de données avec accès restreint (IP whitelist si possible)
- ⚠️ À ajouter : Rate limiting, authentification utilisateur

---

## Prochaines étapes

1. **Configurer l'authentification** (NextAuth.js côté frontend, JWT côté backend)
2. **Ajouter un domaine personnalisé** (Vercel + Cloud Run)
3. **Mettre en place la surveillance** (Cloud Monitoring, Sentry)
4. **Configurer les sauvegardes automatiques** de la base de données
5. **Documenter l'API** avec OpenAPI/Swagger (automatique avec FastAPI)
