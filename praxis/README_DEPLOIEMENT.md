# Déploiement et Test de Praxis MVP

## État actuel

✅ **Application déployée et fonctionnelle**

L'application est actuellement en cours d'exécution sur **http://localhost:3000**

## Architecture implémentée (v0.3)

### Backend (Python/FastAPI)
- **Orchestrator** (`src/services/orchestrator.py`) - Coordonne le cycle de vie des tâches
- **Readiness Engine** (`src/services/readiness_engine.py`) - Calcule les scores de préparation
- **Task Service** (`src/services/task_service.py`) - Gestion des tâches
- **Project Service** (`src/services/project_service.py`) - Gestion des projets
- **Artifact Service** (`src/services/artifact_service.py`) - Gestion des artefacts
- **Validation Service** (`src/services/validation_service.py`) - Contrôle qualité
- **Learning Service** (`src/services/learning_service.py`) - Apprentissage
- **Error Recovery** (`src/services/error_recovery.py`) - Gestion des erreurs

### Frontend (Next.js/React)
- Interface utilisateur avec liste des tâches
- Formulaire de création de tâches
- Design responsive simple

### Base de données (SQLite + Prisma)
- Modèles: User, Project, Task, Plan, Execution, Artifact, Learning, KnowledgeItem, Tool
- Données de seed: Utilisateur test + Projet pilote + Tâche exemple

## Comment tester

### 1. Accéder à l'interface web
Ouvrez votre navigateur et allez sur: **http://localhost:3000**

Vous verrez:
- Un formulaire pour créer une nouvelle tâche
- La liste des tâches existantes (dont la tâche pilote "Analyser ENQUETE_STAT_PRAXIS_PILOTE_COMPLET.xlsx")

### 2. Tester via l'API (optionnel)
L'API FastAPI peut être lancée séparément:
```bash
cd /workspace/praxis
python -m uvicorn src.api.main:app --reload --port 8000
```

Puis testez avec:
```bash
curl http://localhost:8000/api/tasks
```

### 3. Consulter la documentation
Le cahier de conception v0.3 est dans `docs/PRAXIS_CONCEPTION_v0.3.md`

## Fonctionnalités MVP implémentées

✅ Création et visualisation de tâches
✅ Structure de projets
✅ Modèle de données complet (Prisma)
✅ Services backend selon architecture v0.3
✅ Base de connaissances (KnowledgeBase) prête
✅ Système d'artefacts avec provenance
✅ Moteur de readiness
✅ Gestion d'erreurs basique

## Prochaines étapes recommandées

1. **Tester le cas pilote**: Créer une tâche d'analyse de fichier Excel
2. **Ajouter l'interface de projet**: Visualiser le graphe de dépendances
3. **Implémenter les Agents**: Data Analysis Agent, Document Agent, etc.
4. **Ajouter les outils**: pandas, python-docx, python-pptx
5. **Interface de validation**: Checkpoints humains selon le niveau d'autonomie

## Arrêter/Redémarrer le serveur

```bash
# Trouver le processus
ps aux | grep "next dev"

# Arrêter
kill <PID>

# Redémarrer
npm run dev
```

## Fichiers importants

- `.env` - Variables d'environnement (DATABASE_URL)
- `prisma/schema.prisma` - Schéma de base de données
- `praxis.db` - Base de données SQLite
- `src/app/page.tsx` - Page d'accueil
- `src/components/new-task-form.tsx` - Formulaire de création
- `src/services/*.py` - Services backend Python
