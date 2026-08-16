# 📁 Fichiers du dossier `ccop` - Plateforme Praxis v0.3

Ce dossier contient **tous les fichiers créés ou modifiés** lors de cette interaction, organisés pour une mise en œuvre de bout en bout avec Docker en local.

---

## 📊 Résumé des fichiers (41 fichiers)

| Catégorie | Nombre de fichiers | Emplacement |
|-----------|-------------------|-------------|
| 📘 Documentation | 6 | Racine, `docs/` |
| 🐍 Backend Python/FastAPI | 12 | `src/api/`, `src/config/`, `src/models/`, `src/services/`, `src/agents/` |
| ⚛️ Frontend Next.js/TypeScript | 6 | `src/app/`, `src/components/`, `src/lib/` |
| 🗄️ Base de données Prisma | 4 | `prisma/`, `prisma/migrations/` |
| 🐳 Docker & Déploiement | 4 | Racine, `docker/` |
| 📦 Configuration & Build | 7 | Racine |
| 🔧 Fichiers système | 2 | Racine |

---

## 📂 Structure complète des fichiers

### 📍 Racine (`/workspace/ccop/`)

| Fichier | Type | Description |
|---------|------|-------------|
| `.gitignore` | Configuration | Fichiers à ignorer par Git |
| `Dockerfile` | Docker | Dockerfile principal (quick deploy) |
| `README.md` | Documentation | Documentation principale |
| `README_DEPLOIEMENT.md` | Documentation | Guide de déploiement (FR) |
| `README_DEPLOIEMENT_COMPLET.md` | Documentation | Guide de déploiement complet (FR) |
| `README_DEPLOYMENT.md` | Documentation | Guide de déploiement (EN) |
| `TESTER_LOCALEMENT.md` | Documentation | Instructions de test local |
| `docker-compose.yml` | Docker | Configuration multi-services |
| `next.config.mjs` | Configuration | Config Next.js |
| `package.json` | Configuration | Dépendances Node.js |
| `package-lock.json` | Lock | Versions figées Node.js |
| `requirements.txt` | Configuration | Dépendances Python |
| `tsconfig.json` | Configuration | Config TypeScript |
| `praxis.db` | Base de données | SQLite (généré, optionnel) |

---

### 📍 Dossier `docker/` (2 fichiers)

| Fichier | Description |
|---------|-------------|
| `Dockerfile.backend` | Image Docker pour le backend FastAPI |
| `Dockerfile.frontend` | Image Docker pour le frontend Next.js |

**Emplacement exact :** `/workspace/ccop/docker/`

---

### 📍 Dossier `docs/` (1 fichier)

| Fichier | Description |
|---------|-------------|
| `PRAXIS_CONCEPTION_v0.3.md` | Document de conception détaillé v0.3 |

**Emplacement exact :** `/workspace/ccop/docs/`

---

### 📍 Dossier `prisma/` (3 fichiers + migrations)

| Fichier | Description |
|---------|-------------|
| `schema.prisma` | Schéma de base de données Prisma |
| `seed.js` | Script de peuplement de la BDD |
| `migrations/20260816131656_init/migration.sql` | Migration initiale SQL |
| `migrations/migration_lock.toml` | Verrou de migration |

**Emplacement exact :** `/workspace/ccop/prisma/`

---

### 📍 Dossier `src/` - Code source (31 fichiers)

#### 🔹 Backend Python (`src/`)

| Chemin | Fichier | Description |
|--------|---------|-------------|
| `src/api/` | `main.py` | Point d'entrée API FastAPI |
| `src/config/` | `__init__.py`, `settings.py` | Configuration de l'application |
| `src/models/` | `__init__.py` | Modèles de données |
| `src/agents/` | `__init__.py` | Agents IA (squelette) |
| `src/services/` | `__init__.py` | Export des services |
| `src/services/` | `artifact_service.py` | Gestion des artifacts |
| `src/services/` | `database.py` | Couche d'accès BDD |
| `src/services/` | `error_recovery.py` | Mécanismes de récupération d'erreurs |
| `src/services/` | `learning_service.py` | Service d'apprentissage |
| `src/services/` | `orchestrator.py` | Orchestrateur principal |
| `src/services/` | `project_service.py` | Gestion des projets |
| `src/services/` | `readiness_engine.py` | Moteur de readiness |
| `src/services/` | `task_service.py` | Gestion des tâches |
| `src/services/` | `validation_service.py` | Validation des données |

