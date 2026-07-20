import React, { useEffect, useState } from 'react';
import { View, Text, Animated, Easing, TouchableOpacity, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { ProgressBar } from '../components/ProgressBar';
import { getVideo } from '../services/api';
import { Ionicons } from '@expo/vector-icons';
import { PageContainer } from '../components/PageContainer';

interface ProcessingStep {
  key: string;
  label: string;
  desc: string;
  minProgress: number;
}

const STEPS: ProcessingStep[] = [
  { key: 'pending', label: '1. Inisialisasi & Antrean', desc: 'Menghubungkan ke server backend & mengecek antrean video', minProgress: 10 },
  { key: 'downloading', label: '2. Unduh Stream Video', desc: 'Mengunduh video HD & subtitle asli dari YouTube', minProgress: 25 },
  { key: 'subtitling', label: '3. Transkripsi Subtitle', desc: 'Mengekstrak percakapan & kata kunci untuk pencarian momen', minProgress: 40 },
  { key: 'detecting', label: '4. Analisis Momen Viral', desc: 'Menganalisis hook paling menarik (AI / Heuristik)', minProgress: 60 },
  { key: 'clipping', label: '5. Crop 9:16 & Finalisasi', desc: 'Memotong klip, framing vertikal 9:16 & render thumbnail', minProgress: 90 },
];

const STATUS_MAP: Record<string, { progress: number; step: string }> = {
  'pending': { progress: 10, step: '[1/5] Memulai antrean pemrosesan...' },
  'downloading': { progress: 25, step: '[2/5] Mengunduh video YouTube & subtitle...' },
  'subtitling': { progress: 40, step: '[3/5] Transkripsi suara & ekstrak subtitle...' },
  'detecting': { progress: 60, step: '[4/5] Menganalisis momen paling viral...' },
  'clipping': { progress: 80, step: '[5/5] Pemotongan klip & framing 9:16...' },
  'tracking': { progress: 90, step: 'Dynamic Face & Speaker Tracking...' },
  'finalizing': { progress: 95, step: 'Menyelesaikan klip & render thumbnail...' },
  'completed': { progress: 100, step: 'Pemrosesan Selesai!' },
  'failed': { progress: 0, step: 'Pemrosesan Gagal' },
};

function PulsingIcon({ color }: { color: string }) {
  const pulse = React.useRef(new Animated.Value(0.4)).current;
  useEffect(() => {
    const anim = Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, { toValue: 1, duration: 700, useNativeDriver: true }),
        Animated.timing(pulse, { toValue: 0.4, duration: 700, useNativeDriver: true }),
      ])
    );
    anim.start();
    return () => anim.stop();
  }, []);
  return (
    <Animated.View style={{ opacity: pulse, marginTop: 1 }}>
      <Ionicons name="time" size={18} color={color} />
    </Animated.View>
  );
}

