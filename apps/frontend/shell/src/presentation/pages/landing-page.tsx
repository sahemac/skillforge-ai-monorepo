import React from 'react';

export const LandingPage: React.FC = () => {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '20px'
    }}>
      <div style={{ textAlign: 'center', maxWidth: '800px' }}>
        <h1 style={{ fontSize: '4rem', marginBottom: '1rem', fontWeight: 'bold' }}>
          SkillForge AI
        </h1>
        <p style={{ fontSize: '1.5rem', marginBottom: '2rem', opacity: 0.9 }}>
          Révolutionnez votre parcours professionnel avec l'intelligence artificielle
        </p>

        <div style={{
          backgroundColor: 'white',
          color: '#333',
          padding: '2rem',
          borderRadius: '12px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          marginTop: '2rem'
        }}>
          <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>
            Bienvenue sur SkillForge AI
          </h2>
          <p style={{ fontSize: '1.1rem', marginBottom: '1.5rem', lineHeight: '1.6' }}>
            La plateforme de développement des compétences alimentée par l'IA qui connecte
            les talents aux opportunités et transforme les carrières.
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
            marginTop: '2rem',
            textAlign: 'left'
          }}>
            <div style={{ padding: '1rem', backgroundColor: '#f7f7f7', borderRadius: '8px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', color: '#667eea' }}>
                🎯 Pour les Apprenants
              </h3>
              <p style={{ fontSize: '0.95rem', color: '#666' }}>
                Développez vos compétences avec des parcours personnalisés
              </p>
            </div>

            <div style={{ padding: '1rem', backgroundColor: '#f7f7f7', borderRadius: '8px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', color: '#667eea' }}>
                🏢 Pour les Entreprises
              </h3>
              <p style={{ fontSize: '0.95rem', color: '#666' }}>
                Trouvez les talents parfaits pour vos projets
              </p>
            </div>

            <div style={{ padding: '1rem', backgroundColor: '#f7f7f7', borderRadius: '8px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', color: '#667eea' }}>
                🤖 Powered by AI
              </h3>
              <p style={{ fontSize: '0.95rem', color: '#666' }}>
                Matching intelligent et recommandations personnalisées
              </p>
            </div>
          </div>

          <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button style={{
              padding: '12px 24px',
              backgroundColor: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1.1rem',
              cursor: 'pointer',
              fontWeight: '600'
            }}>
              Commencer Maintenant
            </button>
            <button style={{
              padding: '12px 24px',
              backgroundColor: 'transparent',
              color: '#667eea',
              border: '2px solid #667eea',
              borderRadius: '8px',
              fontSize: '1.1rem',
              cursor: 'pointer',
              fontWeight: '600'
            }}>
              En Savoir Plus
            </button>
          </div>
        </div>

        <div style={{ marginTop: '3rem', fontSize: '0.9rem', opacity: 0.9 }}>
          <p>✅ Déployé avec succès sur Google Cloud Run</p>
          <p>🌐 Accessible via: skillforge-ai.emacsah.com | api.emacsah.com</p>
        </div>
      </div>
    </div>
  );
};