import React, { useEffect, useRef, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Platform, Image, StyleSheet, useWindowDimensions } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { FadeInView } from '../components/FadeInView';
import { LiftCard } from '../components/LiftCard';
import { Aurora } from '../components/Aurora';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';
import { Marquee } from '../components/Marquee';
import { StatCounter } from '../components/StatCounter';
import { API_BASE, getPublicStats, getPublicSettings, CreditPackage } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

const heroImage = require('../../assets/hero_preview.png');

const features = [
  { icon: 'flash', color: '#8b5cf6', title: 'AI Auto-Detect', desc: 'Mendeteksi otomatis momen paling lucu, menarik, dan berpotensi viral menggunakan AI.' },
  { icon: 'crop', color: '#06b6d4', title: 'Smart Speaker Tracking', desc: 'Pemangkasan potret 9:16 cerdas dengan analisis wajah & gerakan otomatis per klip.' },
  { icon: 'text', color: '#3b82f6', title: 'Auto Subtitle & Hook Voice', desc: 'Transkrip otomatis Whisper AI plus voiceover hook pembuka yang dibacakan AI.' },
  { icon: 'logo-youtube', color: '#ef4444', title: 'YouTube Shorts Sync', desc: 'Unggah langsung video hasil potongan ke YouTube Shorts hanya dalam 1-klik.' },
  { icon: 'layers', color: '#10b981', title: 'Multi-Format Render', desc: 'Rendisi klip Face Track, Split-Screen 2 orang, atau Center Crop otomatis.' },
  { icon: 'trending-up', color: '#f59e0b', title: 'Viral Metadata SEO', desc: 'Generasi otomatis judul clickbait, hook intro, dan deskripsi SEO optimal.' },
];

const useCases = ['Podcast', 'Gaming Highlight', 'Webinar', 'Vlog Harian', 'Talkshow', 'Tutorial', 'Review Produk', 'Rekap Live Stream'];

const steps = [
  { step: '1', title: 'Tempel Link YouTube', desc: 'Masukkan URL video podcast atau streaming panjang favorit Anda.' },
  { step: '2', title: 'AI Highlight Scan', desc: 'Router LLM menganalisis dialog, traffic heatmap & peak audio untuk cari momen terbaik.' },
  { step: '3', title: 'Auto-Crop & Subtitle', desc: 'Video dipotong potret 9:16 dengan transkrip otomatis & hook voiceover.' },
  { step: '4', title: 'Unggah Instan', desc: 'Tonton pratinjau klip, sesuaikan judul, lalu post ke YouTube Shorts.' },
];

