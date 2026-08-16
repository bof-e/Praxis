import { prisma } from '@/lib/prisma';
import NewTaskForm from '@/components/new-task-form';

async function getTasks() {
  const tasks = await prisma.task.findMany({
    include: {
      project: true,
      user: true,
    },
    orderBy: { createdAt: 'desc' },
  });
  return tasks;
}

export default async function Home() {
  const tasks = await getTasks();

  return (
    <main style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '20px' }}>Praxis MVP - Tâches</h1>
      
      <NewTaskForm />
      
      <h2 style={{ marginTop: '30px', marginBottom: '15px' }}>Liste des tâches</h2>
      
      {tasks.length === 0 ? (
        <p>Aucune tâche pour le moment.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {tasks.map((task) => (
            <li
              key={task.id}
              style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '15px',
                marginBottom: '10px',
                backgroundColor: '#fafafa',
              }}
            >
              <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{task.title}</div>
              {task.description && (
                <div style={{ color: '#666', marginBottom: '5px' }}>{task.description}</div>
              )}
              <div style={{ fontSize: '0.9em', color: '#888' }}>
                <span>Statut: {task.status}</span>
                {task.project && (
                  <span style={{ marginLeft: '15px' }}>Projet: {task.project.name}</span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