export default function ProcessingScreen({ route, navigation }: any) {
  const { videoId } = route.params;
  const { colors, isDark } = useTheme();
  const [currentProgress, setCurrentProgress] = useState(10);
  const [currentStep, setCurrentStep] = useState('Inisialisasi...');
  const [statusKey, setStatusKey] = useState('pending');
  const [videoTitle, setVideoTitle] = useState('');
  const [error, setError] = useState('');
  const [showErrorLog, setShowErrorLog] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const slideAnim = React.useRef(new Animated.Value(30)).current;

  // Stopwatch timer counter
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatElapsed = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
  };

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 600, useNativeDriver: true }),
      Animated.timing(slideAnim, { toValue: 0, duration: 600, easing: Easing.out(Easing.ease), useNativeDriver: true }),
    ]).start();

    const interval = setInterval(async () => {
      try {
        const video = await getVideo(videoId);
        if (video.title) setVideoTitle(video.title);
        
        setStatusKey(video.status || 'pending');
        const statusInfo = STATUS_MAP[video.status] || STATUS_MAP.pending;
        
        const progress = typeof video.progress === 'number' && video.progress > 0
          ? video.progress
          : statusInfo.progress;
        
        setCurrentProgress(progress);
        const stepMessage = video.current_step_log || statusInfo.step;
        setCurrentStep(stepMessage);

        if (video.status === 'completed') {
          clearInterval(interval);
          navigation.replace('Results', { videoId, elapsedSeconds });
        } else if (video.status === 'failed') {
          clearInterval(interval);
          setError(video.error_message || 'Gagal mengunduh / memproses video dari YouTube');
        }
      } catch (e) {
        console.error('Error fetching video status:', e);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [videoId, elapsedSeconds]);

  const handleBack = () => {
    if (navigation.canGoBack()) {
      navigation.goBack();
    } else {
      navigation.replace('MainTabs');
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header title="Status Pemrosesan" />

      <ScrollView contentContainerStyle={{ padding: 20, flexGrow: 1, justifyContent: 'center' }}>
        <PageContainer maxWidth={560}>
        <Animated.View style={{
          opacity: fadeAnim,
          transform: [{ translateY: slideAnim }],
        }}>
          <View style={{
            padding: 24,
            borderRadius: 16,
            backgroundColor: colors.card,
            borderWidth: 1,
            borderColor: colors.border,
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 4 },
            shadowOpacity: 0.1,
            shadowRadius: 10,
            elevation: 6,
          }}>
            {/* Live Stopwatch Badge */}
            <View style={{
              alignSelf: 'center', backgroundColor: isDark ? '#1a1a2e' : '#eef2ff',
              paddingVertical: 4, paddingHorizontal: 12, borderRadius: 20,
              flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 12,
              borderWidth: 1, borderColor: colors.primary + '50',
            }}>
              <Ionicons name="stopwatch-outline" size={14} color={colors.primary} />
              <Text style={{ color: colors.primary, fontWeight: '700', fontSize: 12 }}>
                Waktu Berjalan: {formatElapsed(elapsedSeconds)}
              </Text>
            </View>

            <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text, textAlign: 'center', marginBottom: 6 }}>
              {error ? 'Gagal Memproses Video' : 'Memproses Video Anda'}
            </Text>

            {videoTitle ? (
              <Text style={{ fontSize: 13, color: colors.muted, textAlign: 'center', marginBottom: 20 }} numberOfLines={1}>
                {videoTitle}
              </Text>
            ) : null}

            {error ? (
              <View style={{ alignItems: 'center', marginTop: 10 }}>
                <Ionicons name="alert-circle-outline" size={54} color={colors.error} style={{ marginBottom: 12 }} />
                
                <Text style={{ color: colors.error, textAlign: 'center', fontWeight: '600', fontSize: 15, marginBottom: 8, paddingHorizontal: 10 }}>
                  {error}
                </Text>

                <TouchableOpacity
                  onPress={() => setShowErrorLog(!showErrorLog)}
                  style={{
                    paddingVertical: 6, paddingHorizontal: 12, borderRadius: 6,
                    backgroundColor: colors.border + '40', marginBottom: 20,
                    flexDirection: 'row', alignItems: 'center', gap: 4
                  }}
                >
                  <Ionicons name={showErrorLog ? 'chevron-up' : 'chevron-down'} size={14} color={colors.muted} />
                  <Text style={{ color: colors.muted, fontSize: 12, fontWeight: '500' }}>
                    {showErrorLog ? 'Sembunyikan Rincian Log Error' : 'Lihat Rincian Log Error'}
                  </Text>
                </TouchableOpacity>

                {showErrorLog && (
                  <View style={{
                    width: '100%', padding: 12, borderRadius: 8,
                    backgroundColor: isDark ? '#0a0a0a' : '#f1f5f9',
                    borderWidth: 1, borderColor: colors.border, marginBottom: 20,
                  }}>
                    <Text style={{ fontSize: 11, fontFamily: 'monospace', color: colors.error, lineHeight: 16 }}>
                      {`[SYSTEM DIAGNOSTIC LOG]\nJob ID: ${videoId}\nStatus: ${statusKey}\nDetail: ${error}\n\nSaran: Pastikan URL YouTube valid & publik. Jika video dibatasi umur / negara, pastikan file cookie di Profil telah diperbarui.`}
                    </Text>
                  </View>
                )}

                <TouchableOpacity
                  onPress={handleBack}
                  style={{
                    backgroundColor: colors.primary,
                    paddingVertical: 12,
                    paddingHorizontal: 24,
                    borderRadius: 10,
                    flexDirection: 'row', alignItems: 'center',
                    gap: 8,
                  }}
                >
                  <Ionicons name="arrow-back" size={18} color={'#fff'} />
                  <Text style={{ color: '#fff', fontWeight: '600' }}>Coba Video Lain</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <View>
                <ProgressBar progress={currentProgress} step={currentStep} />

                {/* ─── LIVE THINKING STEP TIMELINE ─── */}
                <View style={{ marginTop: 24, paddingTop: 16, borderTopWidth: 1, borderTopColor: colors.border }}>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                    <Ionicons name="list-outline" size={15} color={colors.text} />
                    <Text style={{ fontWeight: '600', color: colors.text, fontSize: 13 }}>
                      Rincian Tahapan Pemrosesan (Live Log)
                    </Text>
                  </View>

                  {STEPS.map((s, idx) => {
                    const isDone = currentProgress > s.minProgress;
                    const isCurrent = currentProgress >= (STEPS[idx - 1]?.minProgress || 0) && currentProgress <= s.minProgress;
                    
                    return (
                      <View key={s.key} style={{ flexDirection: 'row', alignItems: 'flex-start', marginBottom: 10, gap: 10 }}>
                        {isDone ? (
                          <Ionicons name="checkmark-circle" size={18} color={colors.success} style={{ marginTop: 1 }} />
                        ) : isCurrent ? (
                          <PulsingIcon color={colors.primary} />
                        ) : (
                          <Ionicons name="ellipse-outline" size={18} color={colors.muted} style={{ marginTop: 1 }} />
                        )}
                        <View style={{ flex: 1 }}>
                          <Text style={{
                            fontSize: 13, fontWeight: isCurrent ? '700' : isDone ? '600' : '400',
                            color: isDone ? colors.success : isCurrent ? colors.primary : colors.muted,
                          }}>
                            {s.label}
                          </Text>
                          <Text style={{ fontSize: 11, color: colors.muted, marginTop: 1 }}>
                            {s.desc}
                          </Text>
                        </View>
                      </View>
                    );
                  })}
                </View>
              </View>
            )}
          </View>
        </Animated.View>
        </PageContainer>
      </ScrollView>
    </View>
  );
}
