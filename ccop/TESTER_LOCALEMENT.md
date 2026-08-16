# 🧪 Guide de Test Local - Praxis MVP

## Démarrage rapide en 3 commandes

### Option A : Avec Docker (Recommandé)

```bash
cd praxis

# 1. Tout démarrer (backend + frontend + DB)
docker-compose up -d

# 2. Attendre 30 secondes que les services initialisent

# 3. Tester
curl http://localhost:8000/api/health
```

**Accès :**
- 🌐 Frontend : http://localhost:3000
- 🔧 API Backend : http://localhost:8000
- 📚 Docs API (Swagger) : http://localhost:8000/docs
- 💾 PostgreSQL : localhost:5432 (user: postgres, password: postgres)

**Voir les logs :**
```bash
docker-compose logs -f
```

**Arrêter :**
```bash
docker-compose down
```

---

### Option B : Sans Docker (Développement)

#### Terminal 1 : Backend
```bash
cd praxis

# Installer les dépendances (si pas déjà fait)
python -m pip install -r requirements.txt

# Copier la config
cp .env.example .env

# Lancer le backend
python -m uvicorn src.api.main:app --reload --port 8000
```

#### Terminal 2 : Frontend
```bash
cd praxis

# Installer les dépendances (si pas déjà fait)
npm install

# Copier la config
cp .env.local.example .env.local

# Lancer le frontend
npm run dev
```

**Accès :**
- 🌐 Frontend : http://localhost:3000
- 🔧 API Backend : http://localhost:8000

---

## Tests fonctionnels

### 1. Vérifier que le backend répond
```bash
curl http://localhost:8000/api/health
# Doit retourner : {"status":"ok"}
```

### 2. Liste des tâches (doit être vide au début)
```bash
curl http://localhost:8000/api/tasks
# Doit retourner : []
```

### 3. Créer une première tâche
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mon premier test",
    "objective": "Vérifier que Praxis fonctionne",
    "type": "analyse_donnees",
    "domain": "statistiques"
  }'
```

### 4. Récupérer la tâche créée
```bash
curl http://localhost:8000/api/tasks/1
```

### 5. Tester le Readiness Engine
```bash
curl -X POST http://localhost:8000/api/tasks/1/readiness
```

### 6. Tester un Agent (Understanding Agent)
```bash
curl -X POST http://localhost:8000/api/agents/understanding/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "raw_request": "Analyse ce fichier Excel et fais un rapport"
  }'
```

---

## Tests via l'interface web

1. Ouvrez http://localhost:3000
2. Cliquez sur "Nouvelle tâche"
3. Remplissez le formulaire :
   - Titre : "Test MVP"
   - Objectif : "Valider le déploiement"
   - Type : "Rapport"
   - Domaine : "Suivi-évaluation"
4. Soumettez
5. Vérifiez que la tâche apparaît dans la liste
6. Cliquez dessus pour voir les détails

---

## Tests des composants clés (selon PRAXIS_CONCEPTION_v0.3.md)

### ✅ Architecture v0.3 implémentée

| Composant | Statut | Comment tester |
|-----------|--------|----------------|
| **Orchestrator** | ✅ Implementé | Via création de tâche → vérifiez les logs backend |
| **Task** | ✅ Implementé | `GET /api/tasks` |
| **Project** | ✅ Implementé | `GET /api/projects` |
| **Readiness Engine** | ✅ Implementé | `POST /api/tasks/{id}/readiness` |
| **Context** | ✅ Implementé | Automatique lors de la contextualisation |
| **Plan** | ✅ Implementé | `POST /api/tasks/{id}/plan` |
| **Agents** | ✅ Implementé | `/api/agents/{agent_type}` |
| **Artifacts** | ✅ Implementé | `GET /api/tasks/{id}/artifacts` |
| **Deliverables** | ✅ Implementé | Marqués dans les artifacts |
| **Job Queue** | ⏳ Phase 3 | Synchrone en MVP |
| **KnowledgeBase** | ⏳ Phase 3 | Vide en MVP |
| **Learning** | ⏳ Phase 3 | Journalisation seule en MVP |
| **Error Recovery** | ✅ Basique | Retry automatique |
| **Dependency** | ✅ Implementé | `POST /api/projects/{id}/dependencies` |
| **Source/Evidence** | ✅ Non-bloquant | Traçabilité optionnelle en MVP |

---

## Scénario de test complet (Cas Pilote)

**Objectif :** Analyse d'un fichier Excel → Rapport + Présentation

### Étape 1 : Créer le projet
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Analyse enquête ménage",
    "description": "Analyse complète des données d'enquête",
    "objectives": ["Produire un rapport", "Créer une présentation"]
  }'
```

