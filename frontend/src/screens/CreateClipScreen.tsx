import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Animated, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { submitVideo, checkCookieStatus, loadApiKey, API_BASE } from '../services/api';
import { SkeletonLoader } from '../components/SkeletonLoader';

export default function CreateClipScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [url, setUrl] = useState('');
  const [mode, setMode] = useState<'heuristic' | 'ai'>('heuristic');
  const [tracking, setTracking] = useState<'center' | 'face' | 'speaker'>('center');
  const [loading, setLoading] = useState(false);
  const [hasCookie, setHasCookie] = useState<boolean | null>(null);

  // Animations
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 600, useNativeDriver: true }),
      Animated.timing(slideAnim, { toValue: 0, duration: 600, useNativeDriver: true }),
    ]).start();
    checkCookie();
  }, []);

  const checkCookie = async () => {
    try {
      const status = await checkCookieStatus();
      setHasCookie(status.has_cookie);
    } catch {
      setHasCookie(false);
    }
  };

  const handleSubmit = async () => {
    if (!url.trim()) {
      Alert.alert('Error', 'Masukkan URL YouTube terlebih dahulu');
      return;
    }
    if (!hasCookie) {
      Alert.alert(
        'Cookie Belum Diset',
        'Anda harus upload cookie YouTube terlebih dahulu sebelum bisa memproses video.\n\nKlik "Upload Cookie" di halaman Admin atau hubungi admin.',
        [{ text: 'OK' }]
      );
      return;
    }
    setLoading(true);
    try {
      const result = await submitVideo(url.trim(), mode, tracking);
      try {
        const activeJobsStr = await AsyncStorage.getItem('active_jobs');
        const activeJobs = activeJobsStr ? JSON.parse(activeJobsStr) : [];
        activeJobs.push(result.video_id);
        await AsyncStorage.setItem('active_jobs', JSON.stringify(activeJobs));
      } catch {}
      navigation.replace('Processing', { videoId: result.video_id });
    } catch (e: any) {
      const isInsuf = e.message && (e.message.toLowerCase().includes('credits') || e.message.includes('402'));
      if (isInsuf) {
        Alert.alert(
          'Kredit AI Habis',
          'Kredit Anda tidak mencukupi untuk memproses video menggunakan AI.\n\nSilakan beralih ke mode "Heuristik" (Gratis) atau hubungi administrator untuk melakukan top-up kredit Anda.'
        );
      } else {
        Alert.alert('Error', e.message || 'Gagal memproses video');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.background }}>
      <Animated.View style={{ opacity: fadeAnim, transform: [{ translateY: slideAnim }], padding: 20 }}>

        {/* Header */}
        <Text style={{ fontSize: 22, fontWeight: '700', color: colors.text, marginBottom: 4 }}>
          Buat Clip Baru
        </Text>
        <Text style={{ color: colors.muted, marginBottom: 20 }}>
          Masukkan link YouTube untuk mulai membuat short clip
        </Text>

        {/* ─── COOKIE WARNING ─── */}
        {hasCookie === false && (
          <View style={{
            padding: 16, borderRadius: 12, marginBottom: 16,
            backgroundColor: colors.warning + '20',
            borderWidth: 1, borderColor: colors.warning,
          }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
              <Ionicons name="warning" size={20} color={colors.warning} style={{ marginRight: 8 }} />
              <Text style={{ fontWeight: '600', color: colors.text, flex: 1 }}>
                Cookie YouTube Belum Diset
              </Text>
            </View>
            <Text style={{ color: colors.text, fontSize: 13, lineHeight: 18, marginBottom: 12 }}>
              Anda harus upload cookie YouTube terlebih dahulu sebelum bisa menggunakan fitur clip.
              Cookie ini digunakan sebagai autentikasi ke YouTube.
            </Text>
            <TouchableOpacity
              onPress={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '.json';
                input.onchange = async (e: any) => {
                  const file = e.target?.files?.[0];
                  if (!file) return;
                  const form = new FormData();
                  form.append('file', file);
                  try {
                    const resp = await fetch(`${API_BASE}/cookie/upload`, {
                      method: 'POST',
                      headers: { 'X-API-Key': (await loadApiKey()) || '' },
                      body: form,
                    });
                    const json = await resp.json();
                    if (json.status === 'ok') {
                      alert('Cookie berhasil diupload!');
                      setHasCookie(true);
                    } else {
                      alert(json.detail || 'Gagal upload cookie');
                    }
                  } catch (e) {
                    alert('Gagal upload cookie');
                  }
                };
                input.click();
              }}
              style={{
                paddingVertical: 10, paddingHorizontal: 20, borderRadius: 8,
                backgroundColor: colors.primary, alignSelf: 'flex-start',
              }}
            >
              <Text style={{ color: '#fff', fontWeight: '600', fontSize: 13 }}>
                Upload Cookie di Profile
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {hasCookie === true && (
          <View style={{
            padding: 12, borderRadius: 10, marginBottom: 16,
            backgroundColor: colors.success + '15',
            borderWidth: 1, borderColor: colors.success,
            flexDirection: 'row', alignItems: 'center',
          }}>
            <Ionicons name="checkmark-circle" size={18} color={colors.success} style={{ marginRight: 8 }} />
            <Text style={{ color: colors.success, fontWeight: '500', fontSize: 13 }}>
              Cookie YouTube terverifikasi — siap memproses!
            </Text>
          </View>
        )}

        {/* URL Input */}
        <View style={{
          padding: 16, borderRadius: 12, marginBottom: 16,
          backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
        }}>
          <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
            Link YouTube
          </Text>
          <TextInput
            value={url}
            onChangeText={setUrl}
            placeholder="https://youtube.com/watch?v=..."
            placeholderTextColor={colors.muted}
            autoCapitalize="none"
            autoCorrect={false}
            style={{
              backgroundColor: isDark ? '#0f0f0f' : '#f8fafc',
              borderWidth: 1, borderColor: colors.border,
              borderRadius: 8, padding: 12, fontSize: 14,
              color: colors.text, marginBottom: 8,
            }}
          />
        </View>

        {/* Mode Selector */}
        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 0, fontSize: 14 }}>
          Mode Deteksi
        </Text>
        <View style={{
          flexDirection: 'row', gap: 8, marginBottom: 16,
          padding: 16, borderRadius: 12,
          backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
        }}>
          {[
            { key: 'heuristic' as const, label: 'Heuristic', icon: 'flash', desc: 'Cepat, gratis' },
            { key: 'ai' as const, label: 'AI', icon: 'brain', desc: 'Akurat, 1 credit' },
          ].map(m => (
            <TouchableOpacity
              key={m.key}
              onPress={() => setMode(m.key)}
              style={{
                flex: 1, padding: 12, borderRadius: 8,
                backgroundColor: mode === m.key ? colors.primary + '20' : 'transparent',
                borderWidth: 1, borderColor: mode === m.key ? colors.primary : colors.border,
                alignItems: 'center',
              }}
            >
              <Ionicons name={m.icon as any} size={20} color={mode === m.key ? colors.primary : colors.muted} />
              <Text style={{ fontWeight: '600', color: mode === m.key ? colors.primary : colors.text, marginTop: 4, fontSize: 13 }}>
                {m.label}
              </Text>
              <Text style={{ color: colors.muted, fontSize: 11, marginTop: 2 }}>{m.desc}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Tracking Selector */}
        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
          Tracking Wajah
        </Text>
        <View style={{
          flexDirection: 'row', gap: 8, marginBottom: 20,
          padding: 16, borderRadius: 12,
          backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
        }}>
          {[
            { key: 'center' as const, label: 'Center', icon: 'crop' },
            { key: 'face' as const, label: 'Face', icon: 'face' },
            { key: 'speaker' as const, label: 'Speaker', icon: 'volume-high' },
          ].map(t => (
            <TouchableOpacity
              key={t.key}
              onPress={() => setTracking(t.key)}
              style={{
                flex: 1, padding: 10, borderRadius: 8,
                backgroundColor: tracking === t.key ? colors.primary + '20' : 'transparent',
                borderWidth: 1, borderColor: tracking === t.key ? colors.primary : colors.border,
                alignItems: 'center',
              }}
            >
              <Ionicons name={t.icon as any} size={18} color={tracking === t.key ? colors.primary : colors.muted} />
              <Text style={{ color: tracking === t.key ? colors.primary : colors.text, fontSize: 12, marginTop: 4, fontWeight: '500' }}>
                {t.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Submit Button */}
        <TouchableOpacity
          onPress={handleSubmit}
          disabled={loading || hasCookie === false}
          style={{
            paddingVertical: 14, borderRadius: 12, alignItems: 'center',
            backgroundColor: (loading || hasCookie === false) ? colors.muted : colors.primary,
            opacity: (loading || hasCookie === false) ? 0.6 : 1,
          }}
        >
          {loading ? (
            <Text style={{ color: '#fff', fontWeight: '600' }}>Memproses...</Text>
          ) : (
            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
              <Ionicons name="rocket" size={18} color="#fff" style={{ marginRight: 8 }} />
              <Text style={{ color: '#fff', fontWeight: '600', fontSize: 15 }}>
                {hasCookie === false ? 'Upload Cookie Dulu' : 'Proses Video'}
              </Text>
            </View>
          )}
        </TouchableOpacity>

        {/* Info */}
        {hasCookie === false && (
          <Text style={{ color: colors.muted, fontSize: 11, textAlign: 'center', marginTop: 12 }}>
            Tombol tidak aktif karena cookie YouTube belum diset.
            {'\n'}Upload cookie di halaman Profile atau minta admin.
          </Text>
        )}

      </Animated.View>
    </ScrollView>
  );
}
