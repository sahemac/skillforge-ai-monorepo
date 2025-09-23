import React from 'react';

const CompanyApp: React.FC = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>SkillForge Company Portal</h1>
      <p>Enterprise management portal for organizations</p>
      <div style={{ 
        backgroundColor: '#f7fafc', 
        padding: '15px', 
        borderRadius: '8px',
        margin: '20px 0',
        border: '1px solid #e2e8f0'
      }}>
        <h2>Module Federation Remote - Company</h2>
        <p>This is the Company micro-frontend module running independently.</p>
        <ul>
          <li>Team Management</li>
          <li>Training Programs</li>
          <li>Performance Analytics</li>
          <li>Compliance Tracking</li>
          <li>Skills Assessment</li>
          <li>Budget Management</li>
        </ul>
      </div>
      <footer style={{ 
        marginTop: '40px', 
        padding: '10px', 
        borderTop: '1px solid #ddd',
        color: '#666'
      }}>
        Company Module - SkillForge AI Platform
      </footer>
    </div>
  );
};

export default CompanyApp;