import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, RefreshControl, Platform, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { FadeInView } from '../components/FadeInView';
import { LiftCard } from '../components/LiftCard';
import { PageContainer } from '../components/PageContainer';
import { Button } from '../components/Button';
import { listVideos, deleteVideo } from '../services/api';
import { toast } from '../components/Toast';

const statusColor = (status: string, colors: any) => {
  switch (status) {
    case 'completed': case 'ready': case 'uploaded': return colors.success;
    case 'processing': case 'downloading': case 'subtitling': case 'detecting': case 'clipping': case 'finalizing': case 'pending': return colors.warning;
    case 'failed': return colors.error;
    default: return colors.muted;
  }
};

const statusIcon = (status: string): keyof typeof Ionicons.glyphMap => {
  switch (status) {
    case 'completed': case 'ready': return 'checkmark-circle';
    case 'uploaded': return 'cloud-done';
    case 'processing': case 'downloading': case 'subtitling': case 'detecting': case 'clipping': case 'finalizing': return 'sync-circle';
    case 'pending': return 'time';
    case 'failed': return 'alert-circle';
    default: return 'ellipse';
  }
};

const statusLabel = (status: string) => {
  switch (status) {
    case 'completed': return 'Selesai';
    case 'processing': case 'downloading': case 'subtitling': case 'detecting': case 'clipping': case 'finalizing': return 'Memproses';
    case 'pending': return 'Antri';
    case 'failed': return 'Gagal';
    case 'ready': return 'Siap';
    case 'uploaded': return 'Terupload';
    default: return status;
  }
};

export default function HistoryScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [videos, setVideos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await listVideos();
      setVideos(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error('Failed to fetch history:', e);
    }
    setLoading(false);
  };

  const handleDelete = async (videoId: number, title: string) => {
    const confirmDelete = Platform.OS === 'web'
      ? window.confirm(`Apakah Anda yakin ingin menghapus video "${title}" beserta file klipnya dari storage server?`)
      : true;

    if (!confirmDelete) return;

    try {
      await deleteVideo(videoId);
      toast.success('Video Dihapus 🗑️', 'Video dan file fisik di server berhasil dihapus.');
      fetchHistory();
    } catch (e: any) {
      toast.error('Gagal Hapus ❌', e.message || 'Gagal menghapus video');
    }
  };

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.background }}>
        <Header title="Riwayat" />
        <View style={{ padding: 16, gap: 8 }}>
          <SkeletonLoader height={80} />
          <SkeletonLoader height={80} />
          <SkeletonLoader height={80} />
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header title="Riwayat" />
      <ScrollView style={{ flex: 1 }} refreshControl={<RefreshControl refreshing={loading} onRefresh={fetchHistory} />}>
        <PageContainer maxWidth={860} style={{ padding: 16 }}>
          {videos.length === 0 ? (
            <FadeInView>
              <LiftCard style={{
                padding: 40, alignItems: 'center', borderRadius: 14,
                backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
              }}>
                <Ionicons name="time-outline" size={48} color={colors.muted} />
                <Text style={{ color: colors.muted, marginTop: 12, marginBottom: 16, fontSize: 15 }}>Belum ada riwayat</Text>
                <Button label="Buat Clip Baru" onPress={() => navigation.navigate('CreateClip')} />
              </LiftCard>
            </FadeInView>
          ) : (
            videos.map((v: any, i: number) => (
              <FadeInView key={v.id} delay={Math.min(i, 8) * 35}>
                <TouchableOpacity
                  onPress={() => navigation.navigate(v.status === 'completed' ? 'Results' : 'Processing', { videoId: v.id })}
                  activeOpacity={0.7}
                >
                  <LiftCard style={{
                    padding: 14, borderRadius: 12, backgroundColor: colors.card,
                    borderWidth: 1, borderColor: colors.border, marginBottom: 8,
                  }}>
                    <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
                      <Text style={{ fontWeight: '600', color: colors.text, flex: 1, fontSize: 14 }} numberOfLines={1}>
                        {v.title || 'Video ' + v.youtube_id}
                      </Text>
                      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                        <View style={{
                          flexDirection: 'row', alignItems: 'center', gap: 4,
                          paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6,
                          backgroundColor: statusColor(v.status, colors) + '20',
                        }}>
                          <Ionicons name={statusIcon(v.status)} size={11} color={statusColor(v.status, colors)} />
                          <Text style={{ color: statusColor(v.status, colors), fontSize: 11, fontWeight: '500' }}>{statusLabel(v.status)}</Text>
                        </View>
                        <TouchableOpacity
                          onPress={(e) => {
                            e.stopPropagation();
                            handleDelete(v.id, v.title || 'Video');
                          }}
                          style={{ padding: 4 }}
                        >
                          <Ionicons name="trash-outline" size={16} color={colors.error} />
                        </TouchableOpacity>
                      </View>
                    </View>
                    <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 4 }}>
                      <Text style={{ color: colors.muted, fontSize: 12 }}>{v.clips_count || 0} klip</Text>
                      <Text style={{ color: colors.muted, fontSize: 12 }}>{v.created_at ? new Date(v.created_at).toLocaleDateString('id-ID') : ''}</Text>
                    </View>
                  </LiftCard>
                </TouchableOpacity>
              </FadeInView>
            ))
          )}
        </PageContainer>
      </ScrollView>
    </View>
  );
}
