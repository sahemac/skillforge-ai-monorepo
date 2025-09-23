import React from 'react';

const LearnerApp: React.FC = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>SkillForge Learner Dashboard</h1>
      <p>Welcome to the SkillForge Learning Platform!</p>
      <div style={{ 
        backgroundColor: '#f0f8ff', 
        padding: '15px', 
        borderRadius: '8px',
        margin: '20px 0'
      }}>
        <h2>Module Federation Remote - Learner</h2>
        <p>This is the Learner micro-frontend module running independently.</p>
        <ul>
          <li>Course Progress Tracking</li>
          <li>Skill Assessment</li>
          <li>Learning Path Recommendations</li>
          <li>Achievement System</li>
        </ul>
      </div>
      <footer style={{ 
        marginTop: '40px', 
        padding: '10px', 
        borderTop: '1px solid #ddd',
        color: '#666'
      }}>
        Learner Module - SkillForge AI Platform
      </footer>
    </div>
  );
};

export default LearnerApp;