import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, Platform, Linking, ScrollView, useWindowDimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { Aurora } from '../components/Aurora';
import { Button } from '../components/Button';
import { FadeInView } from '../components/FadeInView';
import { setApiKey, getUser, API_BASE, loginWithPassword, registerWithPassword } from '../services/api';

type AuthMode = 'login' | 'register' | 'apikey';

const brandPoints = [
  { icon: 'flash-outline' as const, text: 'Deteksi highlight otomatis via AI Router' },
  { icon: 'text-outline' as const, text: 'Subtitle & hook voiceover otomatis' },
  { icon: 'phone-portrait-outline' as const, text: 'Auto-crop portrait 9:16 siap unggah' },
  { icon: 'gift-outline' as const, text: '5 kredit AI gratis saat mendaftar' },
];

export default function LoginScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const { width } = useWindowDimensions();
  const isWide = width >= 900;
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

      <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
        <View style={{ flex: 1, flexDirection: isWide ? 'row' : 'column', minHeight: isWide ? 560 : undefined }}>

          {/* ── BRAND PANEL (desktop only) ── */}
          {isWide && (
            <View style={{ flex: 1, backgroundColor: '#12071f', padding: 48, justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
              <Aurora colors={['#8b5cf6', '#6366f1', '#3b82f6']} intensity={1} />
              <FadeInView>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 24 }}>
                  <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: '#8b5cf6', alignItems: 'center', justifyContent: 'center' }}>
                    <Ionicons name="film" size={20} color="#fff" />
                  </View>
                  <Text style={{ color: '#fff', fontWeight: '800', fontSize: 18 }}>AutoClipper</Text>
                </View>
                <Text style={{ color: '#fff', fontSize: 28, fontWeight: '800', lineHeight: 36, marginBottom: 16, maxWidth: 380 }}>
                  Satu link YouTube, jadi puluhan klip siap viral.
                </Text>
                <View style={{ gap: 14, marginTop: 12 }}>
                  {brandPoints.map((p, i) => (
                    <View key={i} style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
                      <View style={{ width: 30, height: 30, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.1)', alignItems: 'center', justifyContent: 'center' }}>
                        <Ionicons name={p.icon} size={15} color="#fff" />
                      </View>
                      <Text style={{ color: 'rgba(255,255,255,0.85)', fontSize: 13, flex: 1 }}>{p.text}</Text>
                    </View>
                  ))}
                </View>
              </FadeInView>
            </View>
          )}

          {/* ── FORM PANEL ── */}
          <View style={{ flex: 1, justifyContent: 'center', padding: isWide ? 48 : 20 }}>
            <FadeInView style={{
              padding: 24,
              borderRadius: 16,
              backgroundColor: colors.card,
              borderWidth: 1,
              borderColor: colors.border,
              maxWidth: 440,
              width: '100%',
              alignSelf: 'center',
            }}>

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
                {(['login', 'register', 'apikey'] as AuthMode[]).map((m) => (
                  <TouchableOpacity
                    key={m}
                    onPress={() => setMode(m)}
                    style={{
                      flex: 1, paddingVertical: 8, borderRadius: 8, alignItems: 'center',
                      backgroundColor: mode === m ? colors.primary : 'transparent',
                    }}
                  >
                    <Text style={{ color: mode === m ? '#fff' : colors.text, fontWeight: '600', fontSize: 13 }}>
                      {m === 'login' ? 'Masuk' : m === 'register' ? 'Daftar' : 'API Key'}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              {/* Google Login SSO Button */}
              <TouchableOpacity
                onPress={handleGoogleLogin}
                disabled={googleLoading}
                style={{
                  flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
                  paddingVertical: 12, borderRadius: 10,
                  backgroundColor: isDark ? '#1a1a1a' : '#fff',
                  borderWidth: 1, borderColor: colors.border, marginBottom: 16,
                  opacity: googleLoading ? 0.6 : 1,
                }}
              >
                <Ionicons name="logo-google" size={18} color="#ea4335" style={{ marginRight: 8 }} />
                <Text style={{ color: colors.text, fontWeight: '600', fontSize: 14 }}>
                  {googleLoading ? 'Memproses...' : 'Lanjutkan dengan Google'}
                </Text>
              </TouchableOpacity>

              <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 16 }}>
                <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
                <Text style={{ color: colors.muted, marginHorizontal: 12, fontSize: 12 }}>atau</Text>
                <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
              </View>

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

                  <Button
                    label={loading ? 'Memproses...' : mode === 'login' ? 'Masuk Sekarang' : 'Daftar Akun Gratis (+5 Kredit)'}
                    loading={loading}
                    fullWidth
                    style={{ marginTop: 6 }}
                    onPress={mode === 'login' ? handlePasswordLogin : handlePasswordRegister}
                  />
                </View>
              ) : (
                <View>
                  <Text style={{ color: colors.text, marginBottom: 4, fontWeight: '500', fontSize: 13 }}>API Key</Text>
                  <TextInput
                    value={key}
                    onChangeText={setKey}
                    placeholder="Masukkan API Key (contoh: ac_...)"
                    placeholderTextColor={colors.muted}
                    autoCapitalize="none"
                    style={{ ...inputStyle, fontFamily: 'monospace' }}
                  />
                  <Text style={{ color: colors.muted, fontSize: 11, marginBottom: 16 }}>
                    Gunakan opsi ini jika Anda memiliki API Key khusus atau akun admin.
                  </Text>

                  <Button
                    label={loading ? 'Memproses...' : 'Masuk dengan API Key'}
                    loading={loading}
                    disabled={!key.trim()}
                    fullWidth
                    onPress={handleApiKeyLogin}
                  />
                </View>
              )}

            </FadeInView>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}
