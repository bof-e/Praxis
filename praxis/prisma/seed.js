const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function main() {
  // Créer un utilisateur local
  const user = await prisma.user.upsert({
    where: { email: 'local@praxis.dev' },
    update: {},
    create: {
      email: 'local@praxis.dev',
      name: 'Utilisateur Local',
    },
  });

  console.log('Utilisateur créé:', user);

  // Créer un projet "Praxis Pilote"
  const project = await prisma.project.create({
    data: {
      name: 'Praxis Pilote',
      description: 'Projet pilote pour le système Praxis',
      userId: user.id,
    },
  });

  console.log('Projet créé:', project);

  // Créer une tâche pilote
  const task = await prisma.task.create({
    data: {
      title: 'Analyser ENQUETE_STAT_PRAXIS_PILOTE_COMPLET.xlsx',
      description: 'Tâche pilote pour analyser le fichier Excel de l\'enquête',
      status: 'pending',
      userId: user.id,
      projectId: project.id,
    },
  });

  console.log('Tâche créée:', task);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
