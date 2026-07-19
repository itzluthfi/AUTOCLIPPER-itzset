import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, TouchableOpacity, ScrollView, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { getApiKey } from '../services/api'; // Import getApiKey

const statusColor = (status: string, colors: any) => {
  switch (status) {
    case 'completed': case 'ready': case 'uploaded': return colors.success;
    case 'processing': case 'downloading': case 'pending': return colors.warning;
    case 'failed': return colors.error;
    default: return colors.muted;
  }
};

const statusIcon = (status: string): keyof typeof Ionicons.glyphMap => {
  switch (status) {
    case 'completed': case 'ready': return 'checkmark-circle';
    case 'uploaded': return 'cloud-done';
    case 'processing': case 'downloading': return 'sync-circle';
    case 'pending': return 'time';
    case 'failed': return 'alert-circle';
    default: return 'ellipse';
  }
};

const statusLabel = (status: string) => {
  switch (status) {
    case 'completed': return 'Selesai';
    case 'processing': case 'downloading': return 'Memproses';
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
      const key = await getApiKey();
      if (!key) {
        setLoading(false);
        return;
      }
      const resp = await fetch('https://autoclipper.sir-l.web.id/api/user/videos', {
        headers: { 'X-API-Key': key },
      });
      if (resp.ok) setVideos(await resp.json());
      else console.error('Failed to fetch history:', await resp.text());
    } catch (e) { console.error(e); }
    setLoading(false);
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
      <ScrollView style={{ flex: 1, padding: 16 }} refreshControl={<RefreshControl refreshing={loading} onRefresh={fetchHistory} />}>
        {videos.length === 0 ? (
          <View style={{ padding: 40, alignItems: 'center' }}>
            <Ionicons name="time-outline" size={48} color={colors.muted} />
            <Text style={{ color: colors.muted, marginTop: 12, fontSize: 15 }}>Belum ada riwayat</Text>
            <TouchableOpacity
              onPress={() => navigation.navigate('CreateClip')}
              style={{ marginTop: 16, paddingVertical: 12, paddingHorizontal: 24, borderRadius: 12, backgroundColor: colors.primary }}
            >
              <Text style={{ color: '#fff', fontWeight: '600' }}>Buat Clip Baru</Text>
            </TouchableOpacity>
          </View>
        ) : (
          videos.map((v: any) => (
            <TouchableOpacity
              key={v.id}
              onPress={() => navigation.navigate('Results', { videoId: v.id })}
              style={{ padding: 14, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 8 }}
              activeOpacity={0.7}
            >
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
                <Text style={{ fontWeight: '600', color: colors.text, flex: 1, fontSize: 14 }} numberOfLines={1}>
                  {v.title || 'Video ' + v.youtube_id}
                </Text>
                <View style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, backgroundColor: statusColor(v.status, colors) + '20' }}>
                  <Text style={{ color: statusColor(v.status, colors), fontSize: 11, fontWeight: '500' }}>{statusLabel(v.status)}</Text>
                </View>
              </View>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 4 }}>
                <Text style={{ color: colors.muted, fontSize: 12 }}>{v.clips_count || 0} klip</Text>
                <Text style={{ color: colors.muted, fontSize: 12 }}>{v.created_at ? new Date(v.created_at).toLocaleDateString('id-ID') : ''}</Text>
              </View>
            </TouchableOpacity>
          ))
        )}
      </ScrollView>
    </View>
  );
}