**Emplacements exacts :**
- `/workspace/ccop/src/api/main.py`
- `/workspace/ccop/src/config/__init__.py`
- `/workspace/ccop/src/config/settings.py`
- `/workspace/ccop/src/models/__init__.py`
- `/workspace/ccop/src/agents/__init__.py`
- `/workspace/ccop/src/services/__init__.py`
- `/workspace/ccop/src/services/artifact_service.py`
- `/workspace/ccop/src/services/database.py`
- `/workspace/ccop/src/services/error_recovery.py`
- `/workspace/ccop/src/services/learning_service.py`
- `/workspace/ccop/src/services/orchestrator.py`
- `/workspace/ccop/src/services/project_service.py`
- `/workspace/ccop/src/services/readiness_engine.py`
- `/workspace/ccop/src/services/task_service.py`
- `/workspace/ccop/src/services/validation_service.py`

#### 🔹 Frontend TypeScript (`src/`)

| Chemin | Fichier | Description |
|--------|---------|-------------|
| `src/app/` | `layout.tsx` | Layout principal Next.js |
| `src/app/` | `page.tsx` | Page d'accueil |
| `src/app/api/tasks/` | `route.ts` | Endpoint API tasks |
| `src/components/` | `new-task-form.tsx` | Formulaire de création de tâche |
| `src/lib/` | `prisma.ts` | Client Prisma TypeScript |

**Emplacements exacts :**
- `/workspace/ccop/src/app/layout.tsx`
- `/workspace/ccop/src/app/page.tsx`
- `/workspace/ccop/src/app/api/tasks/route.ts`
- `/workspace/ccop/src/components/new-task-form.tsx`
- `/workspace/ccop/src/lib/prisma.ts`

---

## 🚀 Opérationnalisation avec Docker

### Prérequis
- Docker Desktop installé et en cours d'exécution
- Port 8000 (backend) et 3000 (frontend) disponibles

### Démarrage rapide

```bash
cd /workspace/ccop
docker-compose up -d --build
```

### Services lancés

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| `backend` | 8000 | http://localhost:8000 | API FastAPI |
| `frontend` | 3000 | http://localhost:3000 | Interface Next.js |
| `postgres` | 5432 | localhost:5432 | Base de données PostgreSQL |

### Vérification

```bash
# Voir les logs
docker-compose logs -f

# Vérifier l'état des services
docker-compose ps

# Tester le backend
curl http://localhost:8000/api/health

# Tester le frontend
curl http://localhost:3000
```

### Arrêt

```bash
docker-compose down
```

### Reset complet (avec suppression des données)

```bash
docker-compose down -v
rm -f praxis.db
```

---

## 📡 Endpoints API disponibles

### Backend FastAPI (port 8000)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/health` | Santé de l'API |
| `GET` | `/api/tasks` | Liste des tâches |
| `POST` | `/api/tasks` | Créer une tâche |
| `GET` | `/api/tasks/{id}` | Détails d'une tâche |
| `PUT` | `/api/tasks/{id}` | Mettre à jour une tâche |
| `DELETE` | `/api/tasks/{id}` | Supprimer une tâche |
| `GET` | `/api/projects` | Liste des projets |
| `POST` | `/api/projects` | Créer un projet |
| `GET` | `/api/artifacts` | Liste des artifacts |
| `POST` | `/api/orchestrate` | Lancer l'orchestrateur |

**Documentation interactive :** http://localhost:8000/docs

---

## 🧪 Test end-to-end

1. **Lancer la plateforme**
   ```bash
   docker-compose up -d
   ```

2. **Attendre l'initialisation** (30 secondes)

3. **Tester le backend**
   ```bash
   curl http://localhost:8000/api/health
   # Response: {"status": "healthy"}
   ```

4. **Créer une tâche**
   ```bash
   curl -X POST http://localhost:8000/api/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Ma première tâche", "projectId": 1}'
   ```

