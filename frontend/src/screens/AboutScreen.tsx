import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';

export default function AboutScreen() {
  const { colors } = useTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Tentang" />
      <ScrollView style={{ flex: 1, padding: 16 }}>
        <View style={{ alignItems: 'center', marginVertical: 32 }}>
          <Text style={{ fontSize: 36, fontWeight: '700', color: colors.text }}>AutoClipper</Text>
          <Text style={{ color: colors.muted, fontSize: 14, marginTop: 4 }}>v1.0.0</Text>
        </View>
        <View style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16 }}>
          <Text style={{ color: colors.text, lineHeight: 22, fontSize: 14, marginBottom: 12 }}>
            AutoClipper adalah platform AI yang dirancang untuk membantu kreator konten mengubah video YouTube panjang menjadi video short secara otomatis.
          </Text>
          <Text style={{ color: colors.text, lineHeight: 22, fontSize: 14, marginBottom: 12 }}>
            Dengan teknologi AI, face tracking, dan subtitle otomatis, AutoClipper memudahkan siapa pun untuk membuat konten Shorts tanpa perlu skill editing video.
          </Text>
          <Text style={{ color: colors.muted, fontSize: 14 }}>
            Dibangun dengan: React Native (Expo), Python FastAPI, Celery, FFmpeg, OpenCV, Whisper AI
          </Text>
        </View>
        <Text style={{ textAlign: 'center', color: colors.muted, fontSize: 12, marginTop: 16 }}>
          &copy; 2026 AutoClipper. All rights reserved.
        </Text>
      </ScrollView>
    </View>
  );
}
