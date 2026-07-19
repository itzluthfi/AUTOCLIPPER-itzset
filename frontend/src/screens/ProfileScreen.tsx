import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { getCredits, getUser, logout, getPublicSettings, checkCookieStatus } from '../services/api';

export default function ProfileScreen({ navigation }: any) {
  const { colors, isDark, theme, setTheme } = useTheme();
  const [credits, setCredits] = useState(0);
  const [user, setUser] = useState<any>(null);
  const [payEnabled, setPayEnabled] = useState(false);
  const [hasCookie, setHasCookie] = useState(false);

  useEffect(() => {
    getCredits().then(c => setCredits(c.credits)).catch(() => {});
    getUser().then(u => setUser(u)).catch(() => {});
    getPublicSettings().then(s => setPayEnabled(s.payment_enabled)).catch(() => {});
    checkCookieStatus().then((res: any) => setHasCookie(res.has_cookie)).catch(() => {});
  }, []);

  const handleLogout = async () => {
    await logout();
    navigation.replace('Home');
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Profil" />
      <ScrollView contentContainerStyle={{ padding: 16, flexGrow: 1 }}>
        {/* User Info */}
        <View style={{ padding: 20, borderRadius: 16, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16, alignItems: 'center' }}>
          <View style={{ width: 64, height: 64, borderRadius: 32, backgroundColor: colors.primary + '30', alignItems: 'center', justifyContent: 'center', marginBottom: 12 }}>
            <Ionicons name="person" size={32} color={colors.primary} />
          </View>
          <Text style={{ fontSize: 18, fontWeight: '600', color: colors.text }}>{user?.name || 'User'}</Text>
          <Text style={{ color: colors.muted, fontSize: 13 }}>{user?.email || ''}</Text>
          <View style={{ marginTop: 12, paddingHorizontal: 16, paddingVertical: 6, borderRadius: 8, backgroundColor: colors.primary + '20' }}>
            <Text style={{ color: colors.primary, fontWeight: '600' }}>{credits} Kredit tersisa</Text>
          </View>
          {payEnabled && (
            <TouchableOpacity
              onPress={() => navigation.navigate('Checkout')}
              style={{
                marginTop: 14, flexDirection: 'row', alignItems: 'center',
                backgroundColor: colors.primary, paddingHorizontal: 20, paddingVertical: 10,
                borderRadius: 10, gap: 6,
              }}
            >
              <Ionicons name="add-circle" size={18} color="#fff" />
              <Text style={{ color: '#fff', fontWeight: '600', fontSize: 13 }}>Beli Kredit (Top-up)</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Theme */}
        <View style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16 }}>
          <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 12, fontSize: 15 }}>Tema</Text>
          <View style={{ flexDirection: 'row', gap: 8 }}>
            {[
              { key: 'light', label: 'Terang' },
              { key: 'dark', label: 'Gelap' },
              { key: 'system', label: 'Sistem' },
            ].map((t) => (
              <TouchableOpacity key={t.key} onPress={() => setTheme(t.key as any)}
                style={{ flex: 1, paddingVertical: 10, borderRadius: 8,
                  backgroundColor: theme === t.key ? colors.primary : isDark ? '#1f1f1f' : '#f1f5f9',
                  alignItems: 'center',
                }}>
                <Text style={{ color: theme === t.key ? '#fff' : colors.text, fontWeight: '500', fontSize: 13 }}>{t.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Account Integration Dashboard */}
        <View style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16 }}>
          <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 12, fontSize: 15 }}>Integrasi Akun Sosial Media</Text>
          <View style={{ gap: 10 }}>
            {/* YouTube */}
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 4 }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                <Ionicons name="logo-youtube" size={20} color="#ff0000" />
                <View>
                  <Text style={{ fontSize: 13, fontWeight: '600', color: colors.text }}>YouTube Uploads</Text>
                  <Text style={{ fontSize: 11, color: colors.muted }}>Cookie YouTube API</Text>
                </View>
              </View>
              <View style={{ paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6, backgroundColor: hasCookie ? colors.success + '20' : colors.error + '20' }}>
                <Text style={{ color: hasCookie ? colors.success : colors.error, fontSize: 11, fontWeight: '600' }}>
                  {hasCookie ? '🟢 Terhubung' : '🔴 Terputus'}
                </Text>
              </View>
            </View>

            {/* TikTok */}
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 4, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 10 }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                <Ionicons name="logo-tiktok" size={20} color={colors.text} />
                <View>
                  <Text style={{ fontSize: 13, fontWeight: '600', color: colors.text }}>TikTok Uploads</Text>
                  <Text style={{ fontSize: 11, color: colors.muted }}>TikTok OAuth Sandbox</Text>
                </View>
              </View>
              <View style={{ paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6, backgroundColor: colors.success + '20' }}>
                <Text style={{ color: colors.success, fontSize: 11, fontWeight: '600' }}>
                  🟢 Terhubung
                </Text>
              </View>
            </View>

            {/* Instagram */}
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 4, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 10 }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                <Ionicons name="logo-instagram" size={20} color="#e1306c" />
                <View>
                  <Text style={{ fontSize: 13, fontWeight: '600', color: colors.text }}>Instagram Reels</Text>
                  <Text style={{ fontSize: 11, color: colors.muted }}>Meta Graph API</Text>
                </View>
              </View>
              <View style={{ paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6, backgroundColor: colors.success + '20' }}>
                <Text style={{ color: colors.success, fontSize: 11, fontWeight: '600' }}>
                  🟢 Terhubung
                </Text>
              </View>
            </View>
          </View>
        </View>
        {user?.role === 'admin' && (
          <TouchableOpacity onPress={() => navigation.navigate('Admin')}
            style={{ padding: 16, borderRadius: 12, backgroundColor: colors.warning + '20', borderWidth: 1, borderColor: colors.warning + '40', marginBottom: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={{ color: colors.warning, fontWeight: '600' }}>Panel Admin</Text>
            <Ionicons name="chevron-forward" size={18} color={colors.warning} />
          </TouchableOpacity>
        )}

        {/* Links */}
        {[
          { name: 'FAQ', screen: 'FAQ' },
          { name: 'Kebijakan Privasi', screen: 'Privacy' },
          { name: 'Kebijakan Cookie', screen: 'Cookie' },
          { name: 'Syarat & Ketentuan', screen: 'Terms' },
        ].map((link, i) => (
          <TouchableOpacity key={i} onPress={() => navigation.navigate(link.screen)}
            style={{ padding: 14, borderRadius: 8, marginBottom: 4, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={{ color: colors.text, fontSize: 14 }}>{link.name}</Text>
            <Ionicons name="chevron-forward" size={16} color={colors.muted} />
          </TouchableOpacity>
        ))}

        {/* Logout */}
        <TouchableOpacity onPress={handleLogout}
          style={{ padding: 14, borderRadius: 12, borderWidth: 1, borderColor: colors.error, alignItems: 'center', marginTop: 16 }}>
          <Text style={{ color: colors.error, fontWeight: '600' }}>Keluar</Text>
        </TouchableOpacity>

        <Text style={{ textAlign: 'center', color: colors.muted, fontSize: 12, marginTop: 20 }}>AutoClipper v1.0.0</Text>
      </ScrollView>
    </View>
  );
}
