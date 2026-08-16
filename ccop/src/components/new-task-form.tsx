'use client';

import { useState } from 'react';

export default function NewTaskForm() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description }),
      });

      if (res.ok) {
        setTitle('');
        setDescription('');
        setMessage({ type: 'success', text: 'Tâche créée avec succès!' });
        // Recharger la page pour afficher la nouvelle tâche
        setTimeout(() => window.location.reload(), 1000);
      } else {
        const data = await res.json();
        setMessage({ type: 'error', text: data.error || 'Erreur lors de la création' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Erreur de connexion au serveur' });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
      <h2 style={{ marginBottom: '15px' }}>Nouvelle tâche</h2>
      
      <div style={{ marginBottom: '10px' }}>
        <input
          type="text"
          placeholder="Titre de la tâche"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '16px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            boxSizing: 'border-box',
          }}
        />
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <textarea
          placeholder="Description (optionnel)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '14px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            resize: 'vertical',
            boxSizing: 'border-box',
          }}
        />
      </div>
      
      <button
        type="submit"
        disabled={loading || !title.trim()}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: loading ? '#ccc' : '#0070f3',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Création...' : 'Créer la tâche'}
      </button>
      
      {message && (
        <p style={{
          marginTop: '10px',
          color: message.type === 'success' ? 'green' : 'red',
        }}>
          {message.text}
        </p>
      )}
    </form>
  );
}
