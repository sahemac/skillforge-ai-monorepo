import React from 'react';
import ReactDOM from 'react-dom/client';
import './presentation/styles/global.css';
import { App } from './app-public';

console.log('🚀 SkillForge AI - Starting with public pages (Landing, Mission, Contact)...');

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

console.log('✅ Application ready');
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
