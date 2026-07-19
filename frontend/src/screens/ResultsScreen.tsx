import React, { useEffect, useState, useCallback, useRef } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Image, StyleSheet, Animated, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { ProgressBar } from '../components/ProgressBar';
import { getVideo, downloadClip } from '../services/api';

export default function ResultsScreen({ route, navigation }: any) {
  const { videoId } = route.params;
  const { colors, isDark } = useTheme();
  const [video, setVideo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const animatedProgress = useSharedValue(0);
  const barStyle = useAnimatedStyle(() => ({
    width: animatedProgress.value + '%',
    opacity: animatedProgress.value === 100 ? 1 : 0.7,
  }));

  const loadVideo = async () => {
    try {
      const v = await getVideo(videoId);
      setVideo(v);
    } catch (e) { setError('Gagal memuat hasil'); }
    finally { setLoading(false); }
  };

  const animateProgress = () => {
    Animated.timing(animatedProgress, {
      toValue: 100,
      duration: 1500,
      useNativeDriver: false,
      easing: Easing.elastic(1, 0.5),
    }).start();
  };

  useEffect(() => {
    loadVideo();
  }, [videoId]);

  const renderClip = (clip: any, index: number) => {
    const clipStatus = clip.status === 'completed' ? 'Selesai' : 
                      clip.status === 'processing' ? 'Memproses' : 'Antri';
    const bgColor = clip.status === 'completed' ? colors.success :
                    clip.status === 'processing' ? colors.warning : colors.muted;

    const progress = animatedProgress.value / 10;
    const progressStyle = useAnimatedStyle(() => ({
      transform: [{ translateX: progress * 150 }],
    }));

    const animatedTitle = useSharedValue(clip.title || `Klip ${index + 1}`);
    const titleAnim = useAnimatedStyle(() => ({
      transform: [{ translateY: animatedTitle.value > 0 ? 0 : -20 }],
      opacity: animatedTitle.value > 0 ? 1 : 0,
    }));

    animatedTitle.value = 1;

    return (
      <View key={clip.id} style={styles.card}>
        <Animated.View style={{ opacity: 0.8 }}>
          <Text style={styleI({ fontWeight: '600', color: clip.status === 'completed' ? colors.success : colors.text })}>
            {clip.title || `Klip ${index + 1}`}
          </Text>
          <Text style={styleI({ color: colors.muted, fontSize: 12 })}>
            {clip.start && 
            Math.floor(clip.start / 60) + ':' + (clip.start % 60).toString().padStart(2, '0') + 
            ' - ' + 
            Math.floor(clip.end / 60) + ':' + (clip.end % 60).toString().padStart(2, '0') +
            ' • ' + (clip.method === 'ai' ? 'AI' : 'Heuristic')}
          </Text>
          {clip.reason && <Text style={styleI({ color: colors.muted, fontSize: 12, fontStyle: 'italic' })}>{clip.reason}</Text>}
        </Animated.View>

        {/* Action Buttons */}
        <View style={styles.actionRow}>
          {clip.status === 'completed' && (
            <TouchableOpacity
              onPress={() => navigation.navigate('EditClip', { clipId: clip.id })}
              style={styles.btnEdit}
            >
              <Text style={styles.btnText}>Edit</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity
            onPress={async () => {
              try {
                const url = await downloadClip(clip.id);
                // Trigger download in web
                if (typeof window !== 'undefined') {
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `clip_${clip.id}.mp4`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                } else {
                  alert('Link akan dibuka di browser');
                }
              } catch (e) { alert('Gagal mendownload'); }
            }}
            style={styles.btnDownload}
          >
            <Text style={styles.btnText}>Download</Text>
          </TouchableOpacity>
        </View>

        <Text style={styleI({ color: colors.muted, fontSize: 12, marginTop: 6 })}>
          {Math.floor(clip.start / 60) + ':' + (clip.start % 60).toString().padStart(2, '0') + ' - ' +
            Math.floor(clip.end / 60) + ':' + (clip.end % 60).toString().padStart(2, '0')}
        </Text>
        {clip.tracking && <Text style={styleI({ color: colors.muted, fontSize: 12 })}>{clip.tracking === 'face' ? 'Face Tracking' : 'Center Crop'}</Text>}
      </View>
    );
  };

  const styleI = (props: any) => ({
    ...props,
    fontSize: 14,
  });

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.background }}>
        <Header showBack title="Hasil Klip" />
        <View style={{ padding: 16 }} layout="center" justifyContent="center">
          {[...Array(4)].map((_, i) => (
            <View key={i} style={{ height: 80, width: '70%', marginVertical: 8, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border }} />
          ))}
        </View>
      </View>
    );
  }

  if (error) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.background }}>
        <Header showBack title="Hasil Klip" />
        <View style={{ padding: 24, alignItems: 'center' }}>
          <Text style={{ color: colors.error, fontSize: 20, marginBottom: 16 }}>{error}</Text>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={{ backgroundColor: colors.primary, paddingVertical: 12, paddingHorizontal: 24, borderRadius: 10 }}
          >
            <Text style={{ color: '#fff', fontWeight: '600' }}>Kembali</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Hasil Klip" />
      <ScrollView style={{ flex: 1, padding: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 4 }}>
          {video?.title || 'Hasil Klip'}
        </Text>
        <Text style={{ color: colors.muted, marginBottom: 16, fontSize: 13 }}>
          {video?.clips?.length || 0} klip ditemukan
        </Text>

        {video?.clips?.map((clip: any, index: number) => renderClip(clip, index))}
      </ScrollView>
    </View>
  );
}