import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Image, StyleSheet, Platform, Alert, Linking, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { FadeInView } from '../components/FadeInView';
import { LiftCard } from '../components/LiftCard';
import { PageContainer } from '../components/PageContainer';
import { Badge } from '../components/Badge';
import { getVideo, uploadClip, getApiKey, API_BASE } from '../services/api';

export default function ResultsScreen({ route, navigation }: any) {
  const { videoId } = route.params;
  const { colors, isDark } = useTheme();
  const [video, setVideo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [playingClipId, setPlayingClipId] = useState<number | null>(null);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [uploadingClipId, setUploadingClipId] = useState<number | null>(null);

  const loadVideo = async () => {
    try {
      const v = await getVideo(videoId);
      setVideo(v);
    } catch (e) {
      setError('Gagal memuat hasil klip');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVideo();
    getApiKey().then(setApiKey);
  }, [videoId]);

  const handleDownload = async (clipId: number) => {
    try {
      const key = await getApiKey();
      const downloadUrl = `${API_BASE}/clips/${clipId}/download?key=${key || ''}`;
      
      if (Platform.OS === 'web') {
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `clip_${clipId}.mp4`;
        a.target = '_blank';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      } else {
        window.open(downloadUrl, '_blank');
      }
    } catch (e) {
      alert('Gagal mendownload klip.');
    }
  };

  const handleUploadYouTube = async (clip: any) => {
    // Jika sudah terupload, buka linknya
    if (clip.youtube_url) {
      Linking.openURL(clip.youtube_url);
      return;
    }
    setUploadingClipId(clip.id);
    try {
      const res = await uploadClip(clip.id);
      Alert.alert(
        'Upload Berhasil',
        `Klip Shorts berhasil diunggah ke YouTube Shorts!\n\n${res.url}`,
        [
          { text: 'Buka di YouTube', onPress: () => Linking.openURL(res.url) },
          { text: 'OK', style: 'cancel' },
        ]
      );
      loadVideo();
    } catch (e: any) {
      Alert.alert(
        'Gagal Upload',
        e.message || 'Gagal mengunggah klip. Pastikan akun YouTube sudah terhubung melalui Login Google di Profil.'
      );
    } finally {
      setUploadingClipId(null);
    }
  };

  const renderClip = (clip: any, index: number) => {
    const isReady = clip.status === 'ready' || clip.status === 'completed';

    return (
      <FadeInView key={clip.id} delay={Math.min(index, 6) * 50}>
      <LiftCard style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
        <View style={{ flexDirection: 'row', gap: 12 }}>
          {/* Thumbnail preview */}
          {isReady && apiKey ? (
            <View style={{ width: 80, height: 120, borderRadius: 8, overflow: 'hidden', backgroundColor: '#000', position: 'relative' }}>
              <Image
                source={{ uri: `${API_BASE}/clips/${clip.id}/thumbnail?key=${apiKey}` }}
                style={{ width: '100%', height: '100%', resizeMode: 'cover' }}
              />
              <TouchableOpacity
                onPress={() => setPlayingClipId(clip.id)}
                style={{
                  position: 'absolute', top: 0, bottom: 0, left: 0, right: 0,
                  justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.3)',
                }}
              >
                <Ionicons name="play-circle" size={32} color="#fff" />
              </TouchableOpacity>
            </View>
          ) : null}

          <View style={{ flex: 1 }}>
            <Text style={{ fontWeight: '700', color: colors.text, fontSize: 15, marginBottom: 4 }}>
              {clip.title || `Klip #${index + 1}`}
            </Text>

            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4, marginBottom: 6, flexWrap: 'wrap' }}>
              <Ionicons name="time-outline" size={12} color={colors.muted} />
              <Text style={{ color: colors.muted, fontSize: 12 }}>
                {Math.floor(clip.start / 60)}:{(clip.start % 60).toString().padStart(2, '0')} - {Math.floor(clip.end / 60)}:{(clip.end % 60).toString().padStart(2, '0')}
              </Text>
              <Badge label={clip.method === 'ai' ? 'AI' : 'Heuristic'} icon={clip.method === 'ai' ? 'sparkles' : 'flash'} color={clip.method === 'ai' ? '#8b5cf6' : colors.muted} />
            </View>

            {clip.tracking ? (
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4, marginBottom: 4 }}>
                <Ionicons name="locate-outline" size={12} color={colors.primary} />
                <Text style={{ color: colors.primary, fontSize: 11, fontWeight: '500' }}>
                  {clip.tracking === 'face' ? 'Face Tracking' : clip.tracking === 'speaker' ? 'Speaker Tracking' : clip.tracking === 'auto' ? 'Auto Mix Framing' : 'Center Crop'}
                </Text>
              </View>
            ) : null}

            {clip.reason ? (
              <Text style={{ color: colors.muted, fontSize: 12, fontStyle: 'italic' }} numberOfLines={2}>
                "{clip.reason}"
              </Text>
            ) : null}

            {clip.youtube_url ? (
              <TouchableOpacity
                onPress={() => Linking.openURL(clip.youtube_url)}
                style={{ flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 4 }}
              >
                <Ionicons name="logo-youtube" size={13} color="#FF0000" />
                <Text style={{ color: '#FF0000', fontSize: 11, fontWeight: '600' }}>Sudah Diupload — Buka Shorts</Text>
                <Ionicons name="open-outline" size={11} color="#FF0000" />
              </TouchableOpacity>
            ) : null}
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionRow}>
          {isReady ? (
            <>
              <TouchableOpacity
                onPress={() => setPlayingClipId(clip.id)}
                style={[styles.btnAction, { backgroundColor: isDark ? '#1e293b' : '#f1f5f9', borderWidth: 1, borderColor: colors.border }]}
              >
                <Ionicons name="play" size={16} color={colors.text} />
                <Text style={[styles.btnText, { color: colors.text }]}>Play</Text>
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => navigation.navigate('EditClip', { clipId: clip.id })}
                style={[styles.btnAction, { backgroundColor: colors.primary }]}
              >
                <Ionicons name="create-outline" size={16} color="#fff" />
                <Text style={styles.btnText}>Edit</Text>
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => handleDownload(clip.id)}
                style={[styles.btnAction, { backgroundColor: colors.success }]}
              >
                <Ionicons name="download-outline" size={16} color="#fff" />
                <Text style={styles.btnText}>Download</Text>
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => handleUploadYouTube(clip)}
                style={[styles.btnAction, { backgroundColor: clip.youtube_url ? '#28a745' : '#FF0000', opacity: uploadingClipId === clip.id ? 0.6 : 1 }]}
                disabled={uploadingClipId === clip.id}
              >
                {uploadingClipId === clip.id ? (
                  <ActivityIndicator size={14} color="#fff" />
                ) : (
                  <Ionicons name={clip.youtube_url ? 'checkmark-circle' : 'logo-youtube'} size={16} color="#fff" />
                )}
                <Text style={styles.btnText}>
                  {uploadingClipId === clip.id ? 'Uploading...' : clip.youtube_url ? 'Sudah Upload' : 'Upload Shorts'}
                </Text>
              </TouchableOpacity>
            </>
          ) : clip.status === 'processing' || clip.status === 'clipping' ? (
            <View style={[styles.statusBanner, { backgroundColor: colors.warning + '20', borderColor: colors.warning, flexDirection: 'row', gap: 6 }]}>
              <Ionicons name="sync-outline" size={14} color={colors.warning} />
              <Text style={{ color: colors.warning, fontWeight: '600', fontSize: 13 }}>Sedang Memproses Klip...</Text>
            </View>
          ) : clip.status === 'failed' ? (
            <View style={[styles.statusBanner, { backgroundColor: colors.error + '20', borderColor: colors.error, flexDirection: 'row', gap: 6 }]}>
              <Ionicons name="alert-circle-outline" size={14} color={colors.error} />
              <Text style={{ color: colors.error, fontWeight: '600', fontSize: 13 }}>Gagal Memproses Klip</Text>
            </View>
          ) : (
            <View style={[styles.statusBanner, { backgroundColor: colors.card, borderColor: colors.border, flexDirection: 'row', gap: 6 }]}>
              <Ionicons name="time-outline" size={14} color={colors.muted} />
              <Text style={{ color: colors.muted, fontWeight: '600', fontSize: 13 }}>Dalam Antrean...</Text>
            </View>
          )}
        </View>
      </LiftCard>
      </FadeInView>
    );
  };

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.background }}>
        <Header showBack title="Hasil Klip" />
        <View style={{ padding: 20, gap: 16 }}>
          {[...Array(3)].map((_, i) => (
            <View key={i} style={{ height: 120, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border }} />
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
          <Text style={{ color: colors.error, fontSize: 18, marginBottom: 16 }}>{error}</Text>
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
      <Header showBack title="Hasil Klip Video" />

      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        <PageContainer maxWidth={860}>
        <FadeInView>
          <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 4 }}>
            {video?.title || 'Hasil Klip Video'}
          </Text>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
              <Ionicons name="checkmark-done-circle" size={14} color={colors.success} />
              <Text style={{ color: colors.muted, fontSize: 13 }}>
                {video?.clips?.length || 0} klip berhasil dihasilkan
              </Text>
            </View>
            {route.params?.elapsedSeconds ? (
              <View style={{
                flexDirection: 'row', alignItems: 'center', gap: 4,
                backgroundColor: colors.success + '20', paddingVertical: 2, paddingHorizontal: 8,
                borderRadius: 6, borderWidth: 1, borderColor: colors.success + '50',
              }}>
                <Ionicons name="stopwatch-outline" size={12} color={colors.success} />
                <Text style={{ color: colors.success, fontSize: 11, fontWeight: '600' }}>
                  Diproses dalam {Math.floor(route.params.elapsedSeconds / 60)}m {route.params.elapsedSeconds % 60}s
                </Text>
              </View>
            ) : null}
          </View>
        </FadeInView>

        {video?.clips?.map((clip: any, index: number) => renderClip(clip, index))}
        </PageContainer>
      </ScrollView>

      {/* Video Player Modal Overlay */}
      {playingClipId !== null && (
        <View style={{
          position: 'absolute', top: 0, bottom: 0, left: 0, right: 0,
          backgroundColor: 'rgba(0,0,0,0.85)', justifyContent: 'center', alignItems: 'center',
          padding: 20, zIndex: 9999,
        }}>
          <View style={{
            width: '100%', maxWidth: 420, backgroundColor: colors.card,
            borderRadius: 16, padding: 16, borderWidth: 1, borderColor: colors.border,
          }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <Text style={{ fontWeight: '700', color: colors.text, fontSize: 16 }}>Preview Klip 9:16</Text>
              <TouchableOpacity onPress={() => setPlayingClipId(null)} style={{ padding: 4 }}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>

            {Platform.OS === 'web' ? (
              <video
                src={`${API_BASE}/clips/${playingClipId}/file?key=${apiKey}`}
                controls
                autoPlay
                style={{ width: '100%', borderRadius: 10, maxHeight: 520, backgroundColor: '#000' }}
              />
            ) : (
              <View style={{ height: 300, backgroundColor: '#000', borderRadius: 10, justifyContent: 'center', alignItems: 'center' }}>
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
    borderRadius: 14,
    marginBottom: 14,
    borderWidth: 1,
  },
  actionRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 14,
  },
  btnAction: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 6,
  },
  btnText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 13,
  },
  statusBanner: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
  },
});