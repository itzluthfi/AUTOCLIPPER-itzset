import React, { useEffect, useState } from 'react';
import { View, Text, Animated, Easing, TouchableOpacity } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { ProgressBar } from '../components/ProgressBar';
import { getVideo } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

const STATUS_MAP: Record<string, { progress: number; step: string }> = {
  'pending': { progress: 10, step: 'Menunggu antrian...' },
  'downloading': { progress: 20, step: 'Mengunduh video...' },
  'subtitling': { progress: 35, step: 'Mengekstrak subtitle...' },
  'detecting': { progress: 50, step: 'Mendeteksi momen penting...' },
  'clipping': { progress: 70, step: 'Mengklip video...' },
  'tracking': { progress: 85, step: 'Face tracking...' },
  'finalizing': { progress: 95, step: 'Menyelesaikan...' },
  'completed': { progress: 100, step: 'Selesai!' },
  'failed': { progress: 0, step: 'Gagal' },
};

export default function ProcessingScreen({ route, navigation }: any) {
  const { videoId } = route.params;
  const { colors } = useTheme();
  const [currentProgress, setCurrentProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('Menunggu...');
  const [error, setError] = useState('');
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const slideAnim = React.useRef(new Animated.Value(50)).current; // For slide-in effect

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 1000, useNativeDriver: true }),
      Animated.timing(slideAnim, { toValue: 0, duration: 1000, easing: Easing.out(Easing.ease), useNativeDriver: true }),
    ]).start();

    const interval = setInterval(async () => {
      try {
        const video = await getVideo(videoId);
        const statusInfo = STATUS_MAP[video.status] || STATUS_MAP.pending;

        // Backend kini mengirim progress asli (0-100); fallback ke estimasi per-status
        const progress = typeof video.progress === 'number' && video.progress > 0
          ? video.progress
          : statusInfo.progress;
        setCurrentProgress(progress);
        setCurrentStep(statusInfo.step);

        if (video.status === 'completed') {
          clearInterval(interval);
          navigation.replace('Results', { videoId });
        } else if (video.status === 'failed') {
          clearInterval(interval);
          setError(video.error_message || 'Proses gagal. Silakan coba lagi.');
        }
      } catch (e) { console.error('Error fetching video status:', e);}
    }, 2000);

    return () => clearInterval(interval);
  }, [videoId]);

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Memproses Video" />

      <Animated.View style={{
        flex: 1,
        justifyContent: 'center',
        padding: 24,
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
          elevation: 8,
        }}>
          <Text style={{ fontSize: 22, fontWeight: '700', color: colors.text, textAlign: 'center', marginBottom: 24 }}>
            {error ? 'Gagal Memproses' : 'Memproses Video Anda'}
          </Text>

          {error ? (
            <View style={{ alignItems: 'center' }}>
              <Ionicons name="alert-circle-outline" size={60} color={colors.error} style={{ marginBottom: 16 }} />
              <Text style={{ color: colors.error, textAlign: 'center', marginBottom: 16, fontSize: 16 }}>{error}</Text>
              <TouchableOpacity
                onPress={() => navigation.goBack()}
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
            <ProgressBar progress={currentProgress} step={currentStep} />
          )}
        </View>
      </Animated.View>
    </View>
  );
}
