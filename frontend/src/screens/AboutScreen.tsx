import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { PageContainer } from '../components/PageContainer';
import { LiftCard } from '../components/LiftCard';
import { FadeInView } from '../components/FadeInView';

const stack = [
  { icon: 'logo-react' as const, name: 'React Native (Expo)' },
  { icon: 'server-outline' as const, name: 'Python FastAPI' },
  { icon: 'sync-outline' as const, name: 'Celery + Redis' },
  { icon: 'film-outline' as const, name: 'FFmpeg' },
  { icon: 'eye-outline' as const, name: 'OpenCV' },
  { icon: 'mic-outline' as const, name: 'Whisper AI' },
];

export default function AboutScreen() {
  const { colors, isDark } = useTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Tentang" />
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <PageContainer maxWidth={640}>
          <FadeInView>
            <View style={{ alignItems: 'center', marginVertical: 24 }}>
              <View style={{ width: 64, height: 64, borderRadius: 18, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
                <Ionicons name="film" size={32} color="#fff" />
              </View>
              <Text style={{ fontSize: 28, fontWeight: '800', color: colors.text }}>AutoClipper</Text>
              <Text style={{ color: colors.muted, fontSize: 13, marginTop: 4 }}>v1.0.0</Text>
            </View>
          </FadeInView>

          <FadeInView delay={60}>
            <LiftCard style={{ padding: 18, borderRadius: 14, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16 }}>
              <Text style={{ color: colors.text, lineHeight: 22, fontSize: 14, marginBottom: 12 }}>
                AutoClipper adalah platform AI yang dirancang untuk membantu kreator konten mengubah video YouTube panjang menjadi video short secara otomatis.
              </Text>
              <Text style={{ color: colors.text, lineHeight: 22, fontSize: 14 }}>
                Dengan teknologi AI, deteksi wajah, dan subtitle otomatis, AutoClipper memudahkan siapa pun untuk membuat konten Shorts tanpa perlu skill editing video.
              </Text>
            </LiftCard>
          </FadeInView>

          <FadeInView delay={120}>
            <Text style={{ fontWeight: '700', color: colors.text, marginBottom: 10, fontSize: 15 }}>Dibangun Dengan</Text>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 20 }}>
              {stack.map((s, i) => (
                <View key={i} style={{
                  flexDirection: 'row', alignItems: 'center', gap: 6,
                  paddingVertical: 8, paddingHorizontal: 12, borderRadius: 10,
                  backgroundColor: isDark ? '#121214' : '#fff', borderWidth: 1, borderColor: colors.border,
                }}>
                  <Ionicons name={s.icon} size={14} color={colors.primary} />
                  <Text style={{ color: colors.text, fontSize: 12, fontWeight: '600' }}>{s.name}</Text>
                </View>
              ))}
            </View>
          </FadeInView>

          <Text style={{ textAlign: 'center', color: colors.muted, fontSize: 12, marginTop: 8, marginBottom: 24 }}>
            &copy; 2026 AutoClipper. All rights reserved.
          </Text>
        </PageContainer>
      </ScrollView>
    </View>
  );
}
