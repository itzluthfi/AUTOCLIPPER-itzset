import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, Platform, Linking, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { setApiKey, getUser, API_BASE, loginWithPassword, registerWithPassword } from '../services/api';

type AuthMode = 'login' | 'register' | 'apikey';

export default function LoginScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [mode, setMode] = useState<AuthMode>('login');
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [key, setKey] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const handlePasswordLogin = async () => {
    if (!email.trim() || !password) {
      alert('Masukkan email dan password');
      return;
    }
    setLoading(true);
    try {
      const res = await loginWithPassword(email.trim(), password);
      await setApiKey(res.api_key);
      if (res.user?.role === 'admin') {
        navigation.replace('Admin');
      } else {
        navigation.replace('MainTabs');
      }
    } catch (e: any) {
      alert(e.message || 'Login gagal');
    }
    setLoading(false);
  };

  const handlePasswordRegister = async () => {
    if (!name.trim() || !email.trim() || !password) {
      alert('Lengkapi nama, email, dan password');
      return;
    }
    setLoading(true);
    try {
      const res = await registerWithPassword(name.trim(), email.trim(), password);
      await setApiKey(res.api_key);
      alert('Registrasi berhasil! Anda mendapatkan bonus 5 Kredit AI gratis.');
      navigation.replace('MainTabs');
    } catch (e: any) {
      alert(e.message || 'Registrasi gagal');
    }
    setLoading(false);
  };

  const handleApiKeyLogin = async () => {
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
      const url = `${API_BASE}/auth/google/app/login`;
      if (Platform.OS === 'web') {
        window.location.href = url;
      } else {
        await Linking.openURL(url);
      }
    } catch (e: any) {
      alert('Gagal membuka halaman login Google');
    }
    setGoogleLoading(false);
  };

  const inputStyle = {
    backgroundColor: isDark ? '#0f0f0f' : '#f8fafc',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    padding: 12,
    fontSize: 14,
    color: colors.text,
    marginBottom: 12,
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title={mode === 'register' ? 'Daftar Akun Baru' : 'Masuk'} />

      <ScrollView contentContainerStyle={{ flexGrow: 1, justifyContent: 'center', padding: 20 }}>
        <View style={{
          padding: 24,
          borderRadius: 16,
          backgroundColor: colors.card,
          borderWidth: 1,
          borderColor: colors.border,
          maxWidth: 480,
          width: '100%',
          alignSelf: 'center',
        }}>
          
          {/* Header Title */}
          <Text style={{ fontSize: 24, fontWeight: '700', color: colors.text, marginBottom: 4 }}>
            {mode === 'register' ? 'Buat Akun Baru' : 'Selamat Datang Kembali'}
          </Text>
          <Text style={{ color: colors.muted, marginBottom: 20, fontSize: 13 }}>
            {mode === 'register' 
              ? 'Dapatkan 5 Kredit AI gratis saat mendaftar akun pertama Anda' 
              : 'Masuk dengan email & password untuk mengakses AutoClipper'}
          </Text>

          {/* Tab Switcher */}
          <View style={{ flexDirection: 'row', backgroundColor: isDark ? '#1a1a1a' : '#f1f5f9', borderRadius: 10, padding: 4, marginBottom: 20 }}>
            <TouchableOpacity
              onPress={() => setMode('login')}
              style={{
                flex: 1, paddingVertical: 8, borderRadius: 8, alignItems: 'center',
                backgroundColor: mode === 'login' ? colors.primary : 'transparent',
              }}
            >
              <Text style={{ color: mode === 'login' ? '#fff' : colors.text, fontWeight: '600', fontSize: 13 }}>Masuk</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => setMode('register')}
              style={{
                flex: 1, paddingVertical: 8, borderRadius: 8, alignItems: 'center',
                backgroundColor: mode === 'register' ? colors.primary : 'transparent',
              }}
            >
              <Text style={{ color: mode === 'register' ? '#fff' : colors.text, fontWeight: '600', fontSize: 13 }}>Daftar Baru</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => setMode('apikey')}
              style={{
                flex: 1, paddingVertical: 8, borderRadius: 8, alignItems: 'center',
                backgroundColor: mode === 'apikey' ? colors.primary : 'transparent',
              }}
            >
              <Text style={{ color: mode === 'apikey' ? '#fff' : colors.text, fontWeight: '600', fontSize: 13 }}>API Key</Text>
            </TouchableOpacity>
          </View>

          {/* Google Login SSO Button */}
          <TouchableOpacity
            onPress={handleGoogleLogin}
            disabled={googleLoading}
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'center',
              paddingVertical: 12,
              borderRadius: 10,
              backgroundColor: isDark ? '#1a1a1a' : '#fff',
              borderWidth: 1,
              borderColor: colors.border,
              marginBottom: 16,
              opacity: googleLoading ? 0.6 : 1,
            }}
          >
            <Ionicons name="logo-google" size={18} color="#ea4335" style={{ marginRight: 8 }} />
            <Text style={{ color: colors.text, fontWeight: '600', fontSize: 14 }}>
              {googleLoading ? 'Memproses...' : 'Lanjutkan dengan Google'}
            </Text>
          </TouchableOpacity>

          {/* Divider */}
          <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 16 }}>
            <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
            <Text style={{ color: colors.muted, marginHorizontal: 12, fontSize: 12 }}>atau</Text>
            <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
          </View>

          {/* Form Fields */}
          {mode === 'register' && (
            <View>
              <Text style={{ color: colors.text, marginBottom: 4, fontWeight: '500', fontSize: 13 }}>Nama Lengkap</Text>
              <TextInput
                value={name}
                onChangeText={setName}
                placeholder="Masukkan nama lengkap Anda"
                placeholderTextColor={colors.muted}
                style={inputStyle}
              />
            </View>
          )}

          {mode !== 'apikey' ? (
            <View>
              <Text style={{ color: colors.text, marginBottom: 4, fontWeight: '500', fontSize: 13 }}>Email</Text>
              <TextInput
                value={email}
                onChangeText={setEmail}
                placeholder="nama@email.com"
                placeholderTextColor={colors.muted}
                keyboardType="email-address"
                autoCapitalize="none"
                style={inputStyle}
              />

              <Text style={{ color: colors.text, marginBottom: 4, fontWeight: '500', fontSize: 13 }}>Password</Text>
              <TextInput
                value={password}
                onChangeText={setPassword}
                placeholder="Masukkan password Anda"
                placeholderTextColor={colors.muted}
                secureTextEntry
                style={inputStyle}
              />

              {mode === 'login' ? (
                <TouchableOpacity
                  onPress={handlePasswordLogin}
                  disabled={loading}
                  style={{
                    backgroundColor: colors.primary,
                    paddingVertical: 14, borderRadius: 10,
                    alignItems: 'center', flexDirection: 'row', justifyContent: 'center',
                    marginTop: 8, opacity: loading ? 0.7 : 1,
                  }}
                >
                  {loading && <ActivityIndicator color="#fff" size="small" style={{ marginRight: 8 }} />}
                  <Text style={{ color: '#fff', fontSize: 15, fontWeight: '600' }}>
                    {loading ? 'Memproses...' : 'Masuk Sekarang'}
                  </Text>
                </TouchableOpacity>
              ) : (
                <TouchableOpacity
                  onPress={handlePasswordRegister}
                  disabled={loading}
                  style={{
                    backgroundColor: colors.primary,
                    paddingVertical: 14, borderRadius: 10,
                    alignItems: 'center', flexDirection: 'row', justifyContent: 'center',
                    marginTop: 8, opacity: loading ? 0.7 : 1,
                  }}
                >
                  {loading && <ActivityIndicator color="#fff" size="small" style={{ marginRight: 8 }} />}
                  <Text style={{ color: '#fff', fontSize: 15, fontWeight: '600' }}>
                    {loading ? 'Memproses...' : 'Daftar Akun Gratis (+5 Kredit)'}
                  </Text>
                </TouchableOpacity>
              )}
            </View>
          ) : (
            <View>
              <Text style={{ color: colors.text, marginBottom: 4, fontWeight: '500', fontSize: 13 }}>API Key</Text>
              <TextInput
                value={key}
                onChangeText={setKey}
                placeholder="Masukkan API Key (e.g. ac_...)"
                placeholderTextColor={colors.muted}
                autoCapitalize="none"
                style={{ ...inputStyle, fontFamily: 'monospace' }}
              />
              <Text style={{ color: colors.muted, fontSize: 11, marginBottom: 16 }}>
                Gunakan opsi ini jika Anda memiliki API Key Khusus atau Akun Admin.
              </Text>

              <TouchableOpacity
                onPress={handleApiKeyLogin}
                disabled={loading || !key.trim()}
                style={{
                  backgroundColor: key.trim() ? colors.primary : colors.muted,
                  paddingVertical: 14, borderRadius: 10,
                  alignItems: 'center', flexDirection: 'row', justifyContent: 'center',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {loading && <ActivityIndicator color="#fff" size="small" style={{ marginRight: 8 }} />}
                <Text style={{ color: '#fff', fontSize: 15, fontWeight: '600' }}>
                  {loading ? 'Memproses...' : 'Masuk dengan API Key'}
                </Text>
              </TouchableOpacity>
            </View>
          )}

        </View>
      </ScrollView>
    </View>
  );
}
