import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { getCredits, getUser, logout } from '../services/api';

export default function ProfileScreen({ navigation }: any) {
  const { colors, isDark, theme, setTheme } = useTheme();
  const [credits, setCredits] = useState(0);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    getCredits().then(c => setCredits(c.credits)).catch(() => {});
    getUser().then(u => setUser(u)).catch(() => {});
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

        {/* Admin */}
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
