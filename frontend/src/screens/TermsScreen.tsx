import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { PageContainer } from '../components/PageContainer';
import { InfoPageHeader } from '../components/InfoPageHeader';
import { LiftCard } from '../components/LiftCard';
import { FadeInView } from '../components/FadeInView';

const sections = [
  { title: 'Penggunaan Layanan', text: 'Dengan menggunakan AutoClipper, Anda menyetujui syarat dan ketentuan ini. Layanan ini hanya untuk tujuan hukum dan tidak boleh digunakan untuk melanggar hak cipta.' },
  { title: 'Hak Kekayaan Intelektual', text: 'Anda bertanggung jawab penuh atas video yang Anda proses. AutoClipper hanya menyediakan alat pemrosesan.' },
  { title: 'Batasan Tanggung Jawab', text: 'AutoClipper tidak bertanggung jawab atas kerugian yang timbul dari penggunaan layanan ini. Layanan disediakan "sebagaimana adanya".' },
  { title: 'Akun Pengguna', text: 'Anda bertanggung jawab menjaga kerahasiaan API Key dan aktivitas akun Anda. Beritahu kami jika ada akses tidak sah.' },
  { title: 'Pembatasan Layanan', text: 'Kami berhak membatasi atau menghentikan akses jika melanggar ketentuan atau menyalahgunakan layanan.' },
  { title: 'Perubahan Ketentuan', text: 'Kami dapat memperbarui ketentuan ini sewaktu-waktu. Penggunaan lanjutan berarti menyetujui perubahan.' },
];

export default function TermsScreen() {
  const { colors } = useTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Syarat & Ketentuan" />
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <PageContainer maxWidth={720}>
          <FadeInView>
            <InfoPageHeader icon="document-text-outline" title="Syarat & Ketentuan" subtitle="Ketentuan penggunaan layanan AutoClipper." />
          </FadeInView>
          {sections.map((s, i) => (
            <FadeInView key={i} delay={i * 40}>
              <LiftCard style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 8 }}>
                <Text style={{ fontWeight: '700', color: colors.text, marginBottom: 4, fontSize: 15 }}>{s.title}</Text>
                <Text style={{ color: colors.muted, lineHeight: 20, fontSize: 14 }}>{s.text}</Text>
              </LiftCard>
            </FadeInView>
          ))}
          <Text style={{ color: colors.muted, fontSize: 12, marginTop: 16, marginBottom: 24, textAlign: 'center' }}>Terakhir diperbarui: Juli 2026</Text>
        </PageContainer>
      </ScrollView>
    </View>
  );
}
