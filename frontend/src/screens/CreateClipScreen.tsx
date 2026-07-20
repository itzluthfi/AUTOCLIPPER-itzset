import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Animated, Alert, Image, useWindowDimensions, Linking, Platform, ActivityIndicator, Modal } from 'react-native';
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
  const [videoTemplate, setVideoTemplate] = useState<'9:16_crop' | '9:16_blur' | '16:9_landscape' | '9:16_podcast' | '9:16_card'>('9:16_crop');
  const [subStyle, setSubStyle] = useState<'tiktok_yellow' | 'clean_caption' | 'neon_cyber' | 'minimal_movie'>('tiktok_yellow');
  const [subAnim, setSubAnim] = useState<'word_pop' | 'full_sentence'>('word_pop');
  const [zoomImage, setZoomImage] = useState<{ uri: string; label: string } | null>(null);
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
      const result = await autoPresetVideo(url.trim());
      if (result.preset) {
        if (result.preset.mode) setMode(result.preset.mode);
        if (result.preset.tracking) setTracking(result.preset.tracking);
        if (result.preset.video_template) setVideoTemplate(result.preset.video_template);
        if (result.preset.sub_style) setSubStyle(result.preset.sub_style);
        if (result.preset.sub_anim) setSubAnim(result.preset.sub_anim);
        if (result.preset.num_clips) setNumClips(result.preset.num_clips);
        if (result.preset.reason) setAutoReason(result.preset.reason);
      }
    } catch (e: any) {
      console.error(e.message);
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
      const result = await submitVideo(url.trim(), mode, tracking, numClips, subLang, videoTemplate, subStyle, subAnim);
      try {
        const activeJobsStr = await AsyncStorage.getItem('active_jobs');
        const activeJobs = activeJobsStr ? JSON.parse(activeJobsStr) : [];
        activeJobs.push({ id: result.video_id, title: videoMeta?.title || url.trim(), createdAt: new Date().toISOString() });
        await AsyncStorage.setItem('active_jobs', JSON.stringify(activeJobs));
      } catch {}

      toast.success(
        'Video Berhasil Dimasukkan Antrian!',
        'Sistem sedang memproses video Anda secara otomatis di latar belakang.'
      );

      navigation.navigate('Main', { screen: 'Clips' });
    } catch (e: any) {
      toast.error('Gagal Memproses Video', e.message || 'Terjadi kesalahan sistem.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.background }} contentContainerStyle={{ paddingVertical: 24 }}>
      <PageContainer maxWidth={680}>
      <Animated.View style={{ opacity: fadeAnim, transform: [{ translateY: slideAnim }], paddingHorizontal: 16 }}>

        <View style={{ marginBottom: 20 }}>
          <Text style={{ fontSize: 24, fontWeight: '800', color: colors.text }}>
            Buat Clip Viral Baru
          </Text>
          <Text style={{ fontSize: 13, color: colors.muted, marginTop: 4 }}>
            Masukkan URL YouTube, pilih template visual & style subtitle, lalu biarkan AI bekerja secara otomatis.
          </Text>
        </View>

        <View style={{
          padding: 16, borderRadius: 16,
          backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
          marginBottom: 16,
        }}>
          <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
            URL Video YouTube
          </Text>
          <TextInput
            placeholder="https://www.youtube.com/watch?v=..."
            placeholderTextColor={colors.muted}
            value={url}
            onChangeText={setUrl}
            style={{
              height: 48, borderRadius: 10, paddingHorizontal: 14,
              backgroundColor: isDark ? '#0f0f0f' : '#f8fafc',
              color: colors.text,
              borderWidth: 1, borderColor: colors.border, fontSize: 14,
            }}
          />

          {youtubeId ? (
            <View style={{ marginTop: 14, borderRadius: 12, overflow: 'hidden', borderWidth: 1, borderColor: colors.border, backgroundColor: colors.background }}>
              {isPlayingPreview ? (
                <View style={{ width: '100%', height: 210, backgroundColor: '#000' }}>
                  {Platform.OS === 'web' ? (
                    <iframe
                      width="100%"
                      height="100%"
                      src={`https://www.youtube.com/embed/${youtubeId}?autoplay=1`}
                      title="YouTube Preview"
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    />
                  ) : (
                    <Image
                      source={{ uri: `https://img.youtube.com/vi/${youtubeId}/hqdefault.jpg` }}
                      style={{ width: '100%', height: '100%', resizeMode: 'cover' }}
                    />
                  )}
                </View>
              ) : (
                <TouchableOpacity onPress={() => setIsPlayingPreview(true)} style={{ position: 'relative', height: 180, width: '100%' }}>
                  <Image
                    source={{ uri: `https://img.youtube.com/vi/${youtubeId}/hqdefault.jpg` }}
                    style={{ width: '100%', height: '100%', resizeMode: 'cover' }}
                  />
                  <View style={{
                    position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.35)', justifyContent: 'center', alignItems: 'center',
                  }}>
                    <View style={{
                      width: 52, height: 52, borderRadius: 26,
                      backgroundColor: colors.primary, justifyContent: 'center', alignItems: 'center',
                      shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 6,
                    }}>
                      <Ionicons name="play" size={26} color="#fff" style={{ marginLeft: 3 }} />
                    </View>
                    <Text style={{ color: '#fff', fontSize: 11, fontWeight: '700', marginTop: 8 }}>
                      Klik untuk Putar Preview Video
                    </Text>
                  </View>
                </TouchableOpacity>
              )}

              {videoMeta ? (
                <View style={{ padding: 10, backgroundColor: colors.card, borderTopWidth: 1, borderTopColor: colors.border }}>
                  <Text style={{ fontWeight: '700', color: colors.text, fontSize: 13 }} numberOfLines={1}>
                    {videoMeta.title || 'Video YouTube'}
                  </Text>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 4 }}>
                    {videoMeta.author ? (
                      <Text style={{ color: colors.muted, fontSize: 11 }}>
                        Channel: <Text style={{ color: colors.primary, fontWeight: '600' }}>{videoMeta.author}</Text>
                      </Text>
                    ) : null}
                    {videoMeta.duration ? (
                      <Text style={{ color: colors.muted, fontSize: 11 }}>
                        Durasi: <Text style={{ color: colors.text, fontWeight: '600' }}>{Math.floor(videoMeta.duration / 60)}m {videoMeta.duration % 60}s</Text>
                      </Text>
                    ) : null}
                  </View>
                </View>
              ) : null}
            </View>
          ) : null}

          <TouchableOpacity
            onPress={handleAutoDetect}
            disabled={autoDetecting}
            style={{
              marginTop: 12, paddingVertical: 10, paddingHorizontal: 14,
              borderRadius: 10, backgroundColor: colors.primary + '15',
              borderWidth: 1, borderColor: colors.primary + '40',
              flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
            }}
          >
            {autoDetecting ? (
              <ActivityIndicator size="small" color={colors.primary} />
            ) : (
              <Ionicons name="film-outline" size={18} color={colors.primary} />
            )}
            <Text style={{ color: colors.primary, fontWeight: '700', fontSize: 13 }}>
              {autoDetecting ? 'Sutradara AI Membaca Video...' : '🎬 Konsultasi Sutradara AI (Auto-Preset Template)'}
            </Text>
          </TouchableOpacity>

          {autoReason ? (
            <View style={{
              marginTop: 10, padding: 10, borderRadius: 8,
              backgroundColor: '#064e3b', borderWidth: 1, borderColor: '#10b981',
            }}>
              <Text style={{ color: '#ecfdf5', fontSize: 12, fontWeight: '600' }}>
                {autoReason}
              </Text>
            </View>
          ) : null}
        </View>

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

        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
          🖼️ Template Layout Output Video
        </Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 16 }}>
          <View style={{ flexDirection: 'row', gap: 10 }}>
            {[
              { key: '9:16_crop' as const, label: '9:16 Full Crop', icon: 'crop-outline', desc: 'Shorts / TikTok (Face Track)', imgUri: 'https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=500' },
              { key: '9:16_blur' as const, label: '9:16 Blur Background', icon: 'phone-portrait-outline', desc: 'Landscape Utuh + Blur Top/Bottom', imgUri: 'https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=500' },
              { key: '9:16_podcast' as const, label: '9:16 Podcast Split', icon: 'git-network-outline', desc: '2 Panel Stack Wawancara', imgUri: 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=500' },
              { key: '9:16_card' as const, label: '9:16 Floating Card', icon: 'square-outline', desc: 'Frame Emas + Dark Background', imgUri: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=500' },
              { key: '16:9_landscape' as const, label: '16:9 Full Landscape', icon: 'tv-outline', desc: 'Format Horizontal Original', imgUri: 'https://images.unsplash.com/photo-1518173946687-a4c8a383392e?w=500' },
            ].map(vt => (
              <View
                key={vt.key}
                style={{
                  width: 148, padding: 10, borderRadius: 12,
                  backgroundColor: videoTemplate === vt.key ? colors.primary + '20' : colors.card,
                  borderWidth: 1, borderColor: videoTemplate === vt.key ? colors.primary : colors.border,
                  justifyContent: 'space-between',
                }}
              >
                <TouchableOpacity onPress={() => setVideoTemplate(vt.key)} style={{ alignItems: 'center' }}>
                  <Ionicons name={vt.icon as any} size={20} color={videoTemplate === vt.key ? colors.primary : colors.muted} />
                  <Text style={{ fontWeight: '700', color: videoTemplate === vt.key ? colors.primary : colors.text, marginTop: 6, fontSize: 12, textAlign: 'center' }}>
                    {vt.label}
                  </Text>
                  <Text style={{ color: colors.muted, fontSize: 10, marginTop: 2, textAlign: 'center', minHeight: 28 }}>
                    {vt.desc}
                  </Text>
                </TouchableOpacity>

                {/* Small Zoom Preview Button */}
                <TouchableOpacity
                  onPress={() => setZoomImage({ uri: vt.imgUri, label: vt.label })}
                  style={{
                    marginTop: 8, paddingVertical: 4, paddingHorizontal: 8,
                    borderRadius: 6, backgroundColor: colors.primary + '18',
                    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 4,
                  }}
                >
                  <Ionicons name="search" size={12} color={colors.primary} />
                  <Text style={{ color: colors.primary, fontSize: 10, fontWeight: '700' }}>
                    🔍 Zoom Preview
                  </Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>
        </ScrollView>

        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
          🎨 Style Subtitle
        </Text>
        <View style={{
          flexDirection: 'row', gap: 8, marginBottom: 16, flexWrap: 'wrap',
        }}>
          {[
            { key: 'tiktok_yellow' as const, label: '🔥 TikTok Viral Yellow', desc: 'Teks Kuning + Stroke Hitam Tebal' },
            { key: 'clean_caption' as const, label: '💬 Clean Modern Box', desc: 'Teks Putih + Translucent Dark Box' },
            { key: 'neon_cyber' as const, label: '⚡ Neon Cyberpunk', desc: 'Teks Cyan/Magenta Menyala Glow' },
            { key: 'minimal_movie' as const, label: '🎬 Movie Minimalist', desc: 'Teks Sinematik Halus Bawah' },
          ].map(ss => (
            <TouchableOpacity
              key={ss.key}
              onPress={() => setSubStyle(ss.key)}
              style={{
                flex: 1, minWidth: 140, padding: 10, borderRadius: 10,
                backgroundColor: subStyle === ss.key ? colors.primary + '20' : colors.card,
                borderWidth: 1, borderColor: subStyle === ss.key ? colors.primary : colors.border,
              }}
            >
              <Text style={{ fontWeight: '700', color: subStyle === ss.key ? colors.primary : colors.text, fontSize: 12 }}>
                {ss.label}
              </Text>
              <Text style={{ color: colors.muted, fontSize: 10, marginTop: 2 }}>
                {ss.desc}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
          ⚡ Animasi & Timing Subtitle
        </Text>
        <View style={{
          flexDirection: 'row', gap: 8, marginBottom: 16,
          padding: 12, borderRadius: 12,
          backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
        }}>
          {[
            { key: 'word_pop' as const, label: '🎤 Karaoke Word Highlight', icon: 'mic-outline', desc: 'Highlight kata per kata secara realtime' },
            { key: 'full_sentence' as const, label: '📝 Kalimat Utuh', icon: 'document-text-outline', desc: 'Teks muncul per frasa' },
          ].map(sa => (
            <TouchableOpacity
              key={sa.key}
              onPress={() => setSubAnim(sa.key)}
              style={{
                flex: 1, padding: 10, borderRadius: 8,
                backgroundColor: subAnim === sa.key ? colors.primary + '20' : 'transparent',
                borderWidth: 1, borderColor: subAnim === sa.key ? colors.primary : colors.border,
                alignItems: 'center',
              }}
            >
              <Ionicons name={sa.icon as any} size={18} color={subAnim === sa.key ? colors.primary : colors.muted} />
              <Text style={{ fontWeight: '700', color: subAnim === sa.key ? colors.primary : colors.text, marginTop: 4, fontSize: 12, textAlign: 'center' }}>
                {sa.label}
              </Text>
              <Text style={{ color: colors.muted, fontSize: 10, marginTop: 2, textAlign: 'center' }}>
                {sa.desc}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 14 }}>
          Bahasa Subtitle Video
        </Text>
        <View style={{
          flexDirection: 'row', gap: 8, marginBottom: 20,
          padding: 12, borderRadius: 12,
          backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
        }}>
          {[
            { key: 'id' as const, label: 'Indonesia (id)', icon: 'language-outline' },
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

        <Button
          label={loading ? 'Memproses Video...' : 'Buat Short Clip Sekarang'}
          icon="rocket-outline"
          loading={loading}
          fullWidth
          onPress={handleSubmit}
        />

      </Animated.View>
      </PageContainer>

      {/* ─── INTERACTIVE ZOOM PREVIEW MODAL ─── */}
      <Modal visible={!!zoomImage} transparent animationType="fade" onRequestClose={() => setZoomImage(null)}>
        <TouchableOpacity
          activeOpacity={1}
          onPress={() => setZoomImage(null)}
          style={{
            flex: 1, backgroundColor: 'rgba(0,0,0,0.85)',
            justifyContent: 'center', alignItems: 'center', padding: 20,
          }}
        >
          <View style={{
            width: '100%', maxWidth: 520, backgroundColor: colors.card,
            borderRadius: 16, overflow: 'hidden', borderWidth: 1, borderColor: colors.border,
            shadowColor: '#000', shadowOffset: { width: 0, height: 10 }, shadowOpacity: 0.5, shadowRadius: 15,
          }}>
            <View style={{ padding: 14, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', borderBottomWidth: 1, borderBottomColor: colors.border }}>
              <Text style={{ fontWeight: '700', color: colors.text, fontSize: 14 }}>
                🔍 Zoom Preview: {zoomImage?.label}
              </Text>
              <TouchableOpacity onPress={() => setZoomImage(null)}>
                <Ionicons name="close-circle" size={24} color={colors.muted} />
              </TouchableOpacity>
            </View>

            <View style={{ height: 380, width: '100%', backgroundColor: '#050505', justifyContent: 'center', alignItems: 'center', padding: 10 }}>
              <Image
                source={{ uri: zoomImage?.uri }}
                style={{ width: '100%', height: '100%', resizeMode: 'contain', borderRadius: 8 }}
              />
            </View>

            <View style={{ padding: 12, backgroundColor: colors.background, alignItems: 'center' }}>
              <Text style={{ color: colors.muted, fontSize: 12 }}>
                Klik area mana saja untuk menutup zoom preview
              </Text>
            </View>
          </View>
        </TouchableOpacity>
      </Modal>
    </ScrollView>
  );
}
