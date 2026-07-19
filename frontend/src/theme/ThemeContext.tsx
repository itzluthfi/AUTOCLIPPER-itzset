import React, { createContext, useContext, useState, useEffect } from 'react';
import { useColorScheme } from 'react-native';

type Theme = 'light' | 'dark' | 'system';

type ThemeColors = {
  background: string;
  card: string;
  border: string;
  text: string;
  muted: string;
  primary: string;
  accent: string;
  error: string;
  success: string;
  warning: string;
};

const lightColors: ThemeColors = {
  background: '#ffffff',
  card: '#f8fafc',
  border: '#e2e8f0',
  text: '#0f172a',
  muted: '#64748b',
  primary: '#3b82f6',
  accent: '#8b5cf6',
  error: '#ef4444',
  success: '#22c55e',
  warning: '#f59e0b',
};

const darkColors: ThemeColors = {
  background: '#0f0f0f',
  card: '#1a1a1a',
  border: '#2a2a2a',
  text: '#f1f5f9',
  muted: '#a0a0a0',
  primary: '#3b82f6',
  accent: '#a78bfa',
  error: '#f87171',
  success: '#4ade80',
  warning: '#fbbf24',
};

type ThemeContextType = {
  theme: Theme;
  setTheme: (t: Theme) => void;
  colors: ThemeColors;
  isDark: boolean;
};

const ThemeContext = createContext<ThemeContextType>({
  theme: 'system',
  setTheme: () => {},
  colors: lightColors,
  isDark: false,
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const systemScheme = useColorScheme();
  const [theme, setTheme] = useState<Theme>('system');
  const isDark = theme === 'system' ? systemScheme === 'dark' : theme === 'dark';
  const colors = isDark ? darkColors : lightColors;

  return (
    <ThemeContext.Provider value={{ theme, setTheme, colors, isDark }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
