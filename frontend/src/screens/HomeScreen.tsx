import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Platform, Image, StyleSheet } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { API_BASE } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

const heroImage = require('../../assets/hero_preview.png');

const features = [
  { icon: 'flash', color: '#8b5cf6', title: 'AI Auto-Detect', desc: 'Mendeteksi otomatis momen paling lucu, menarik, dan berpotensi viral menggunakan AI.' },
  { icon: 'crop', color: '#06b6d4', title: 'Smart Speaker Tracking', desc: 'Pemangkasan potret 9:16 cerdas dengan pelacakan wajah aktif YuNet AI.' },
  { icon: 'text', color: '#3b82f6', title: 'Auto Subtitle & Styles', desc: 'Menghasilkan transkrip otomatis Whisper AI dengan 5 gaya subtitle khas CapCut.' },
  { icon: 'logo-youtube', color: '#ef4444', title: 'YouTube Shorts Sync', desc: 'Unggah langsung video hasil potongan ke YouTube Shorts hanya dalam 1-klik.' },
  { icon: 'layers', color: '#10b981', title: 'Multi-Format Render', desc: 'Rendisi klip Portrait (9:16), Landscape (16:9), atau vstack Split-Screen sekaligus.' },
  { icon: 'trending-up', color: '#f59e0b', title: 'Viral Metadata SEO', desc: 'Generasi otomatis judul clickbait, hook intro, tag, dan deskripsi SEO optimal.' },
];

