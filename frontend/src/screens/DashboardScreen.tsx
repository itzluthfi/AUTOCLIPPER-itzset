import React, { useEffect, useState, useRef } from 'react';
import { View, Text, TouchableOpacity, ScrollView, RefreshControl, useWindowDimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { FadeInView } from '../components/FadeInView';
import { LiftCard } from '../components/LiftCard';
import { StatTile } from '../components/StatTile';
import { PageContainer } from '../components/PageContainer';
import { Button } from '../components/Button';
import { listVideos, getCredits, checkCookieStatus } from '../services/api';

export default function DashboardScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const { width } = useWindowDimensions();
  const isTablet = width >= 640;
  const [videos, setVideos] = useState<any[]>([]);
  const [credits, setCredits] = useState(0);
  const [loading, setLoading] = useState(true);
  const [hasCookie, setHasCookie] = useState<boolean | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [v, c, cookie] = await Promise.all([
        listVideos(),
        getCredits().catch(() => ({ credits: 0 })),
        checkCookieStatus().catch(() => ({ has_cookie: false })),
      ]);
      setVideos(v || []);
      setCredits(c.credits || 0);
      setHasCookie(cookie.has_cookie);
    } catch (e) {
      console.error('Dashboard load error:', e);
    }
    setLoading(false);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.background, padding: 20 }}>
        <SkeletonLoader height={40} />
        <SkeletonLoader height={80} style={{ marginTop: 12 }} />
        <SkeletonLoader height={80} style={{ marginTop: 8 }} />
        <SkeletonLoader height={80} style={{ marginTop: 8 }} />
      </View>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return colors.success;
      case 'processing': case 'downloading': case 'subtitling': case 'detecting': case 'clipping': case 'finalizing': return colors.warning;
      case 'failed': return colors.error;
      default: return colors.muted;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed': return 'Selesai';
      case 'processing': return 'Memproses';
      case 'downloading': return 'Mengunduh';
      case 'subtitling': return 'Subtitle';
      case 'detecting': return 'Menganalisis';
      case 'clipping': return 'Memotong';
      case 'finalizing': return 'Finalisasi';
      case 'pending': return 'Antri';
      case 'failed': return 'Gagal';
      case 'ready': return 'Siap';
      case 'uploaded': return 'Terupload';
      default: return status;
    }
  };

  const totalClips = videos.reduce((sum, v) => sum + (v.clips_count || 0), 0);
  const totalVideos = videos.length;
  const completedVideos = videos.filter(v => v.status === 'completed').length;

  const renderCard = (item: any, index: number) => (
    <FadeInView key={item.id} delay={Math.min(index, 6) * 40}>
      <TouchableOpacity
        onPress={() => {
          if (item.status === 'completed') {
            navigation.navigate('Results', { videoId: item.id });
          } else if (item.status === 'failed') {
            navigation.navigate('CreateClip');
          } else {
            navigation.navigate('Processing', { videoId: item.id });
          }
        }}
        activeOpacity={0.7}
      >
        <LiftCard style={{
          padding: 16,
          borderRadius: 12,
          backgroundColor: colors.card,
          borderWidth: 1,
          borderColor: colors.border,
          marginBottom: 10,
        }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 }}>
            <Text style={{ fontWeight: '600', color: colors.text, flex: 1, fontSize: 14 }} numberOfLines={1}>
              {item.title || 'Video ' + item.youtube_id}
            </Text>
            <View style={{
              paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6,
              backgroundColor: getStatusColor(item.status) + '20',
            }}>
              <Text style={{ color: getStatusColor(item.status), fontSize: 11, fontWeight: '500' }}>
                {getStatusLabel(item.status)}
              </Text>
            </View>
          </View>
          <Text style={{ color: colors.muted, fontSize: 12 }}>
            {item.clips_count || 0} klip · {item.duration ? Math.floor(item.duration / 60) + 'm' : '?'}
          </Text>
        </LiftCard>
      </TouchableOpacity>
    </FadeInView>
  );

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <ScrollView
        contentContainerStyle={{ paddingBottom: 100 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <PageContainer maxWidth={960}>
          {/* Header */}
          <FadeInView style={{ padding: 20, paddingBottom: 0 }}>
            <Text style={{ fontSize: 22, fontWeight: '700', color: colors.text }}>Dashboard</Text>
            <Text style={{ color: colors.muted, fontSize: 14, marginTop: 4 }}>Selamat datang kembali!</Text>
          </FadeInView>

          {/* Stat Tiles */}
          <FadeInView delay={60} style={{ padding: 20, paddingBottom: 0 }}>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
              <StatTile icon="wallet" color={colors.primary} label="Kredit Tersedia" value={credits} />
              <StatTile icon="film" color="#06b6d4" label="Total Klip" value={totalClips} />
              <StatTile icon="checkmark-done" color="#22c55e" label="Video Selesai" value={completedVideos} />
            </View>

            {hasCookie === false && (
              <TouchableOpacity onPress={() => navigation.navigate('Profile')}>
                <LiftCard style={{
                  padding: 14, borderRadius: 12, marginBottom: 16,
                  backgroundColor: colors.warning + '15',
                  borderWidth: 1, borderColor: colors.warning,
                  flexDirection: 'row', alignItems: 'center',
                }}>
                  <Ionicons name="cloud-upload" size={20} color={colors.warning} style={{ marginRight: 10 }} />
                  <View style={{ flex: 1 }}>
                    <Text style={{ fontWeight: '600', color: colors.text, fontSize: 13 }}>Upload Cookie YouTube</Text>
                    <Text style={{ color: colors.muted, fontSize: 11, marginTop: 2 }}>Diperlukan sebelum memproses video</Text>
                  </View>
                  <Ionicons name="chevron-forward" size={18} color={colors.muted} />
                </LiftCard>
              </TouchableOpacity>
            )}
          </FadeInView>

          {/* Video List */}
          <FadeInView delay={100} style={{ padding: 20, paddingTop: 0 }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <Text style={{ fontWeight: '600', color: colors.text, fontSize: 15 }}>Video Terbaru</Text>
              {videos.length > 0 && (
                <Button label="Buat Baru" size="md" variant="ghost" icon="add" onPress={() => navigation.navigate('CreateClip')} />
              )}
            </View>
            {videos.length === 0 ? (
              <LiftCard style={{
                padding: 40, borderRadius: 12,
                backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
                alignItems: 'center',
              }}>
                <Ionicons name="videocam" size={48} color={colors.muted} />
                <Text style={{ color: colors.muted, fontSize: 15, marginTop: 12, marginBottom: 16 }}>
                  Belum ada video
                </Text>
                <Button
                  label={hasCookie ? 'Buat Clip Baru' : 'Upload Cookie Dulu'}
                  onPress={() => navigation.navigate(hasCookie ? 'CreateClip' : 'Profile')}
                />
              </LiftCard>
            ) : (
              videos.map(renderCard)
            )}
          </FadeInView>
        </PageContainer>
      </ScrollView>
    </View>
  );
}
