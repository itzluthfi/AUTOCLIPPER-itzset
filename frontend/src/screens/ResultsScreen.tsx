import React, { useEffect, useState, useCallback, useRef } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Image, StyleSheet, Animated, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { ProgressBar } from '../components/ProgressBar';
import { getVideo, downloadClip, getApiKey, API_BASE } from '../services/api';

export default function ResultsScreen({ route, navigation }: any) {
  const { videoId } = route.params;
  const { colors, isDark } = useTheme();
  const [video, setVideo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [playingClipId, setPlayingClipId] = useState<number | null>(null);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const loadVideo = async () => {
    try {
      const v = await getVideo(videoId);
      setVideo(v);
    } catch (e) { setError('Gagal memuat hasil'); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    loadVideo();
    getApiKey().then(setApiKey);
  }, [videoId]);

  const renderClip = (clip: any, index: number) => {
    const clipStatus = clip.status === 'completed' ? 'Selesai' : 
                      clip.status === 'processing' ? 'Memproses' : 'Antri';
    const bgColor = clip.status === 'completed' ? colors.success :
                    clip.status === 'processing' ? colors.warning : colors.muted;

    return (
      <View key={clip.id} style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
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
          {clip.status === 'ready' || clip.status === 'completed' ? (
            <>
              <TouchableOpacity
                onPress={() => setPlayingClipId(clip.id)}
                style={[styles.btnEdit, { backgroundColor: isDark ? '#1a1a1a' : '#f1f5f9', borderWidth: 1, borderColor: colors.border }]}
              >
                <Text style={[styles.btnText, { color: colors.text }]}>▶ Play</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => navigation.navigate('EditClip', { clipId: clip.id })}
                style={styles.btnEdit}
              >
                <Text style={styles.btnText}>Edit</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={async () => {
                  try {
                    const url = await downloadClip(clip.id);
                    if (Platform.OS === 'web') {
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `clip_${clip.id}.mp4`;
                      document.body.appendChild(a);
                      a.click();
                      document.body.removeChild(a);
                    } else {
                      alert('Link download akan dibuka di browser.');
                    }
                  } catch (e) {
                    alert('Gagal mendownload klip.');
                  }
                }}
                style={styles.btnDownload}
              >
                <Text style={styles.btnText}>Download</Text>
              </TouchableOpacity>
            </>
          ) : clip.status === 'processing' || clip.status === 'downloading' ? (
            <View style={[styles.btnDownload, { backgroundColor: colors.warning + '30', flex: 1, borderWidth: 1, borderColor: colors.warning, paddingVertical: 8, borderRadius: 8, alignItems: 'center' }]}>
              <Text style={{ color: colors.warning, fontWeight: '600', fontSize: 13 }}>⏳ Sedang Diproses...</Text>
            </View>
          ) : clip.status === 'failed' ? (
            <View style={[styles.btnDownload, { backgroundColor: colors.error + '30', flex: 1, borderWidth: 1, borderColor: colors.error, paddingVertical: 8, borderRadius: 8, alignItems: 'center' }]}>
              <Text style={{ color: colors.error, fontWeight: '600', fontSize: 13 }}>❌ Gagal Memproses</Text>
            </View>
          ) : (
            <View style={[styles.btnDownload, { backgroundColor: colors.card, flex: 1, borderWidth: 1, borderColor: colors.border, paddingVertical: 8, borderRadius: 8, alignItems: 'center' }]}>
              <Text style={{ color: colors.muted, fontWeight: '600', fontSize: 13 }}>🕒 Mengantri...</Text>
            </View>
          )}
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
        <View style={{ padding: 16, justifyContent: 'center', alignItems: 'center' }}>
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

      {/* Video Player Modal Overlay */}
      {playingClipId !== null && (
        <View style={{
          position: 'absolute', top: 0, bottom: 0, left: 0, right: 0,
          backgroundColor: 'rgba(0,0,0,0.85)', justifyContent: 'center', alignItems: 'center',
          padding: 20, zIndex: 9999,
        }}>
          <View style={{
            width: '100%', maxWidth: 500, backgroundColor: colors.card,
            borderRadius: 16, padding: 16, borderWidth: 1, borderColor: colors.border,
          }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <Text style={{ fontWeight: '700', color: colors.text, fontSize: 16 }}>Preview Klip</Text>
              <TouchableOpacity onPress={() => setPlayingClipId(null)} style={{ padding: 4 }}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>

            {Platform.OS === 'web' ? (
              <video
                src={`${API_BASE}/clips/${playingClipId}/file?key=${apiKey}`}
                controls
                autoPlay
                style={{ width: '100%', borderRadius: 8, maxHeight: 400, backgroundColor: '#000' }}
              />
            ) : (
              <View style={{ height: 200, backgroundColor: '#000', borderRadius: 8, justifyContent: 'center', alignItems: 'center' }}>
                <Ionicons name="play-circle" size={48} color={colors.primary} />
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
  card: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#fff',
  },
  actionRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 12,
  },
  btnEdit: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#3182ce',
    alignItems: 'center',
  },
  btnDownload: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#2ecc71',
    alignItems: 'center',
  },
  btnText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 13,
  },
});