export default function HomeScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const { width } = useWindowDimensions();
  const [featuredClips, setFeaturedClips] = useState<any[]>([]);
  const [playingClipId, setPlayingClipId] = useState<number | null>(null);
  const [stats, setStats] = useState<{ clips_created: number; videos_processed: number; creators: number } | null>(null);
  const [packages, setPackages] = useState<CreditPackage[]>([]);

  const scrollRef = useRef<ScrollView>(null);
  const howItWorksY = useRef(0);

  // Breakpoint berbasis lebar layar — bukan Platform.OS,
  // supaya browser HP mendapat layout mobile yang benar.
  const isWide = width >= 900;
  const isTablet = width >= 640;
  const isDesktop = width >= 1024;
  const cardWidth = isDesktop ? '33.33%' : isTablet ? '50%' : '100%';

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
      .then(data => setFeaturedClips(Array.isArray(data) ? data : []))
      .catch(() => {});

    getPublicStats().then(setStats).catch(() => {});
    getPublicSettings().then(s => setPackages(s.packages || [])).catch(() => {});
  }, []);

  const card = { backgroundColor: isDark ? '#121214' : '#ffffff', borderColor: colors.border };
  const showLiveStats = !!stats && (stats.clips_created + stats.videos_processed + stats.creators) > 0;

  const scrollToHowItWorks = () => {
    scrollRef.current?.scrollTo({ y: Math.max(0, howItWorksY.current - 16), animated: true });
  };

  return (
    <View style={{ flex: 1, backgroundColor: isDark ? '#09090b' : '#f8fafc' }}>
      <Header
        rightAction={
          <View style={{ flexDirection: 'row', gap: 8 }}>
            <Button label="Masuk" variant="secondary" size="md" onPress={() => navigation.navigate('Login')} />
          </View>
        }
      />

      <ScrollView ref={scrollRef} style={{ flex: 1 }} contentContainerStyle={{ paddingBottom: 60 }}>
        <View style={styles.container}>

          {/* ── HERO ── */}
          <View style={{ margin: isWide ? 24 : 16, marginBottom: isWide ? 0 : 0 }}>
            <View style={[styles.heroContainer, card, { flexDirection: isWide ? 'row' : 'column', padding: isWide ? 40 : 20, overflow: 'hidden' }]}>
              <Aurora colors={['#8b5cf6', '#3b82f6', '#06b6d4']} intensity={isDark ? 1 : 0.6} />

              <FadeInView style={{ flex: isWide ? 1.15 : undefined, paddingRight: isWide ? 32 : 0, justifyContent: 'center' }}>
                <Badge icon="flash" label="Didukung Router LLM DeepSeek & Whisper AI" color="#8b5cf6" />
                <Text style={[styles.heroTitle, { color: colors.text, fontSize: isWide ? 38 : 27, lineHeight: isWide ? 48 : 35, marginTop: 16 }]}>
                  Ubah Video YouTube Jadi <Text style={{ color: '#8b5cf6' }}>Shorts Viral</Text> Dalam Hitungan Menit
                </Text>
                <Text style={[styles.heroSubtitle, { color: colors.muted }]}>
                  AutoClipper menganalisis podcast, wawancara, atau streaming panjang Anda dengan AI, lalu otomatis memotongnya jadi klip 9:16 lengkap dengan subtitle dan voiceover hook yang siap unggah.
                </Text>

                <View style={{ flexDirection: 'row', gap: 12, marginTop: 8, flexWrap: 'wrap' }}>
                  <Button label="Coba Gratis Sekarang" icon="arrow-forward" iconPosition="right" onPress={() => navigation.navigate('Login')} />
                  <Button label="Lihat Cara Kerja" variant="secondary" onPress={scrollToHowItWorks} />
                </View>

                {showLiveStats && (
                  <View style={{ flexDirection: 'row', gap: 22, marginTop: 28, flexWrap: 'wrap' }}>
                    <View>
                      <StatCounter value={stats!.clips_created} suffix="+" style={{ fontSize: 20, fontWeight: '800', color: colors.text }} />
                      <Text style={{ color: colors.muted, fontSize: 11 }}>Klip dibuat</Text>
                    </View>
                    <View>
                      <StatCounter value={stats!.videos_processed} suffix="+" style={{ fontSize: 20, fontWeight: '800', color: colors.text }} />
                      <Text style={{ color: colors.muted, fontSize: 11 }}>Video diproses</Text>
                    </View>
                    <View>
                      <StatCounter value={stats!.creators} suffix="+" style={{ fontSize: 20, fontWeight: '800', color: colors.text }} />
                      <Text style={{ color: colors.muted, fontSize: 11 }}>Kreator aktif</Text>
                    </View>
                  </View>
                )}
              </FadeInView>

              <FadeInView delay={150} style={{ flex: isWide ? 1 : undefined, marginTop: isWide ? 0 : 28, alignItems: 'center', justifyContent: 'center' }}>
                <View style={styles.mockupWrapper}>
                  <Image source={heroImage} style={styles.heroImg} />
                  <View style={styles.glowOverlay} />

                  {/* Floating proof chips — gaya iklan produk SaaS */}
                  <FadeInView delay={500} style={[styles.floatChip, { top: -14, left: -14, backgroundColor: isDark ? '#18181b' : '#fff', borderColor: colors.border }]}>
                    <Ionicons name="sparkles" size={14} color="#8b5cf6" />
                    <Text style={[styles.floatChipText, { color: colors.text }]}>AI Highlight Ditemukan</Text>
                  </FadeInView>
                  <FadeInView delay={750} style={[styles.floatChip, { bottom: -12, right: -10, backgroundColor: isDark ? '#18181b' : '#fff', borderColor: colors.border }]}>
                    <Ionicons name="phone-portrait" size={14} color="#06b6d4" />
                    <Text style={[styles.floatChipText, { color: colors.text }]}>Siap 9:16</Text>
                  </FadeInView>
                </View>
              </FadeInView>
            </View>
          </View>

          {/* ── USE-CASE MARQUEE ── */}
          <FadeInView delay={80}>
            <View style={{ marginTop: 36, paddingVertical: 4 }}>
              <Text style={{ textAlign: 'center', color: colors.muted, fontSize: 12, fontWeight: '600', letterSpacing: 0.5, marginBottom: 14, textTransform: 'uppercase' }}>
                Cocok untuk segala jenis konten panjang
              </Text>
              <Marquee speed={35}>
                {useCases.map((u, i) => (
                  <View key={i} style={[styles.useCasePill, { borderColor: colors.border, backgroundColor: isDark ? '#121214' : '#fff' }]}>
                    <Ionicons name="checkmark-circle" size={14} color="#8b5cf6" />
                    <Text style={{ color: colors.text, fontSize: 13, fontWeight: '600' }}>{u}</Text>
                  </View>
                ))}
              </Marquee>
            </View>
          </FadeInView>

          {/* ── CARA KERJA ── */}
          <View onLayout={(e) => { howItWorksY.current = e.nativeEvent.layout.y; }}>
            <FadeInView delay={120}>
              <View style={{ paddingHorizontal: isWide ? 24 : 16, marginTop: 44 }}>
                <Text style={[styles.sectionTitle, { color: colors.text }]}>Cara Kerja Cepat</Text>
                <Text style={[styles.sectionSub, { color: colors.muted }]}>Hanya 4 langkah mudah untuk mengunggah klip viral pertama Anda</Text>

                <View style={{ flexDirection: isTablet ? 'row' : 'column', flexWrap: 'wrap', gap: 16, marginTop: 24 }}>
                  {steps.map((item, i) => (
                    <LiftCard key={i} style={[styles.stepCard, card, { minWidth: isTablet ? 200 : undefined }]}>
                      <View style={styles.stepBadge}>
                        <Text style={{ color: '#fff', fontWeight: '800', fontSize: 15 }}>{item.step}</Text>
                      </View>
                      <Text style={[styles.stepTitle, { color: colors.text }]}>{item.title}</Text>
                      <Text style={[styles.stepDesc, { color: colors.muted }]}>{item.desc}</Text>
                    </LiftCard>
                  ))}
                </View>
              </View>
            </FadeInView>
          </View>

          {/* ── FITUR UNGGULAN ── */}
          <FadeInView delay={160}>
            <View style={{ paddingHorizontal: isWide ? 24 : 16, marginTop: 48 }}>
              <Text style={[styles.sectionTitle, { color: colors.text }]}>Fitur Unggulan Premium</Text>
              <Text style={[styles.sectionSub, { color: colors.muted }]}>Dilengkapi teknologi pemrosesan video tercanggih saat ini</Text>

              <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -8, marginTop: 24 }}>
                {features.map((f, i) => (
                  <View key={i} style={{ width: cardWidth, paddingHorizontal: 8, marginBottom: 16 }}>
                    <LiftCard style={[styles.featureCard, card]}>
                      <View style={[styles.iconContainer, { backgroundColor: f.color + '15' }]}>
                        <Ionicons name={f.icon as any} size={22} color={f.color} />
                      </View>
                      <Text style={[styles.featureTitle, { color: colors.text }]}>{f.title}</Text>
                      <Text style={[styles.featureDesc, { color: colors.muted }]}>{f.desc}</Text>
                    </LiftCard>
                  </View>
                ))}
              </View>
            </View>
          </FadeInView>

          {/* ── LIVE STATS BAND ── */}
          {showLiveStats && (
            <FadeInView delay={100}>
              <View style={{ marginHorizontal: isWide ? 24 : 16, marginTop: 48 }}>
                <LinearStatsBand isDark={isDark} colors={colors} stats={stats!} />
              </View>
            </FadeInView>
          )}

          {/* ── FEATURED SHOWCASE CLIPS ── */}
          {featuredClips.length > 0 && (
            <View style={{ paddingHorizontal: isWide ? 24 : 16, marginTop: 48 }}>
              <Text style={[styles.sectionTitle, { color: colors.text }]}>Contoh Klip Hasil AI</Text>
              <Text style={[styles.sectionSub, { color: colors.muted }]}>Tonton beberapa video viral pilihan admin yang dibuat oleh sistem</Text>

              <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -8, marginTop: 24 }}>
                {featuredClips.map((clip) => (
                  <View key={clip.id} style={{ width: cardWidth, paddingHorizontal: 8, marginBottom: 16 }}>
                    <LiftCard style={[styles.clipCard, card]}>
                      <View style={styles.clipThumb}>
                        <Ionicons name="videocam" size={36} color={colors.primary + '80'} />
                        <Text style={{ color: '#fff', fontSize: 11, marginTop: 6, fontWeight: '500' }}>{Math.floor(clip.end - clip.start)} Detik Durasi</Text>
                      </View>

                      <Text style={[styles.clipTitle, { color: colors.text }]} numberOfLines={1}>
                        {clip.title}
                      </Text>
                      <Text style={{ color: colors.muted, fontSize: 11, marginBottom: 14 }} numberOfLines={2}>
                        {clip.reason || 'Klip highlight yang dihasilkan AI.'}
                      </Text>

                      <TouchableOpacity onPress={() => setPlayingClipId(clip.id)} style={styles.btnWatch} activeOpacity={0.85}>
                        <Ionicons name="play" size={14} color="#fff" />
                        <Text style={{ color: '#fff', fontSize: 12, fontWeight: '700' }}>Tonton Klip</Text>
                      </TouchableOpacity>
                    </LiftCard>
                  </View>
                ))}
              </View>
            </View>
          )}

          {/* ── PRICING PREVIEW ── */}
          {packages.length > 0 && (
            <FadeInView delay={140}>
              <View style={{ paddingHorizontal: isWide ? 24 : 16, marginTop: 48 }}>
                <Text style={[styles.sectionTitle, { color: colors.text }]}>Paket Kredit Fleksibel</Text>
                <Text style={[styles.sectionSub, { color: colors.muted }]}>Mode Heuristik selalu gratis & unlimited — kredit hanya untuk Mode AI Router</Text>

                <View style={{ flexDirection: isTablet ? 'row' : 'column', gap: 16, marginTop: 24 }}>
                  {packages.map((pkg, i) => {
                    const isPopular = i === 1;
                    return (
                      <LiftCard key={pkg.id} style={[
                        styles.priceCard, card,
                        isPopular && { borderColor: '#8b5cf6', borderWidth: 2 },
                      ]}>
                        {isPopular && (
                          <View style={styles.popularTag}>
                            <Text style={{ color: '#fff', fontSize: 10, fontWeight: '800' }}>PALING POPULER</Text>
                          </View>
                        )}
                        <Text style={{ color: colors.muted, fontSize: 13, fontWeight: '600' }}>{pkg.label}</Text>
                        <Text style={{ color: colors.text, fontSize: 26, fontWeight: '800', marginTop: 6 }}>
                          Rp {pkg.amount.toLocaleString('id-ID')}
                        </Text>
                        <Text style={{ color: '#8b5cf6', fontSize: 13, fontWeight: '700', marginTop: 2, marginBottom: 14 }}>
                          {pkg.credits} Kredit AI
                        </Text>
                        {['Deteksi highlight via Router LLM', 'Auto-crop portrait 9:16', 'Subtitle & hook voiceover otomatis', 'Auto mix face / split-screen'].map((f, fi) => (
                          <View key={fi} style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                            <Ionicons name="checkmark-circle" size={15} color="#22c55e" />
                            <Text style={{ color: colors.text, fontSize: 12.5, flex: 1 }}>{f}</Text>
                          </View>
                        ))}
                        <Button
                          label="Pilih Paket"
                          variant={isPopular ? 'primary' : 'secondary'}
                          fullWidth
                          style={{ marginTop: 10 }}
                          onPress={() => navigation.navigate('Login')}
                        />
                      </LiftCard>
                    );
                  })}
                </View>
              </View>
            </FadeInView>
          )}

          {/* ── FINAL CTA ── */}
          <FadeInView delay={100}>
            <View style={{ marginHorizontal: isWide ? 24 : 16, marginTop: 56 }}>
              <View style={[styles.finalCta, { overflow: 'hidden' }]}>
                <Aurora colors={['#8b5cf6', '#6366f1', '#3b82f6']} intensity={1} />
                <Text style={styles.finalCtaTitle}>Siap Membuat Klip Viral Pertama Anda?</Text>
                <Text style={styles.finalCtaSub}>Gratis untuk mulai. Tidak perlu kartu kredit.</Text>
                <Button
                  label="Mulai Sekarang — Gratis"
                  icon="rocket-outline"
                  size="lg"
                  onPress={() => navigation.navigate('Login')}
                  style={{ marginTop: 20 }}
                />
              </View>
            </View>
          </FadeInView>

          {/* ── FOOTER ── */}
          <View style={{ borderTopWidth: 1, borderTopColor: colors.border, marginTop: 60, paddingTop: 30, paddingHorizontal: 16 }}>
            <View style={{ flexDirection: isTablet ? 'row' : 'column', justifyContent: 'space-between', gap: 24 }}>
              <View style={{ maxWidth: 260 }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <View style={{ width: 26, height: 26, borderRadius: 8, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center' }}>
                    <Ionicons name="film" size={14} color="#fff" />
                  </View>
                  <Text style={{ fontWeight: '800', color: colors.text, fontSize: 15 }}>AutoClipper</Text>
                </View>
                <Text style={{ color: colors.muted, fontSize: 12, lineHeight: 18 }}>
                  Platform AI untuk mengubah video panjang menjadi short-form content 9:16 secara otomatis.
                </Text>
              </View>

              <View style={{ flexDirection: 'row', gap: 40, flexWrap: 'wrap' }}>
                <FooterColumn title="Produk" colors={colors} items={[
                  { name: 'Cara Kerja', onPress: scrollToHowItWorks },
                  { name: 'FAQ', onPress: () => navigation.navigate('FAQ') },
                  { name: 'Tentang', onPress: () => navigation.navigate('About') },
                ]} />
                <FooterColumn title="Legal" colors={colors} items={[
                  { name: 'Kebijakan Privasi', onPress: () => navigation.navigate('Privacy') },
                  { name: 'Kebijakan Cookie', onPress: () => navigation.navigate('Cookie') },
                  { name: 'Syarat & Ketentuan', onPress: () => navigation.navigate('Terms') },
                ]} />
              </View>
            </View>

            <Text style={{ color: colors.muted, fontSize: 12, textAlign: 'center', marginTop: 30 }}>
              &copy; 2026 AutoClipper. All rights reserved.
            </Text>
          </View>

        </View>
      </ScrollView>

      {/* Video Player Modal Overlay */}
      {playingClipId !== null && (
        <View style={styles.modalOverlay}>
          <View style={[styles.modalCard, card]}>
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

function FooterColumn({ title, items, colors }: { title: string; items: { name: string; onPress: () => void }[]; colors: any }) {
  return (
    <View>
      <Text style={{ color: colors.text, fontWeight: '700', fontSize: 13, marginBottom: 10 }}>{title}</Text>
      <View style={{ gap: 8 }}>
        {items.map((it, i) => (
          <TouchableOpacity key={i} onPress={it.onPress}>
            <Text style={{ color: colors.muted, fontSize: 13 }}>{it.name}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

function LinearStatsBand({ isDark, colors, stats }: { isDark: boolean; colors: any; stats: { clips_created: number; videos_processed: number; creators: number } }) {
  const items = [
    { icon: 'cut' as const, value: stats.clips_created, label: 'Klip Dihasilkan', color: '#8b5cf6' },
    { icon: 'videocam' as const, value: stats.videos_processed, label: 'Video Diproses', color: '#06b6d4' },
    { icon: 'people' as const, value: stats.creators, label: 'Kreator Aktif', color: '#f59e0b' },
  ];
  return (
    <View style={{
      flexDirection: 'row', flexWrap: 'wrap', borderRadius: 20, borderWidth: 1,
      borderColor: colors.border, backgroundColor: isDark ? '#121214' : '#ffffff',
      padding: 24, gap: 16,
    }}>
      {items.map((it, i) => (
        <View key={i} style={{ flex: 1, minWidth: 140, alignItems: 'center' }}>
          <View style={{ width: 40, height: 40, borderRadius: 12, backgroundColor: it.color + '18', alignItems: 'center', justifyContent: 'center', marginBottom: 10 }}>
            <Ionicons name={it.icon} size={19} color={it.color} />
          </View>
          <StatCounter value={it.value} suffix="+" style={{ fontSize: 24, fontWeight: '800', color: colors.text }} />
          <Text style={{ color: colors.muted, fontSize: 12, marginTop: 2 }}>{it.label}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
    maxWidth: 1152,
    alignSelf: 'center',
  },
  heroContainer: {
    borderRadius: 24,
    borderWidth: 1,
    position: 'relative',
    shadowColor: '#8b5cf6',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 24,
  },
  heroTitle: {
    fontWeight: '800',
    marginBottom: 14,
  },
  heroSubtitle: {
    fontSize: 14,
    lineHeight: 22,
    marginBottom: 22,
    maxWidth: 520,
  },
  mockupWrapper: {
    position: 'relative',
    width: '100%',
    maxWidth: 420,
    borderRadius: 14,
    overflow: 'visible',
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
  floatChip: {
    position: 'absolute',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
  },
  floatChipText: {
    fontSize: 11,
    fontWeight: '700',
  },
  useCasePill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    borderWidth: 1,
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
  clipThumb: {
    height: 180,
    backgroundColor: '#000',
    borderRadius: 8,
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 14,
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
  priceCard: {
    flex: 1,
    padding: 22,
    borderRadius: 18,
    borderWidth: 1,
    position: 'relative',
  },
  popularTag: {
    position: 'absolute',
    top: -11,
    alignSelf: 'center',
    backgroundColor: '#8b5cf6',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 10,
  },
  finalCta: {
    borderRadius: 24,
    padding: 44,
    alignItems: 'center',
    backgroundColor: '#12071f',
    position: 'relative',
  },
  finalCtaTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#fff',
    textAlign: 'center',
  },
  finalCtaSub: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 8,
    textAlign: 'center',
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
