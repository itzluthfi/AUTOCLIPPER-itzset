import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { setApiKey, getUser, loadApiKey } from '../services/api';

const API_BASE = 'https://autoclipper.sir-l.web.id/api';

export default function LoginScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [key, setKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const handleLogin = async () => {
    if (!key.trim()) return;
    setLoading(true);
    try {
      await setApiKey(key.trim());
      const user = await getUser();
      if (user.role === 'admin') {
        navigation.replace('Admin');
      } else {
        navigation.replace('MainTabs');
      }
    } catch (e: any) {
      alert('API Key tidak valid');
    }
    setLoading(false);
  };

  const handleGoogleLogin = async () => {
    setGoogleLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/auth/google/login`);
      const data = await resp.json();

      if (data.login_url) {
        // Web: redirect
        if (typeof window !== 'undefined') {
          window.location.href = data.login_url;
        }
      } else {
        alert('Google OAuth belum dikonfigurasi. Admin perlu set GOOGLE_CLIENT_ID.');
      }
    } catch (e: any) {
      alert('Gagal menghubungi server');
    }
    setGoogleLoading(false);
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Masuk" />

      <View style={{ flex: 1, justifyContent: 'center', padding: 24 }}>
        <View style={{
          padding: 24,
          borderRadius: 16,
          backgroundColor: colors.card,
          borderWidth: 1,
          borderColor: colors.border,
        }}>
          <Text style={{ fontSize: 24, fontWeight: '700', color: colors.text, marginBottom: 4 }}>
            Selamat Datang
          </Text>
          <Text style={{ color: colors.muted, marginBottom: 24, fontSize: 14 }}>
            Masuk untuk mulai menggunakan AutoClipper
          </Text>

          {/* Google Login */}
          <TouchableOpacity
            onPress={handleGoogleLogin}
            disabled={googleLoading}
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'center',
              paddingVertical: 14,
              borderRadius: 10,
              backgroundColor: isDark ? '#1a1a1a' : '#fff',
              borderWidth: 1,
              borderColor: colors.border,
              marginBottom: 16,
              opacity: googleLoading ? 0.6 : 1,
            }}
          >
            <Ionicons name="logo-google" size={20} color="#ea4335" style={{ marginRight: 10 }} />
            <Text style={{ color: colors.text, fontWeight: '600', fontSize: 15 }}>
              {googleLoading ? 'Memproses...' : 'Lanjutkan dengan Google'}
            </Text>
          </TouchableOpacity>

          {/* Divider */}
          <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 16 }}>
            <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
            <Text style={{ color: colors.muted, marginHorizontal: 12, fontSize: 13 }}>atau</Text>
            <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
          </View>

          {/* API Key Login */}
          <Text style={{ color: colors.text, marginBottom: 8, fontWeight: '500', fontSize: 14 }}>API Key</Text>
          <TextInput
            value={key}
            onChangeText={setKey}
            placeholder="Masukkan API Key"
            placeholderTextColor={colors.muted}
            autoCapitalize="none"
            autoCorrect={false}
            style={{
              backgroundColor: isDark ? '#0f0f0f' : '#f8fafc',
              borderWidth: 1,
              borderColor: colors.border,
              borderRadius: 10,
              padding: 14,
              fontSize: 14,
              color: colors.text,
              marginBottom: 4,
              fontFamily: 'monospace',
            }}
          />
          <Text style={{ color: colors.muted, fontSize: 11, marginBottom: 16 }}>
            API Key didapat setelah login Google atau dari admin
          </Text>

          <TouchableOpacity
            onPress={handleLogin}
            disabled={loading || !key.trim()}
            style={{
              backgroundColor: key.trim() ? colors.primary : colors.muted,
              paddingVertical: 14,
              borderRadius: 10,
              alignItems: 'center',
              flexDirection: 'row',
              justifyContent: 'center',
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading && <ActivityIndicator color="#fff" size="small" style={{ marginRight: 8 }} />}
            <Text style={{ color: '#fff', fontSize: 16, fontWeight: '600' }}>
              {loading ? 'Memproses...' : 'Masuk dengan API Key'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}
