import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Animated, Alert, Image, useWindowDimensions, Linking, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { submitVideo, autoPresetVideo, checkCookieStatus, getUser } from '../services/api';
import { toast } from '../components/Toast';
import { PageContainer } from '../components/PageContainer';
import { Button } from '../components/Button';
import { LiftCard } from '../components/LiftCard';

function extractYouTubeId(text: string): string | null {
  if (!text) return null;
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|shorts\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = text.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
}

export default function CreateClipScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const { width } = useWindowDimensions();
  const isTablet = width >= 640;
  const [url, setUrl] = useState('');
  const [mode, setMode] = useState<'heuristic' | 'ai'>('heuristic');
  const [tracking, setTracking] = useState<'auto' | 'center' | 'face' | 'speaker'>('auto');
  const [subLang, setSubLang] = useState<'id' | 'en' | 'auto'>('id');
  const [numClips, setNumClips] = useState<number>(5);
  const [autoDetecting, setAutoDetecting] = useState<boolean>(false);
  const [autoReason, setAutoReason] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [userRole, setUserRole] = useState<string>('free');
  const [hasCookie, setHasCookie] = useState<boolean | null>(null);
  const [isPlayingPreview, setIsPlayingPreview] = useState<boolean>(false);
  const [videoMeta, setVideoMeta] = useState<{ title?: string; author?: string; duration?: number } | null>(null);

  const youtubeId = extractYouTubeId(url.trim());

  useEffect(() => {
    setIsPlayingPreview(false);
    if (!youtubeId) {
      setVideoMeta(null);
      return;
    }

    // 1. Instant oEmbed metadata (Title & Channel Author)
    fetch(`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${youtubeId}&format=json`)
      .then(res => res.json())
      .then(data => {
        if (data.title || data.author_name) {
          setVideoMeta(prev => ({
            ...prev,
            title: data.title,
            author: data.author_name,
          }));
        }
      })
      .catch(() => {});

    // 2. Fetch backend metadata & duration
    autoPresetVideo(url.trim())
      .then(res => {
        if (res.title || res.duration) {
          setVideoMeta(prev => ({
            ...prev,
            title: res.title || prev?.title,
            duration: res.duration || prev?.duration,
          }));
        }
      })
      .catch(() => {});
  }, [youtubeId]);

  // Animations
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 600, useNativeDriver: true }),
      Animated.timing(slideAnim, { toValue: 0, duration: 600, useNativeDriver: true }),
    ]).start();
    checkCookie();
    loadUserRole();
  }, []);

  const loadUserRole = async () => {
    try {
      const u = await getUser();
      if (u && u.role) setUserRole(u.role);
    } catch {}
  };

  const checkCookie = async () => {
    try {
      const status = await checkCookieStatus();
      setHasCookie(status.has_cookie);
    } catch {
      setHasCookie(false);
    }
  };

  const handleAutoDetect = async () => {
    if (!url.trim()) {
      Alert.alert('Error', 'Masukkan URL YouTube terlebih dahulu untuk deteksi otomatis');
      return;
    }
    setAutoDetecting(true);
    setAutoReason(null);
    try {
      const res = await autoPresetVideo(url.trim());
      if (res.preset) {
        if (res.preset.mode) setMode(res.preset.mode);
        if (res.preset.tracking) setTracking(res.preset.tracking);
        if (res.preset.num_clips) setNumClips(res.preset.num_clips);
        setAutoReason(res.preset.reason || 'Saran otomatis dari AI berhasil diterapkan!');
      }
    } catch (e: any) {
      Alert.alert('Info', 'Gagal membaca metadata otomatis. Menampilkan preset standar.');
    } finally {
      setAutoDetecting(false);
    }
  };

  const handleSubmit = async () => {
    if (!url.trim()) {
      toast.warning('Input Kosong', 'Masukkan URL YouTube terlebih dahulu');
      return;
    }
    if (!hasCookie) {
      toast.warning('Cookie Belum Diset', 'Silakan upload / set Cookie YouTube di menu Profil terlebih dahulu.');
      navigation.navigate('Profile');
      return;
    }
    setLoading(true);
    try {
      const result = await submitVideo(url.trim(), mode, tracking, numClips, subLang);
      try {
        const activeJobsStr = await AsyncStorage.getItem('active_jobs');
        const activeJobs = activeJobsStr ? JSON.parse(activeJobsStr) : [];
        activeJobs.push(result.video_id);
        await AsyncStorage.setItem('active_jobs', JSON.stringify(activeJobs));
      } catch {}
      toast.success('Antrian Dibuat 🚀', 'Video berhasil ditambahkan ke antrian pemrosesan.');
      navigation.replace('Processing', { videoId: result.video_id });
    } catch (e: any) {
      const isInsuf = e.message && (e.message.toLowerCase().includes('credits') || e.message.includes('402'));
      if (isInsuf) {
        toast.warning('Kredit AI Habis', 'Kredit tidak mencukupi. Silakan beralih ke mode "Heuristik" (Gratis).');
      } else {
        toast.error('Gagal Submit Video', e.message || 'Gagal memproses video');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.background }}>
      <PageContainer maxWidth={760}>
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
            <Button
              label="Setup Cookie YouTube di Profil"
              icon="key-outline"
              size="md"
              onPress={() => navigation.navigate('Profile')}
            />
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
            placeholder="https://youtube.com/watch?v=... atau Shorts"
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

          {/* ─── LIVE INSTANT YOUTUBE PREVIEW CARD ─── */}
          {youtubeId ? (
            <View style={{
              marginTop: 8, borderRadius: 10, overflow: 'hidden',
              backgroundColor: isDark ? '#141414' : '#f1f5f9',
              borderWidth: 1, borderColor: colors.primary + '60',
            }}>
              <View style={{ position: 'relative', height: 210, backgroundColor: '#000' }}>
                {Platform.OS === 'web' && isPlayingPreview ? (
                  <iframe
                    src={`https://www.youtube.com/embed/${youtubeId}?autoplay=1`}
                    style={{ width: '100%', height: '100%', border: 'none' }}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  />
                ) : (
                  <TouchableOpacity
                    onPress={() => {
                      if (Platform.OS === 'web') {
                        setIsPlayingPreview(true);
                      } else {
                        Linking.openURL(`https://www.youtube.com/watch?v=${youtubeId}`);
                      }
                    }}
                    activeOpacity={0.85}
                    style={{ width: '100%', height: '100%', position: 'relative' }}
                  >
                    <Image
                      source={{ uri: `https://img.youtube.com/vi/${youtubeId}/hqdefault.jpg` }}
                      style={{ width: '100%', height: '100%', resizeMode: 'cover', opacity: 0.88 }}
                    />
                    <View style={{
                      position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                      justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.35)',
                    }}>
                      <View style={{
                        backgroundColor: 'rgba(0,0,0,0.6)', borderRadius: 30, padding: 4,
                        borderWidth: 2, borderColor: '#FF0000',
                      }}>
                        <Ionicons name="play-circle" size={56} color="#FF0000" />
                      </View>
                      <Text style={{ color: '#ffffff', fontWeight: '700', fontSize: 12, marginTop: 6, textShadowColor: '#000', textShadowRadius: 4 }}>
                        Klik untuk Putar Preview Video
                      </Text>
                    </View>
                    <View style={{
                      position: 'absolute', top: 8, right: 8,
                      backgroundColor: '#FF0000', paddingVertical: 4, paddingHorizontal: 8,
                      borderRadius: 6, flexDirection: 'row', alignItems: 'center', gap: 4,
                    }}>
                      <Ionicons name="logo-youtube" size={12} color="#fff" />
                      <Text style={{ color: '#fff', fontSize: 10, fontWeight: '700' }}>YouTube</Text>
                    </View>
                  </TouchableOpacity>
                )}
              </View>
              {/* Rich Metadata Panel */}
              <View style={{ padding: 12, gap: 6 }}>
                {videoMeta?.title ? (
                  <Text style={{ color: colors.text, fontWeight: '700', fontSize: 14, lineHeight: 20 }} numberOfLines={2}>
                    {videoMeta.title}
                  </Text>
                ) : null}

                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, marginTop: 2 }}>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
                    {videoMeta?.author ? (
                      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
                        <Ionicons name="person-circle-outline" size={15} color={colors.primary} />
                        <Text style={{ color: colors.text, fontSize: 12, fontWeight: '600' }}>
                          {videoMeta.author}
                        </Text>
                      </View>
                    ) : null}

                    {videoMeta?.duration ? (
                      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
                        <Ionicons name="time-outline" size={14} color={colors.muted} />
                        <Text style={{ color: colors.muted, fontSize: 12, fontWeight: '500' }}>
                          {Math.floor(videoMeta.duration / 60)}m {videoMeta.duration % 60}s
                        </Text>
                      </View>
                    ) : null}
                  </View>

                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: colors.success + '18', paddingVertical: 3, paddingHorizontal: 8, borderRadius: 6 }}>
                    <Ionicons name="checkmark-circle" size={14} color={colors.success} />
                    <Text style={{ color: colors.success, fontSize: 11, fontWeight: '600' }}>
                      {isPlayingPreview ? 'Memutar Preview' : 'Siap Diproses'}
                    </Text>
                  </View>
                </View>
              </View>
            </View>
          ) : null}
          {/* ─── AUTO-DETECT LLM PRESET BUTTON ─── */}
          <TouchableOpacity
            onPress={handleAutoDetect}
            disabled={autoDetecting || !url.trim()}
            style={{
              marginTop: 10, paddingVertical: 10, paddingHorizontal: 12, borderRadius: 8,
              backgroundColor: isDark ? '#1a103c' : '#f0e6ff',
              borderWidth: 1, borderColor: colors.primary + '80',
              flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6,
              opacity: (autoDetecting || !url.trim()) ? 0.6 : 1,
            }}
          >
            <Ionicons name="hardware-chip-outline" size={16} color={colors.primary} />
            <Text style={{ color: colors.primary, fontWeight: '700', fontSize: 13 }}>
              {autoDetecting ? 'Membaca Metadata Video...' : 'Deteksi Otomatis LLM (Rekomendasi Mode)'}
            </Text>
          </TouchableOpacity>

          {autoReason ? (
            <View style={{ marginTop: 8, padding: 10, borderRadius: 8, backgroundColor: colors.primary + '15', flexDirection: 'row', alignItems: 'flex-start', gap: 6 }}>
              <Ionicons name="bulb-outline" size={14} color={colors.primary} style={{ marginTop: 1 }} />
              <Text style={{ color: colors.primary, fontSize: 11, fontWeight: '500', flex: 1 }}>
                {autoReason}
              </Text>
            </View>
          ) : null}
        </View>

        {/* ─── CLIP COUNT SELECTOR (MAX 10) ─── */}
        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
          Jumlah Klip Yang Diinginkan (Maksimal 10 Klip)
        </Text>
        <View style={{
          flexDirection: 'row', gap: 8, marginBottom: 16,
          padding: 14, borderRadius: 12,
          backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
        }}>
          {[3, 5, 8, 10].map(c => (
            <TouchableOpacity
              key={c}
              onPress={() => setNumClips(c)}
              style={{
                flex: 1, paddingVertical: 10, borderRadius: 8,
                backgroundColor: numClips === c ? colors.primary : (isDark ? '#1a1a1a' : '#f1f5f9'),
                alignItems: 'center', justifyContent: 'center',
              }}
            >
              <Text style={{ color: numClips === c ? '#fff' : colors.text, fontWeight: '700', fontSize: 13 }}>
                {c} Klip
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Mode Selector */}
        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
          Mode Deteksi Highlight
        </Text>
        <View style={{
          flexDirection: 'row', gap: 8, marginBottom: 16,
          padding: 16, borderRadius: 12,
          backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
        }}>
          {[
            { key: 'heuristic' as const, label: 'Heuristic', icon: 'flash', desc: 'Cepat, gratis' },
            { key: 'ai' as const, label: 'AI Router', icon: (userRole === 'free' ? 'lock-closed' : 'sparkles'), desc: userRole === 'free' ? 'Khusus Paid' : 'Akurat, 1 credit' },
          ].map(m => (
            <TouchableOpacity
              key={m.key}
              onPress={() => {
                if (m.key === 'ai' && userRole === 'free') {
                  Alert.alert(
                    'Khusus Akun Paid',
                    'Mode AI Router hanya tersedia untuk akun Paid / Premium. Silakan upgrade paket Anda atau gunakan Mode Heuristik (Gratis).'
                  );
                  return;
                }
                setMode(m.key);
              }}
              style={{
                flex: 1, padding: 12, borderRadius: 8,
                backgroundColor: mode === m.key ? colors.primary + '20' : 'transparent',
                borderWidth: 1, borderColor: mode === m.key ? colors.primary : colors.border,
                alignItems: 'center', opacity: (m.key === 'ai' && userRole === 'free') ? 0.7 : 1,
              }}
            >
              <Ionicons name={m.icon as any} size={20} color={mode === m.key ? colors.primary : colors.muted} />
              <Text style={{ fontWeight: '600', color: mode === m.key ? colors.primary : colors.text, marginTop: 4, fontSize: 13 }}>
                {m.label}
              </Text>
              <Text style={{ color: (m.key === 'ai' && userRole === 'free') ? colors.warning : colors.muted, fontSize: 11, marginTop: 2, fontWeight: (m.key === 'ai' && userRole === 'free') ? '600' : '400' }}>
                {m.desc}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Subtitle Language Selector */}
        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
          Bahasa Subtitle Video
        </Text>
        <View style={{
          flexDirection: 'row', gap: 8, marginBottom: 16,
          padding: 12, borderRadius: 12,
          backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
        }}>
          {[
            { key: 'id' as const, label: 'Bahasa Indonesia (id)', icon: 'language-outline' },
            { key: 'en' as const, label: 'English (en)', icon: 'globe-outline' },
            { key: 'auto' as const, label: 'Auto Detect', icon: 'sparkles-outline' },
          ].map(l => (
            <TouchableOpacity
              key={l.key}
              onPress={() => setSubLang(l.key)}
              style={{
                flex: 1, paddingVertical: 8, paddingHorizontal: 6, borderRadius: 8,
                backgroundColor: subLang === l.key ? colors.primary + '20' : 'transparent',
                borderWidth: 1, borderColor: subLang === l.key ? colors.primary : colors.border,
                alignItems: 'center', flexDirection: 'row', justifyContent: 'center', gap: 4,
              }}
            >
              <Ionicons name={l.icon as any} size={14} color={subLang === l.key ? colors.primary : colors.muted} />
              <Text style={{ fontWeight: '600', color: subLang === l.key ? colors.primary : colors.text, fontSize: 11 }}>
                {l.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Submit Button */}
        <Button
          label={loading ? 'Memproses Video...' : 'Buat Short Clip Sekarang'}
          icon="rocket-outline"
          loading={loading}
          fullWidth
          onPress={handleSubmit}
        />

      </Animated.View>
      </PageContainer>
    </ScrollView>
  );
}