export default function HomeScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [featuredClips, setFeaturedClips] = useState<any[]>([]);
  const [playingClipId, setPlayingClipId] = useState<number | null>(null);

  useEffect(() => {
    const checkLoginStatus = async () => {
      if (Platform.OS === 'web') {
        const params = new URLSearchParams(window.location.search);
        const urlKey = params.get('api_key');
        if (urlKey) {
          await AsyncStorage.setItem('api_key', urlKey);
          navigation.replace('MainTabs');
          return;
        }
      }
      const token = await AsyncStorage.getItem('api_key');
      if (token) {
        navigation.replace('MainTabs');
      }
    };
    checkLoginStatus();

    fetch(`${API_BASE}/clips/public/featured`)
      .then(r => r.json())
      .then(data => setFeaturedClips(data || []))
      .catch(() => {});
  }, []);

  return (
    <View style={{ flex: 1, backgroundColor: isDark ? '#09090b' : '#f8fafc' }}>
      <Header />

      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ paddingBottom: 60 }}>
        
        {/* HERO SECTION */}
        <View style={[
          styles.heroContainer,
          { 
            backgroundColor: isDark ? '#121214' : '#ffffff', 
            borderColor: colors.border,
            flexDirection: Platform.OS === 'web' ? 'row' : 'column'
          }
        ]}>
          
          {/* Left Column: CTA Info */}
          <View style={{ flex: 1.2, paddingRight: Platform.OS === 'web' ? 24 : 0, justifyContent: 'center' }}>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>⚡ Powered by DeepSeek V4 & Whisper</Text>
            </View>
            <Text style={[styles.heroTitle, { color: colors.text }]}>
              Ubah Video YouTube Jadi <Text style={{ color: '#8b5cf6' }}>Shorts Viral</Text> Dalam Hitungan Detik
            </Text>
            <Text style={[styles.heroSubtitle, { color: colors.muted }]}>
              AutoClipper mengidentifikasi highlight terbaik dari podcast, wawancara, atau streaming game Anda secara cerdas, memotongnya menjadi format portrait 9:16 dengan teks otomatis yang menarik.
            </Text>
            
            <View style={{ flexDirection: 'row', gap: 12, marginTop: 12, flexWrap: 'wrap' }}>
              <TouchableOpacity
                onPress={() => navigation.navigate('Login')}
                style={styles.btnPrimary}
              >
                <Text style={{ color: '#fff', fontSize: 15, fontWeight: '700' }}>Coba Gratis Sekarang</Text>
                <Ionicons name="arrow-forward" size={16} color="#fff" />
              </TouchableOpacity>
              
              <TouchableOpacity
                onPress={() => navigation.navigate('FAQ')}
                style={[styles.btnSecondary, { borderColor: colors.border }]}
              >
                <Text style={{ color: colors.text, fontSize: 15, fontWeight: '600' }}>Pelajari Lebih Lanjut</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Right Column: Premium Mockup Screenshot */}
          <View style={{ flex: 1, marginTop: Platform.OS === 'web' ? 0 : 30, alignItems: 'center', justifyContent: 'center' }}>
            <View style={styles.mockupWrapper}>
              <Image
                source={heroImage}
                style={styles.heroImg}
              />
              <View style={styles.glowOverlay} />
            </View>
          </View>

        </View>

        {/* CARA KERJA */}
        <View style={{ paddingHorizontal: 24, marginTop: 40 }}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Cara Kerja Cepat</Text>
          <Text style={[styles.sectionSub, { color: colors.muted }]}>Hanya 4 langkah mudah untuk mengunggah klip viral pertama Anda</Text>
          
          <View style={{ flexDirection: Platform.OS === 'web' ? 'row' : 'column', gap: 16, marginTop: 24 }}>
            {[
              { step: '1', title: 'Tempel Link YouTube', desc: 'Masukkan URL video podcast atau streaming panjang favorit Anda.' },
              { step: '2', title: 'AI Highlight Scans', desc: 'DeepSeek menganalisis dialog & interaksi paling berpotensi viral.' },
              { step: '3', title: 'Auto-Crop & Subtitle', desc: 'Video dipotong potret 9:16 dengan transkrip font bergaya CapCut.' },
              { step: '4', title: 'Unggah Instan', desc: 'Tonton pratinjau klip, sesuaikan judul, lalu post ke YouTube Shorts.' },
            ].map((item, i) => (
              <View key={i} style={[styles.stepCard, { backgroundColor: isDark ? '#121214' : '#fff', borderColor: colors.border }]}>
                <View style={styles.stepBadge}>
                  <Text style={{ color: '#fff', fontWeight: '800', fontSize: 15 }}>{item.step}</Text>
                </View>
                <Text style={[styles.stepTitle, { color: colors.text }]}>{item.title}</Text>
                <Text style={[styles.stepDesc, { color: colors.muted }]}>{item.desc}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* FITUR UNGGULAN */}
        <View style={{ paddingHorizontal: 24, marginTop: 48 }}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Fitur Unggulan Premium</Text>
          <Text style={[styles.sectionSub, { color: colors.muted }]}>Dilengkapi teknologi pemrosesan video tercanggih saat ini</Text>
          
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -8, marginTop: 24 }}>
            {features.map((f, i) => (
              <View key={i} style={{ width: Platform.OS === 'web' ? '33.33%' : '50%', paddingHorizontal: 8, marginBottom: 16 }}>
                <View style={[styles.featureCard, { backgroundColor: isDark ? '#121214' : '#fff', borderColor: colors.border }]}>
                  <View style={[styles.iconContainer, { backgroundColor: f.color + '15' }]}>
                    <Ionicons name={f.icon as any} size={22} color={f.color} />
                  </View>
                  <Text style={[styles.featureTitle, { color: colors.text }]}>{f.title}</Text>
                  <Text style={[styles.featureDesc, { color: colors.muted }]}>{f.desc}</Text>
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* FEATURED SHOWCASE CLIPS */}
        {featuredClips.length > 0 && (
          <View style={{ paddingHorizontal: 24, marginTop: 48 }}>
            <Text style={[styles.sectionTitle, { color: colors.text }]}>🔥 Contoh Klip Hasil AI</Text>
            <Text style={[styles.sectionSub, { color: colors.muted }]}>Tonton beberapa video viral pilihan admin yang dibuat oleh sistem</Text>
            
            <View style={{ flexDirection: Platform.OS === 'web' ? 'row' : 'column', flexWrap: 'wrap', marginHorizontal: -8, marginTop: 24 }}>
              {featuredClips.map((clip) => (
                <View key={clip.id} style={{ width: Platform.OS === 'web' ? '33.33%' : '100%', paddingHorizontal: 8, marginBottom: 16 }}>
                  <View style={[styles.clipCard, { backgroundColor: isDark ? '#121214' : '#fff', borderColor: colors.border }]}>
                    
                    {/* Media Mockup */}
                    <View style={{ height: 180, backgroundColor: '#000', borderRadius: 8, overflow: 'hidden', justifyContent: 'center', alignItems: 'center', marginBottom: 14 }}>
                      <Ionicons name="videocam" size={36} color={colors.primary + '80'} />
                      <Text style={{ color: '#fff', fontSize: 11, marginTop: 6, fontWeight: '500' }}>{Math.floor(clip.end - clip.start)} Detik Durasi</Text>
                    </View>

                    <Text style={[styles.clipTitle, { color: colors.text }]} numberOfLines={1}>
                      {clip.title}
                    </Text>
                    <Text style={{ color: colors.muted, fontSize: 11, marginBottom: 14 }} numberOfLines={2}>
                      {clip.reason || 'Klip highlight yang dihasilkan AI.'}
                    </Text>
                    
                    <TouchableOpacity
                      onPress={() => setPlayingClipId(clip.id)}
                      style={styles.btnWatch}
                    >
                      <Ionicons name="play" size={14} color="#fff" />
                      <Text style={{ color: '#fff', fontSize: 12, fontWeight: '700' }}>Tonton Klip</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* FOOTER */}
        <View style={{ borderTopWidth: 1, borderTopColor: colors.border, marginTop: 60, paddingTop: 30, alignItems: 'center' }}>
          <View style={{ flexDirection: 'row', gap: 16, marginBottom: 16 }}>
            {[
              { name: 'FAQ', screen: 'FAQ' },
              { name: 'Kebijakan Privasi', screen: 'Privacy' },
              { name: 'Cookie', screen: 'Cookie' },
              { name: 'Syarat & Ketentuan', screen: 'Terms' },
              { name: 'Tentang', screen: 'About' },
            ].map((link, i) => (
              <TouchableOpacity key={i} onPress={() => navigation.navigate(link.screen)}>
                <Text style={{ color: '#8b5cf6', fontSize: 13, fontWeight: '600' }}>{link.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text style={{ color: colors.muted, fontSize: 12 }}>
            &copy; 2026 AutoClipper. All rights reserved.
          </Text>
        </View>

      </ScrollView>

      {/* Video Player Modal Overlay */}
      {playingClipId !== null && (
        <View style={styles.modalOverlay}>
          <View style={[styles.modalCard, { backgroundColor: isDark ? '#121214' : '#fff', borderColor: colors.border }]}>
            <View style={styles.modalHeader}>
              <Text style={{ fontWeight: '800', color: colors.text, fontSize: 16 }}>Showcase Video Player</Text>
              <TouchableOpacity onPress={() => setPlayingClipId(null)} style={{ padding: 4 }}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>

            {Platform.OS === 'web' ? (
              <video
                src={`${API_BASE}/clips/${playingClipId}/file/public`}
                controls
                autoPlay
                style={styles.videoPlayer}
              />
            ) : (
              <View style={styles.videoPlayerPlaceholder}>
                <Ionicons name="play-circle" size={48} color="#8b5cf6" />
                <Text style={{ color: '#fff', marginTop: 8, fontSize: 12 }}>Pemutar video diaktifkan di Web Browser</Text>
              </View>
            )}
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  heroContainer: {
    margin: 24,
    padding: 32,
    borderRadius: 20,
    borderWidth: 1,
    shadowColor: '#8b5cf6',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 24,
  },
  badge: {
    alignSelf: 'flex-start',
    backgroundColor: '#8b5cf618',
    borderColor: '#8b5cf640',
    borderWidth: 1,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    marginBottom: 16,
  },
  badgeText: {
    color: '#8b5cf6',
    fontSize: 12,
    fontWeight: '700',
  },
  heroTitle: {
    fontSize: 32,
    fontWeight: '800',
    lineHeight: 42,
    marginBottom: 12,
  },
  heroSubtitle: {
    fontSize: 14,
    lineHeight: 22,
    marginBottom: 24,
  },
  btnPrimary: {
    backgroundColor: '#8b5cf6',
    paddingVertical: 14,
    paddingHorizontal: 22,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    shadowColor: '#8b5cf6',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  btnSecondary: {
    borderWidth: 1,
    paddingVertical: 14,
    paddingHorizontal: 22,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mockupWrapper: {
    position: 'relative',
    width: '100%',
    maxWidth: 420,
    borderRadius: 14,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#ffffff15',
  },
  heroImg: {
    width: '100%',
    height: 250,
    borderRadius: 12,
    resizeMode: 'cover',
  },
  glowOverlay: {
    position: 'absolute',
    top: 0, bottom: 0, left: 0, right: 0,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#8b5cf650',
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '800',
    textAlign: 'center',
  },
  sectionSub: {
    fontSize: 13,
    textAlign: 'center',
    marginTop: 4,
  },
  stepCard: {
    flex: 1,
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    position: 'relative',
  },
  stepBadge: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#8b5cf6',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  stepTitle: {
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 6,
  },
  stepDesc: {
    fontSize: 12,
    lineHeight: 18,
  },
  featureCard: {
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    height: '100%',
    minHeight: 130,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  featureTitle: {
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 4,
  },
  featureDesc: {
    fontSize: 11,
    lineHeight: 16,
  },
  clipCard: {
    padding: 14,
    borderRadius: 16,
    borderWidth: 1,
  },
  clipTitle: {
    fontSize: 13,
    fontWeight: '700',
  },
  btnWatch: {
    backgroundColor: '#8b5cf6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 8,
    gap: 6,
  },
  modalOverlay: {
    position: 'absolute',
    top: 0, bottom: 0, left: 0, right: 0,
    backgroundColor: 'rgba(0,0,0,0.85)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    zIndex: 9999,
  },
  modalCard: {
    width: '100%',
    maxWidth: 550,
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  videoPlayer: {
    width: '100%',
    borderRadius: 12,
    maxHeight: 420,
    backgroundColor: '#000',
  },
  videoPlayerPlaceholder: {
    height: 250,
    backgroundColor: '#000',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