### Étape 2 : Créer la tâche
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Analyse données Excel",
    "objective": "Nettoyer et analyser les données, produire rapports",
    "type": "analyse_donnees",
    "domain": "statistiques",
    "project_id": 1,
    "deliverables": ["rapport.docx", "presentation.pptx"],
    "autonomy_level": 1
  }'
```

### Étape 3 : Calculer le readiness score
```bash
curl -X POST http://localhost:8000/api/tasks/1/readiness
```

### Étape 4 : Générer le plan
```bash
curl -X POST http://localhost:8000/api/tasks/1/plan
```

### Étape 5 : Valider le plan (niveau 1 = validation humaine requise)
```bash
curl -X POST http://localhost:8000/api/tasks/1/plan/validate \
  -H "Content-Type: application/json" \
  -d '{"validated": true}'
```

### Étape 6 : Exécuter
```bash
curl -X POST http://localhost:8000/api/tasks/1/execute
```

### Étape 7 : Vérifier les artifacts produits
```bash
curl http://localhost:8000/api/tasks/1/artifacts
```

### Étape 8 : Valider le livrable final
```bash
curl -X POST http://localhost:8000/api/tasks/1/deliverable/validate \
  -H "Content-Type: application/json" \
  -d '{"validated": true}'
```

---

## Métriques à vérifier (selon §14 de PRAXIS_CONCEPTION_v0.3.md)

Après plusieurs tests, vérifiez :

```bash
# Taux de complétion
curl http://localhost:8000/api/metrics/completion-rate

# Taux de succès au premier passage
curl http://localhost:8000/api/metrics/first-pass-success

# Écart durée estimée vs réelle
curl http://localhost:8000/api/metrics/duration-accuracy

# Taux d'intervention utilisateur
curl http://localhost:8000/api/metrics/user-intervention
```

⚠️ **Note :** Ces métriques seront disponibles à partir de la Phase 3. En MVP, consultez les logs manuellement.

---

## Dépannage

### Le backend ne démarre pas
```bash
# Vérifier les dépendances Python
pip install -r requirements.txt

# Vérifier le port
lsof -i :8000

# Voir les erreurs
python -m uvicorn src.api.main:app --reload --port 8000
```

### La base de données n'est pas accessible
```bash
# Avec Docker
docker-compose ps
docker-compose logs db

# Sans Docker (SQLite)
ls -la praxis.db
```

### Erreur de migration
```bash
# Reset de la DB (dev seulement !)
rm praxis.db
python src/scripts/init_db.py
```

### Le frontend ne se connecte pas
```bash
# Vérifier .env.local
cat .env.local
# NEXT_PUBLIC_API_URL doit être http://localhost:8000

# Redémarrer le frontend
npm run dev
```

### CORS error dans le navigateur
```bash
# Vérifier CORS_ORIGINS dans .env
cat .env
# Doit inclure http://localhost:3000

# Redémarrer le backend
```

---

## Logs et débogage

### Backend
```bash
# Logs en temps réel
docker-compose logs -f backend

# Ou sans Docker
# Les logs s'affichent dans le terminal où uvicorn tourne
```

### Frontend
```bash
# Logs en temps réel
docker-compose logs -f frontend

# Ou sans Docker
# Les logs Next.js s'affichent dans le terminal
```

### Base de données
```bash
# Voir les tables (Docker)
docker-compose exec db psql -U postgres -d praxis -c "\dt"

# Voir les tâches
docker-compose exec db psql -U postgres -d praxis -c "SELECT * FROM tasks;"
```

---

## Prochaines étapes après les tests locaux

1. ✅ Tests locaux validés
2. 📦 Déploiement sur Vercel + Cloud Run (voir `README_DEPLOYMENT.md`)
3. 🔐 Configuration authentification
4. 📊 Activation des métriques de performance
5. 🧠 Alimentation de KnowledgeBase (Phase 3)
6. 🤖 Autonomie niveau 2-3 (après tâches éprouvées)

---

## Support

Pour toute question ou bug :
1. Vérifiez les logs
2. Consultez `PRAXIS_CONCEPTION_v0.3.md` dans `docs/`
3. Vérifiez `README_DEPLOIEMENT_COMPLET.md` pour la production
