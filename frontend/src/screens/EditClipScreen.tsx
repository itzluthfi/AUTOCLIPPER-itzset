import React, { useState, useEffect, useCallback, useRef } from 'react';
import { View, Text, TextInput, ScrollView, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { getClip, updateClip } from '../services/api';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { PageContainer } from '../components/PageContainer';
import { LiftCard } from '../components/LiftCard';
import { Button } from '../components/Button';

const ANIM_DURATION = 500;

export default function EditClipScreen({ route, navigation }: any) {
  const { clipId } = route.params;
  const { colors, isDark } = useTheme();
  const [clip, setClip] = useState<any>(null);
  const [title, setTitle] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const loadClip = useCallback(async () => {
    try {
      const fetchedClip = await getClip(clipId);
      setClip(fetchedClip);
      setTitle(fetchedClip.title || '');
      setStartTime(String(fetchedClip.start));
      setEndTime(String(fetchedClip.end));
      setSubtitle(fetchedClip.subtitle || '');
      Animated.timing(fadeAnim, { toValue: 1, duration: ANIM_DURATION, useNativeDriver: true }).start();
    } catch (e) {
      console.error('Error loading clip:', e);
      alert('Gagal memuat klip');
    } finally {
      setLoading(false);
    }
  }, [clipId]);

  useEffect(() => {
    loadClip();
  }, [loadClip]);

  const startNum = parseInt(startTime || '0', 10);
  const endNum = parseInt(endTime || '0', 10);
  const rangeInvalid = !isNaN(startNum) && !isNaN(endNum) && endNum <= startNum;

  const handleSave = async () => {
    if (rangeInvalid) {
      alert('Waktu selesai harus lebih besar dari waktu mulai');
      return;
    }
    setSaving(true);
    try {
      await updateClip(clipId, {
        title,
        start: startNum,
        end: endNum,
        subtitle,
      });
      navigation.goBack();
    } catch (e) {
      console.error('Error saving clip:', e);
      alert('Gagal menyimpan perubahan');
    } finally {
      setSaving(false);
    }
  };

  const inputStyle = (hasError = false) => ({
    backgroundColor: isDark ? '#0f0f0f' : '#f8fafc',
    borderWidth: 1,
    borderColor: hasError ? colors.error : colors.border,
    borderRadius: 10,
    padding: 14,
    fontSize: 14,
    color: colors.text,
    marginBottom: 8,
  });

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.background }}>
        <Header showBack title="Edit Klip" />
        <View style={{ padding: 16, gap: 16 }}>
          <SkeletonLoader height={180} />
          <SkeletonLoader height={100} />
          <SkeletonLoader height={150} />
          <SkeletonLoader height={50} />
        </View>
      </View>
    );
  }

  if (!clip) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.background, justifyContent: 'center', alignItems: 'center' }}>
        <Text style={{ color: colors.error, fontSize: 18 }}>Klip tidak ditemukan.</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Edit Klip" />
      <Animated.ScrollView style={{ flex: 1, opacity: fadeAnim }} contentContainerStyle={{ padding: 16 }}>
        <PageContainer maxWidth={640}>

          {/* Preview */}
          <LiftCard style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16 }}>
            <Text style={{ fontWeight: '700', color: colors.text, marginBottom: 12, fontSize: 16 }}>Preview</Text>
            <View style={{ height: 200, borderRadius: 8, alignItems: 'center', justifyContent: 'center', backgroundColor: isDark ? '#0f0f0f' : '#f1f5f9' }}>
              <Ionicons name="film-outline" size={48} color={colors.muted} />
              <Text style={{ color: colors.muted, marginTop: 8 }}>Preview Video</Text>
            </View>
          </LiftCard>

          {/* Timeline */}
          <LiftCard style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16 }}>
            <Text style={{ fontWeight: '700', color: colors.text, marginBottom: 12, fontSize: 16 }}>Timeline</Text>
            <View style={{ flexDirection: 'row', gap: 12 }}>
              <View style={{ flex: 1 }}>
                <Text style={{ color: colors.muted, fontSize: 13, marginBottom: 6 }}>Mulai (detik)</Text>
                <TextInput
                  value={startTime}
                  onChangeText={(text) => setStartTime(text.replace(/[^0-9]/g, ''))}
                  placeholder="0"
                  placeholderTextColor={colors.muted}
                  keyboardType="numeric"
                  style={inputStyle(rangeInvalid)}
                />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ color: colors.muted, fontSize: 13, marginBottom: 6 }}>Selesai (detik)</Text>
                <TextInput
                  value={endTime}
                  onChangeText={(text) => setEndTime(text.replace(/[^0-9]/g, ''))}
                  placeholder="60"
                  placeholderTextColor={colors.muted}
                  keyboardType="numeric"
                  style={inputStyle(rangeInvalid)}
                />
              </View>
            </View>
            {rangeInvalid && (
              <Text style={{ color: colors.error, fontSize: 12, marginTop: 4 }}>
                Waktu selesai harus lebih besar dari waktu mulai.
              </Text>
            )}
          </LiftCard>

          {/* Metadata */}
          <LiftCard style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16 }}>
            <Text style={{ fontWeight: '700', color: colors.text, marginBottom: 12, fontSize: 16 }}>Judul & Subtitle</Text>
            <TextInput
              value={title}
              onChangeText={setTitle}
              placeholder="Judul klip"
              placeholderTextColor={colors.muted}
              style={inputStyle()}
            />
            <TextInput
              value={subtitle}
              onChangeText={setSubtitle}
              placeholder="Edit teks subtitle..."
              placeholderTextColor={colors.muted}
              multiline
              numberOfLines={4}
              style={[inputStyle(), { minHeight: 100, textAlignVertical: 'top' }]}
            />
          </LiftCard>

          <Button
            label={saving ? 'Menyimpan...' : 'Simpan Perubahan'}
            loading={saving}
            disabled={rangeInvalid}
            fullWidth
            onPress={handleSave}
          />
        </PageContainer>
      </Animated.ScrollView>
    </View>
  );
}
