# Praxis MVP

Système de travail intelligent personnel - MVP local.

## Stack

- Next.js App Router
- TypeScript
- Prisma
- SQLite local

## Installation

```bash
npm install
npx prisma migrate dev --name init
npm run prisma:seed
npm run dev
```

L'application sera accessible sur http://localhost:3000

## Modèles de données

- User
- Project
- Task
- Plan
- Execution
- Artifact
- Learning
- KnowledgeItem
- Tool
