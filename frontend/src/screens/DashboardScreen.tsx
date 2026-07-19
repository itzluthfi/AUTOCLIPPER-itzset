import React, { useEffect, useState, useCallback, useRef } from 'react';
import { View, Text, TouchableOpacity, ScrollView, RefreshControl, Animated, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { listVideos, getCredits, checkCookieStatus } from '../services/api';

export default function DashboardScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [videos, setVideos] = useState<any[]>([]);
  const [credits, setCredits] = useState(0);
  const [loading, setLoading] = useState(true);
  const [hasCookie, setHasCookie] = useState<boolean | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 600, useNativeDriver: true }).start();
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
      case 'processing': case 'downloading': return colors.warning;
      case 'failed': return colors.error;
      default: return colors.muted;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed': return 'Selesai';
      case 'processing': return 'Memproses';
      case 'downloading': return 'Mengunduh';
      case 'pending': return 'Antri';
      case 'failed': return 'Gagal';
      case 'ready': return 'Siap';
      case 'uploaded': return 'Terupload';
      default: return status;
    }
  };

  const renderCard = (item: any) => (
    <TouchableOpacity
      key={item.id}
      onPress={() => {
        if (item.status === 'completed') {
          navigation.navigate('Results', { videoId: item.id });
        }
      }}
      style={{
        padding: 16,
        borderRadius: 12,
        backgroundColor: colors.card,
        borderWidth: 1,
        borderColor: colors.border,
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -4 },
        shadowOpacity: 0.1,
        shadowRadius: 12,
        elevation: 4,
        overflow: 'hidden',
      }}
      activeOpacity={0.7}
    >
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
    </TouchableOpacity>
  );

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <ScrollView
        contentContainerStyle={{ paddingBottom: 100 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Header */}
        <Animated.View style={{ opacity: fadeAnim, padding: 20, paddingBottom: 0 }}>
          <Text style={{ fontSize: 22, fontWeight: '700', color: colors.text }}>
            Dashboard
          </Text>
          <Text style={{ color: colors.muted, fontSize: 14, marginTop: 4 }}>
            Selamat datang kembali!
          </Text>
        </Animated.View>

        {/* Credits & Cookie Status */}
        <Animated.View style={{ opacity: fadeAnim, padding: 20, paddingBottom: 0 }}>
          <View style={{
            padding: 16, borderRadius: 12, marginBottom: 16,
            backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
          }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
              <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                <View style={{
                  width: 40, height: 40, borderRadius: 12,
                  backgroundColor: colors.primary + '20',
                  alignItems: 'center', justifyContent: 'center', marginRight: 12,
                }}>
                  <Ionicons name="wallet" size={20} color={colors.primary} />
                </View>
                <View>
                  <Text style={{ color: colors.muted, fontSize: 11 }}>Kredit Tersedia</Text>
                  <Text style={{ fontWeight: '700', color: colors.text, fontSize: 18 }}>{credits}</Text>
                </View>
              </View>
              <View style={{
                paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8,
                backgroundColor: hasCookie ? colors.success + '20' : colors.warning + '20',
                flexDirection: 'row', alignItems: 'center',
              }}>
                <Ionicons
                  name={hasCookie ? 'checkmark-circle' : 'warning'}
                  size={16}
                  color={hasCookie ? colors.success : colors.warning}
                  style={{ marginRight: 4 }}
                />
                <Text style={{
                  color: hasCookie ? colors.success : colors.warning,
                  fontSize: 12, fontWeight: '500',
                }}>
                  {hasCookie ? 'Cookie Siap' : 'Cookie?'}
                </Text>
              </View>
            </View>
          </View>

          {hasCookie === false && (
            <TouchableOpacity
              onPress={() => navigation.navigate('Profile')}
              style={{
                padding: 14, borderRadius: 12, marginBottom: 16,
                backgroundColor: colors.warning + '15',
                borderWidth: 1, borderColor: colors.warning,
                flexDirection: 'row', alignItems: 'center',
              }}
            >
              <Ionicons name="cloud-upload" size={20} color={colors.warning} style={{ marginRight: 10 }} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontWeight: '600', color: colors.text, fontSize: 13 }}>
                  Upload Cookie YouTube
                </Text>
                <Text style={{ color: colors.muted, fontSize: 11, marginTop: 2 }}>
                  Diperlukan sebelum memproses video
                </Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color={colors.muted} />
            </TouchableOpacity>
          )}
        </Animated.View>

        {/* Video List */}
        <Animated.View style={{ opacity: fadeAnim, padding: 20, paddingTop: 0 }}>
          <Text style={{ fontWeight: '600', color: colors.text, fontSize: 15, marginBottom: 12 }}>
            Video Terbaru
          </Text>
          {videos.length === 0 ? (
            <View style={{
              padding: 40, borderRadius: 12,
              backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border,
              alignItems: 'center',
            }}>
              <Ionicons name="videocam" size={48} color={colors.muted} />
              <Text style={{ color: colors.muted, fontSize: 15, marginTop: 12 }}>
                Belum ada video
              </Text>
              <TouchableOpacity
                onPress={() => navigation.navigate('CreateClip')}
                style={{
                  marginTop: 16, paddingVertical: 10, paddingHorizontal: 24,
                  borderRadius: 8, backgroundColor: hasCookie ? colors.primary : colors.muted,
                }}
              >
                <Text style={{ color: '#fff', fontWeight: '600' }}>
                  {hasCookie ? 'Buat Clip Baru' : 'Upload Cookie Dulu'}
                </Text>
              </TouchableOpacity>
            </View>
          ) : (
            videos.map(renderCard)
          )}
        </Animated.View>
      </ScrollView>
    </View>
  );
}