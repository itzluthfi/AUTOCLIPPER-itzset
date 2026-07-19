import React, { useState, useEffect, useCallback, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Animated, StyleSheet, Platform, Easing } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { getClip, updateClip } from '../services/api';
import { SkeletonLoader } from '../components/SkeletonLoader';

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
  const fadeAnim = useRef(new Animated.Value(0)).current; // For fade-in effect

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

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateClip(clipId, {
        title: title,
        start: parseInt(startTime),
        end: parseInt(endTime),
        subtitle: subtitle,
      });
      alert('Perubahan disimpan!');
      navigation.goBack();
    } catch (e) {
      console.error('Error saving clip:', e);
      alert('Gagal menyimpan perubahan');
    } finally {
      setSaving(false);
    }
  };

  const handleApplyTimeline = () => {
    // Logic to apply timeline changes to video preview, not implemented in this mock
    alert('Timeline diterapkan!');
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
      <Animated.ScrollView style={{ flex: 1, padding: 16, opacity: fadeAnim }}>
        {/* Preview Section */}
        <View style={styles.sectionContainer}>
          <Text style={styles.sectionTitle}>Preview</Text>
          <View style={[styles.videoPlaceholder, { backgroundColor: isDark ? colors.card : '#f1f5f9' }]}>
            <Ionicons name="film-outline" size={48} color={colors.muted} />
            <Text style={{ color: colors.muted, marginTop: 8 }}>Preview Video</Text>
          </View>
        </View>

        {/* Timeline Section */}
        <View style={styles.sectionContainer}>
          <Text style={styles.sectionTitle}>Timeline</Text>
          <View style={{ flexDirection: 'row', gap: 12, marginBottom: 12 }}>
            <View style={{ flex: 1 }}>
              <Text style={styles.inputLabel}>Mulai (detik)</Text>
              <TextInput
                value={startTime}
                onChangeText={(text) => setStartTime(text.replace(/[^0-9]/g, ''))}
                placeholder="0"
                placeholderTextColor={colors.muted}
                keyboardType="numeric"
                style={inputStyle()}
              />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.inputLabel}>Selesai (detik)</Text>
              <TextInput
                value={endTime}
                onChangeText={(text) => setEndTime(text.replace(/[^0-9]/g, ''))}
                placeholder="60"
                placeholderTextColor={colors.muted}
                keyboardType="numeric"
                style={inputStyle()}
              />
            </View>
          </View>
          <TouchableOpacity onPress={handleApplyTimeline} style={styles.applyButton}>
            <Text style={styles.applyButtonText}>Terapkan Timeline</Text>
          </TouchableOpacity>
        </View>

        {/* Metadata Section */}
        <View style={styles.sectionContainer}>
          <Text style={styles.sectionTitle}>Judul & Subtitle</Text>
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
        </View>

        <TouchableOpacity
          onPress={handleSave}
          disabled={saving}
          style={[styles.saveButton, saving && styles.saveButtonDisabled]}
        >
          <Text style={styles.saveButtonText}>
            {saving ? 'Menyimpan...' : 'Simpan Perubahan'}
          </Text>
        </TouchableOpacity>
      </Animated.ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  sectionContainer: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: '#1E1E1E',
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  sectionTitle: {
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 12,
    fontSize: 18,
  },
  videoPlaceholder: {
    height: 200,
    backgroundColor: '#2A2A2A',
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  inputLabel: {
    color: '#BBBBBB',
    fontSize: 13,
    marginBottom: 6,
  },
  applyButton: {
    paddingVertical: 12,
    borderRadius: 10,
    backgroundColor: '#007AFF',
    alignItems: 'center',
    marginTop: 12,
  },
  applyButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  saveButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 6,
  },
  saveButtonDisabled: {
    backgroundColor: '#A0A0A0',
    shadowColor: 'transparent',
  },
  saveButtonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
});