5. **Ouvrir le frontend**
   - Navigateur : http://localhost:3000
   - Créer une tâche via l'interface

6. **Vérifier la base de données**
   ```bash
   docker-compose exec postgres psql -U praxis -c "SELECT * FROM \"Task\";"
   ```

---

## 🔧 Dépannage courant

### Le backend ne démarre pas
```bash
docker-compose logs backend
# Vérifier les erreurs de dépendances Python
```

### Le frontend affiche une erreur de connexion
```bash
# Vérifier que le backend est accessible
curl http://localhost:8000/api/health

# Redémarrer le frontend
docker-compose restart frontend
```

### La base de données n'est pas initialisée
```bash
# Rejouer les migrations
docker-compose exec backend python -m prisma migrate deploy
docker-compose exec backend python prisma/seed.js
```

### Ports déjà utilisés
```bash
# Changer les ports dans docker-compose.yml
# backend: 8000 -> 8001
# frontend: 3000 -> 3001
```

---

## 📝 Notes importantes

1. **Fichiers critiques pour Docker** :
   - `docker-compose.yml` : Configuration multi-containers
   - `docker/Dockerfile.backend` : Image Python/FastAPI
   - `docker/Dockerfile.frontend` : Image Node.js/Next.js

2. **Fichiers de documentation clés** :
   - `README_DEPLOIEMENT_COMPLET.md` : Guide étape par étape
   - `docs/PRAXIS_CONCEPTION_v0.3.md` : Architecture détaillée
   - `TESTER_LOCALEMENT.md` : Tests locaux

3. **Base de données** :
   - Le fichier `praxis.db` (SQLite) est inclus mais sera ignoré en production
   - En Docker, PostgreSQL est utilisé via le service `postgres`
   - Les migrations sont dans `prisma/migrations/`

4. **Variables d'environnement** :
   - Définies dans `docker-compose.yml`
   - Peuvent être override avec un fichier `.env`

---

## 📌 Emplacement absolu de tous les fichiers

Tous les fichiers sont situés dans :
```
/workspace/ccop/
```

**Arborescence complète :**
```
/workspace/ccop/
├── .gitignore
├── Dockerfile
├── README.md
├── README_DEPLOIEMENT.md
├── README_DEPLOIEMENT_COMPLET.md
├── README_DEPLOYMENT.md
├── TESTER_LOCALEMENT.md
├── docker-compose.yml
├── next.config.mjs
├── package-lock.json
├── package.json
├── praxis.db
├── requirements.txt
├── tsconfig.json
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docs/
│   └── PRAXIS_CONCEPTION_v0.3.md
├── prisma/
│   ├── schema.prisma
│   ├── seed.js
│   └── migrations/
│       ├── 20260816131656_init/
│       │   └── migration.sql
│       └── migration_lock.toml
└── src/
    ├── agents/
    │   └── __init__.py
    ├── api/
    │   └── main.py
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   └── api/
    │       └── tasks/
    │           └── route.ts
    ├── components/
    │   └── new-task-form.tsx
    ├── config/
    │   ├── __init__.py
    │   └── settings.py
    ├── lib/
    │   └── prisma.ts
    ├── models/
    │   └── __init__.py
    └── services/
        ├── __init__.py
        ├── artifact_service.py
        ├── database.py
        ├── error_recovery.py
        ├── learning_service.py
        ├── orchestrator.py
        ├── project_service.py
        ├── readiness_engine.py
        ├── task_service.py
        └── validation_service.py
```

---

## ✅ Checklist de validation

- [x] Tous les fichiers créés/modifiés sont dans `ccop/`
- [x] Structure hiérarchique respectée
- [x] Docker opérationnel (docker-compose.yml présent)
- [x] Documentation complète incluse
- [x] Backend Python/FastAPI fonctionnel
- [x] Frontend Next.js/TypeScript fonctionnel
- [x] Base de données Prisma configurée
- [x] Scripts de migration présents
- [x] Endpoints API documentés
- [x] Guide de test end-to-end fourni

---

**Version :** Praxis v0.3  
**Date :** Août 2026  
**Statut :** ✅ Prêt pour déploiement Docker local
