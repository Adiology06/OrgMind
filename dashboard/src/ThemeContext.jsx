import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(true);

  const toggleTheme = () => setIsDark(!isDark);

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      // 🌙 DARK MODE (Keep existing colors exactly as they were)
      root.style.setProperty('--bg-main', '#0a0a0f');
      root.style.setProperty('--bg-sidebar', '#0d0d1a');
      root.style.setProperty('--bg-card', '#0d0d1a');
      root.style.setProperty('--bg-secondary', '#1a1a2e'); 
      root.style.setProperty('--text-main', '#e2e8f0');
      root.style.setProperty('--text-muted', '#a0aec0');
      root.style.setProperty('--border-color', '#1e1e3a');
      root.style.setProperty('--result-bg', '#080810');
      root.style.setProperty('--result-text', '#68d391'); 
      
      // ADD THESE NEW STATUS VARIABLES FOR DARK MODE
      root.style.setProperty('--step-bg-success', '#0a1f0a');
      root.style.setProperty('--step-border-success', '#48bb78');
      root.style.setProperty('--step-bg-warning', '#1f1200');
      root.style.setProperty('--step-border-warning', '#f6ad55');
      root.style.setProperty('--step-bg-error', '#1f0a0a');
      root.style.setProperty('--step-border-error', '#fc8181');
      root.style.setProperty('--info-bg', '#0a1040');
      root.style.setProperty('--info-border', '#7c6af7');

    } else {
      // ☀️ LIGHT MODE (Soft pastel backgrounds with high-contrast borders)
      root.style.setProperty('--bg-main', 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'); 
      root.style.setProperty('--bg-sidebar', '#ffffff');    
      root.style.setProperty('--bg-card', '#ffffff');       
      root.style.setProperty('--bg-secondary', '#f1f5f9');  
      root.style.setProperty('--text-main', '#0f172a');    
      root.style.setProperty('--text-muted', '#475569');   
      root.style.setProperty('--border-color', '#cbd5e1'); 
      root.style.setProperty('--result-bg', '#f0fdf4');    
      root.style.setProperty('--result-text', '#047857');  
      
      // ADD THESE NEW STATUS VARIABLES FOR LIGHT MODE
      root.style.setProperty('--step-bg-success', '#f0fdf4');    /* Pale green */
      root.style.setProperty('--step-border-success', '#16a34a'); /* Strong green */
      root.style.setProperty('--step-bg-warning', '#fffbeb');    /* Pale amber */
      root.style.setProperty('--step-border-warning', '#d97706'); /* Strong amber */
      root.style.setProperty('--step-bg-error', '#fef2f2');      /* Pale red */
      root.style.setProperty('--step-border-error', '#dc2626');  /* Strong red */
      root.style.setProperty('--info-bg', '#eef2ff');            /* Pale indigo */
      root.style.setProperty('--info-border', '#6366f1');        /* Strong indigo */
    }
  }, [isDark]);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);

// Small Toggle Button Component
export const ThemeToggleButton = () => {
  const { isDark, toggleTheme } = useTheme();
  return (
    <button onClick={toggleTheme} className="theme-btn">
      {isDark ? '☀️ Light Mode' : '🌙 Dark Mode'}
    </button>
  );
};