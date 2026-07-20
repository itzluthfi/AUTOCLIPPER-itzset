import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, TextInput, ActivityIndicator, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { PageContainer } from '../components/PageContainer';
import { LiftCard } from '../components/LiftCard';
import { Button } from '../components/Button';
import { FadeInView } from '../components/FadeInView';
import { getCredits, getUser, logout, getPublicSettings, checkCookieStatus, uploadCookie, pasteCookieText, testCookie } from '../services/api';

export default function ProfileScreen({ navigation }: any) {
  const { colors, isDark, theme, setTheme } = useTheme();
  const [credits, setCredits] = useState(0);
  const [user, setUser] = useState<any>(null);
  const [payEnabled, setPayEnabled] = useState(false);
  const [hasCookie, setHasCookie] = useState(false);

  const [showCookieModal, setShowCookieModal] = useState(false);
  const [cookieMode, setCookieMode] = useState<'upload' | 'paste'>('upload');
  const [pastedText, setPastedText] = useState('');
  const [savingCookie, setSavingCookie] = useState(false);
  const [testingCookie, setTestingCookie] = useState(false);

  useEffect(() => {
    getCredits().then(c => setCredits(c.credits)).catch(() => {});
    getUser().then(u => setUser(u)).catch(() => {});
    getPublicSettings().then(s => setPayEnabled(s.payment_enabled)).catch(() => {});
    checkCookieStatus().then((res: any) => setHasCookie(res.has_cookie)).catch(() => {});
  }, []);

  const handleTestCookie = async () => {
    setTestingCookie(true);
    try {
      const res = await testCookie();
      alert(res.message);
    } catch (e: any) {
      alert(e.message || 'Gagal menguji cookie');
    }
    setTestingCookie(false);
  };

  const handlePasteCookie = async () => {
    if (!pastedText.trim()) {
      alert('Masukkan teks cookie Netscape atau JSON!');
      return;
    }
    setSavingCookie(true);
    try {
      const res = await pasteCookieText(pastedText.trim());
      alert(res.message || 'Cookie berhasil disimpan!');
      setHasCookie(true);
      setPastedText('');
      setShowCookieModal(false);
    } catch (e: any) {
      alert(e.message || 'Gagal menyimpan cookie');
    }
    setSavingCookie(false);
  };

  const handleUploadCookieFile = () => {
    if (Platform.OS === 'web') {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.txt,.json,text/plain,application/json';
      input.onchange = async (e: any) => {
        const file = e.target?.files?.[0];
        if (!file) return;
        setSavingCookie(true);
        try {
          await uploadCookie(file);
          alert('File Cookie (.txt / .json) berhasil diupload!');
          setHasCookie(true);
          setShowCookieModal(false);
        } catch (err: any) {
          alert(err.message || 'Gagal upload cookie');
        }
        setSavingCookie(false);
      };
      input.click();
    }
  };

  const handleLogout = async () => {
    await logout();
    navigation.replace('Home');
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Profil" />
      <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
      <PageContainer maxWidth={640} style={{ padding: 16 }}>
        {/* User Info */}
        <FadeInView>
        <LiftCard style={{ padding: 20, borderRadius: 16, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16, alignItems: 'center' }}>
          <View style={{ width: 64, height: 64, borderRadius: 32, backgroundColor: colors.primary + '30', alignItems: 'center', justifyContent: 'center', marginBottom: 12 }}>
            <Ionicons name="person" size={32} color={colors.primary} />
          </View>
          <Text style={{ fontSize: 18, fontWeight: '600', color: colors.text }}>{user?.name || 'User'}</Text>
          <Text style={{ color: colors.muted, fontSize: 13 }}>{user?.email || ''}</Text>
          <View style={{ marginTop: 12, paddingHorizontal: 16, paddingVertical: 6, borderRadius: 8, backgroundColor: colors.primary + '20' }}>
            <Text style={{ color: colors.primary, fontWeight: '600' }}>{credits} Kredit tersisa</Text>
          </View>
          {payEnabled && (
            <Button
              label="Beli Kredit (Top-up)"
              icon="add-circle"
              size="md"
              style={{ marginTop: 14 }}
              onPress={() => navigation.navigate('Checkout')}
            />
          )}
        </LiftCard>
        </FadeInView>

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
            <View style={{ paddingVertical: 8 }}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                  <Ionicons name="logo-youtube" size={20} color="#ff0000" />
                  <View>
                    <Text style={{ fontSize: 13, fontWeight: '600', color: colors.text }}>YouTube Cookie & Auth</Text>
                    <Text style={{ fontSize: 11, color: colors.muted }}>Netscape .txt / JSON Cookie</Text>
                  </View>
                </View>
                <TouchableOpacity
                  onPress={() => setShowCookieModal(!showCookieModal)}
                  style={{
                    paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6,
                    backgroundColor: hasCookie ? colors.success + '20' : colors.warning + '20',
                  }}
                >
                  <Text style={{ color: hasCookie ? colors.success : colors.warning, fontSize: 11, fontWeight: '600' }}>
                    {hasCookie ? 'Terhubung (Atur)' : 'Setup Cookie'}
                  </Text>
                </TouchableOpacity>
              </View>

              {/* Cookie Setup Expanded Card */}
              {showCookieModal && (
                <View style={{
                  marginTop: 12, padding: 14, borderRadius: 10,
                  backgroundColor: isDark ? '#141414' : '#f8fafc',
                  borderWidth: 1, borderColor: colors.border,
                }}>
                  <Text style={{ color: colors.text, fontWeight: '600', fontSize: 13, marginBottom: 8 }}>
                    Kelola Cookie YouTube (Dukungan Format .txt & Paste Teks)
                  </Text>
                  <Text style={{ color: colors.muted, fontSize: 11, marginBottom: 12 }}>
                    Ekspor file <Text style={{ fontFamily: 'monospace' }}>cookies.txt</Text> dari ekstensi browser (e.g. Get cookies.txt LOCALLY) atau paste langsung isi teksnya.
                  </Text>

                  {/* Sub Tabs */}
                  <View style={{ flexDirection: 'row', backgroundColor: isDark ? '#222' : '#e2e8f0', borderRadius: 8, padding: 3, marginBottom: 12, gap: 4 }}>
                    <TouchableOpacity
                      onPress={() => setCookieMode('upload')}
                      style={{
                        flex: 1, paddingVertical: 8, paddingHorizontal: 6, borderRadius: 6, alignItems: 'center', justifyContent: 'center',
                        backgroundColor: cookieMode === 'upload' ? colors.primary : 'transparent',
                      }}
                    >
                      <Text
                        numberOfLines={1}
                        adjustsFontSizeToFit
                        style={{ color: cookieMode === 'upload' ? '#fff' : colors.text, fontSize: 12, fontWeight: '600', textAlign: 'center' }}
                      >
                        Upload File
                      </Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      onPress={() => setCookieMode('paste')}
                      style={{
                        flex: 1, paddingVertical: 8, paddingHorizontal: 6, borderRadius: 6, alignItems: 'center', justifyContent: 'center',
                        backgroundColor: cookieMode === 'paste' ? colors.primary : 'transparent',
                      }}
                    >
                      <Text
                        numberOfLines={1}
                        adjustsFontSizeToFit
                        style={{ color: cookieMode === 'paste' ? '#fff' : colors.text, fontSize: 12, fontWeight: '600', textAlign: 'center' }}
                      >
                        Paste Cookie
                      </Text>
                    </TouchableOpacity>
                  </View>

                  {cookieMode === 'upload' ? (
                    <TouchableOpacity
                      onPress={handleUploadCookieFile}
                      disabled={savingCookie}
                      style={{
                        paddingVertical: 12, borderRadius: 8, backgroundColor: colors.primary,
                        alignItems: 'center', flexDirection: 'row', justifyContent: 'center', gap: 6,
                        opacity: savingCookie ? 0.7 : 1,
                      }}
                    >
                      {savingCookie && <ActivityIndicator color="#fff" size="small" />}
                      <Ionicons name="document-attach-outline" size={18} color="#fff" />
                      <Text numberOfLines={1} style={{ color: '#fff', fontWeight: '600', fontSize: 13 }}>
                        Pilih File cookies.txt / .json
                      </Text>
                    </TouchableOpacity>
                  ) : (
                    <View>
                      <TextInput
                        value={pastedText}
                        onChangeText={setPastedText}
                        placeholder={`Paste isi file cookies.txt di sini...\nContoh:\n.youtube.com TRUE / TRUE 1791171430 LOGIN_INFO ...`}
                        placeholderTextColor={colors.muted}
                        multiline
                        numberOfLines={5}
                        style={{
                          backgroundColor: isDark ? '#0a0a0a' : '#fff',
                          borderWidth: 1, borderColor: colors.border, borderRadius: 8,
                          padding: 10, fontSize: 12, color: colors.text, fontFamily: 'monospace',
                          height: 110, textAlignVertical: 'top', marginBottom: 10,
                        }}
                      />
                      <TouchableOpacity
                        onPress={handlePasteCookie}
                        disabled={savingCookie || !pastedText.trim()}
                        style={{
                          paddingVertical: 12, borderRadius: 8,
                          backgroundColor: pastedText.trim() ? colors.primary : colors.muted,
                          alignItems: 'center', flexDirection: 'row', justifyContent: 'center', gap: 6,
                          opacity: savingCookie ? 0.7 : 1,
                        }}
                      >
                        {savingCookie && <ActivityIndicator color="#fff" size="small" />}
                        <Ionicons name="checkmark-circle-outline" size={18} color="#fff" />
                        <Text style={{ color: '#fff', fontWeight: '600', fontSize: 13 }}>
                          Simpan Teks Cookie
                        </Text>
                      </TouchableOpacity>
                    </View>
                  )}

                  {hasCookie && (
                    <TouchableOpacity
                      onPress={handleTestCookie}
                      disabled={testingCookie}
                      style={{
                        marginTop: 10, paddingVertical: 10, borderRadius: 8,
                        backgroundColor: isDark ? '#222' : '#e2e8f0',
                        alignItems: 'center', flexDirection: 'row', justifyContent: 'center', gap: 6,
                        opacity: testingCookie ? 0.7 : 1,
                      }}
                    >
                      {testingCookie && <ActivityIndicator color={colors.text} size="small" />}
                      <Ionicons name="flask-outline" size={16} color={colors.text} />
                      <Text style={{ color: colors.text, fontWeight: '600', fontSize: 12 }}>
                        Uji Validitas Cookie (Test YouTube Access)
                      </Text>
                    </TouchableOpacity>
                  )}
                </View>
              )}
            </View>

            {/* TikTok — belum diintegrasikan di backend web, jangan tampilkan status palsu */}
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 4, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 10 }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                <Ionicons name="logo-tiktok" size={20} color={colors.text} />
                <View>
                  <Text style={{ fontSize: 13, fontWeight: '600', color: colors.text }}>TikTok Uploads</Text>
                  <Text style={{ fontSize: 11, color: colors.muted }}>Auto-upload ke TikTok</Text>
                </View>
              </View>
              <View style={{ paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6, backgroundColor: colors.muted + '20' }}>
                <Text style={{ color: colors.muted, fontSize: 11, fontWeight: '600' }}>Segera Hadir</Text>
              </View>
            </View>

            {/* Instagram — belum diintegrasikan di backend web */}
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 4, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 10 }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                <Ionicons name="logo-instagram" size={20} color="#e1306c" />
                <View>
                  <Text style={{ fontSize: 13, fontWeight: '600', color: colors.text }}>Instagram Reels</Text>
                  <Text style={{ fontSize: 11, color: colors.muted }}>Auto-upload ke Reels</Text>
                </View>
              </View>
              <View style={{ paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6, backgroundColor: colors.muted + '20' }}>
                <Text style={{ color: colors.muted, fontSize: 11, fontWeight: '600' }}>Segera Hadir</Text>
              </View>
            </View>
          </View>
        </View>
        {user?.role === 'admin' && (
          <TouchableOpacity onPress={() => navigation.navigate('Admin')}>
            <LiftCard style={{ padding: 16, borderRadius: 12, backgroundColor: colors.warning + '20', borderWidth: 1, borderColor: colors.warning + '40', marginBottom: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text style={{ color: colors.warning, fontWeight: '600' }}>Panel Admin</Text>
              <Ionicons name="chevron-forward" size={18} color={colors.warning} />
            </LiftCard>
          </TouchableOpacity>
        )}

        {/* Links */}
        <LiftCard style={{ borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16, overflow: 'hidden' }}>
          {[
            { name: 'FAQ', screen: 'FAQ' },
            { name: 'Kebijakan Privasi', screen: 'Privacy' },
            { name: 'Kebijakan Cookie', screen: 'Cookie' },
            { name: 'Syarat & Ketentuan', screen: 'Terms' },
            { name: 'Tentang Aplikasi', screen: 'About' },
          ].map((link, i) => (
            <TouchableOpacity key={i} onPress={() => navigation.navigate(link.screen)}
              style={{ padding: 14, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', borderTopWidth: i === 0 ? 0 : 1, borderTopColor: colors.border }}>
              <Text style={{ color: colors.text, fontSize: 14 }}>{link.name}</Text>
              <Ionicons name="chevron-forward" size={16} color={colors.muted} />
            </TouchableOpacity>
          ))}
        </LiftCard>

        {/* Logout */}
        <Button label="Keluar" variant="danger" fullWidth onPress={handleLogout} />

        <Text style={{ textAlign: 'center', color: colors.muted, fontSize: 12, marginTop: 20 }}>AutoClipper v1.0.0</Text>
      </PageContainer>
      </ScrollView>
    </View>
  );
}
