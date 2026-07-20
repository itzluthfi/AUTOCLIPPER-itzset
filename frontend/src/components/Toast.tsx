import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, Animated, Platform, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

type ToastListener = (toast: ToastMessage) => void;
const listeners: Set<ToastListener> = new Set();

export const toast = {
  show: (title: string, message?: string, type: ToastType = 'info', duration: number = 3500) => {
    const item: ToastMessage = {
      id: Math.random().toString(36).substring(2, 9),
      type,
      title,
      message,
      duration,
    };
    listeners.forEach((listener) => listener(item));
  },
  success: (title: string, message?: string) => toast.show(title, message, 'success'),
  error: (title: string, message?: string) => toast.show(title, message, 'error'),
  warning: (title: string, message?: string) => toast.show(title, message, 'warning'),
  info: (title: string, message?: string) => toast.show(title, message, 'info'),
};

// Polyfill window.alert dan Alert.alert agar otomatis menggunakan Toast ini
if (typeof window !== 'undefined') {
  (window as any).alert = (msg: any) => {
    const text = typeof msg === 'object' ? JSON.stringify(msg) : String(msg);
    if (text.toLowerCase().includes('gagal') || text.toLowerCase().includes('error')) {
      toast.error('Notifikasi', text);
    } else if (text.toLowerCase().includes('berhasil') || text.toLowerCase().includes('sukses')) {
      toast.success('Notifikasi', text);
    } else {
      toast.info('Notifikasi', text);
    }
  };
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const handleToast = (newToast: ToastMessage) => {
      setToasts((prev) => [newToast, ...prev].slice(0, 4));
    };
    listeners.add(handleToast);
    return () => {
      listeners.delete(handleToast);
    };
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <View style={styles.container} pointerEvents="box-none">
      {toasts.map((item) => (
        <ToastItem key={item.id} item={item} onClose={() => removeToast(item.id)} />
      ))}
    </View>
  );
}

function ToastItem({ item, onClose }: { item: ToastMessage; onClose: () => void }) {
  const [fadeAnim] = useState(new Animated.Value(0));
  const [translateYAnim] = useState(new Animated.Value(-20));

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 250, useNativeDriver: Platform.OS !== 'web' }),
      Animated.timing(translateYAnim, { toValue: 0, duration: 250, useNativeDriver: Platform.OS !== 'web' }),
    ]).start();

    const timer = setTimeout(() => {
      handleDismiss();
    }, item.duration || 3500);

    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = () => {
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 0, duration: 200, useNativeDriver: Platform.OS !== 'web' }),
      Animated.timing(translateYAnim, { toValue: -20, duration: 200, useNativeDriver: Platform.OS !== 'web' }),
    ]).start(() => {
      onClose();
    });
  };

  const getTypeDetails = () => {
    switch (item.type) {
      case 'success':
        return {
          icon: 'checkmark-circle' as const,
          color: '#10b981',
          bg: '#064e3b',
          border: '#059669',
        };
      case 'error':
        return {
          icon: 'alert-circle' as const,
          color: '#ef4444',
          bg: '#451a1a',
          border: '#dc2626',
        };
      case 'warning':
        return {
          icon: 'warning' as const,
          color: '#f59e0b',
          bg: '#452d0a',
          border: '#d97706',
        };
      default:
        return {
          icon: 'information-circle' as const,
          color: '#3b82f6',
          bg: '#1e3a8a',
          border: '#2563eb',
        };
    }
  };

  const details = getTypeDetails();

  return (
    <Animated.View
      style={[
        styles.toastCard,
        {
          opacity: fadeAnim,
          transform: [{ translateY: translateYAnim }],
          backgroundColor: details.bg,
          borderColor: details.border,
        },
      ]}
    >
      <Ionicons name={details.icon} size={22} color={details.color} style={{ marginRight: 10 }} />
      <View style={{ flex: 1, marginRight: 8 }}>
        <Text style={styles.title}>{item.title}</Text>
        {item.message ? <Text style={styles.message}>{item.message}</Text> : null}
      </View>
      <TouchableOpacity onPress={handleDismiss} style={styles.closeBtn}>
        <Ionicons name="close" size={18} color="#94a3b8" />
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: (Platform.OS === 'web' ? ('fixed' as any) : 'absolute'),
    top: 16,
    right: 16,
    left: Platform.OS === 'web' ? 'auto' : 16,
    zIndex: 999999,
    width: Platform.OS === 'web' ? 380 : 'auto',
    gap: 10,
  },
  toastCard: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  title: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 14,
  },
  message: {
    color: '#cbd5e1',
    fontSize: 12,
    marginTop: 2,
  },
  closeBtn: {
    padding: 4,
  },
});
