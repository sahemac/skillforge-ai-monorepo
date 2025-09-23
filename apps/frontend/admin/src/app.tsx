import React from 'react';

const AdminApp: React.FC = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>SkillForge Admin Dashboard</h1>
      <p>Administration panel for the SkillForge AI Platform</p>
      <div style={{ 
        backgroundColor: '#fff5f5', 
        padding: '15px', 
        borderRadius: '8px',
        margin: '20px 0',
        border: '1px solid #fed7d7'
      }}>
        <h2>Module Federation Remote - Admin</h2>
        <p>This is the Admin micro-frontend module running independently.</p>
        <ul>
          <li>User Management</li>
          <li>Course Administration</li>
          <li>Analytics & Reports</li>
          <li>System Configuration</li>
          <li>Content Moderation</li>
        </ul>
      </div>
      <footer style={{ 
        marginTop: '40px', 
        padding: '10px', 
        borderTop: '1px solid #ddd',
        color: '#666'
      }}>
        Admin Module - SkillForge AI Platform
      </footer>
    </div>
  );
};

export default AdminApp;