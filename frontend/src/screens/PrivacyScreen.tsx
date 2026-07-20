import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { PageContainer } from '../components/PageContainer';
import { InfoPageHeader } from '../components/InfoPageHeader';
import { LiftCard } from '../components/LiftCard';
import { FadeInView } from '../components/FadeInView';

const sections = [
  { title: 'Informasi yang Kami Kumpulkan', text: 'Kami mengumpulkan informasi yang Anda berikan saat mendaftar: nama, email, dan data akun Google/YouTube. Kami juga mengumpulkan data penggunaan layanan seperti URL video yang diproses.' },
  { title: 'Penggunaan Informasi', text: 'Informasi digunakan untuk: memproses video, mengelola akun, meningkatkan layanan, dan komunikasi terkait layanan.' },
  { title: 'Penyimpanan Video', text: 'Video sumber yang diunduh hanya disimpan sementara selama proses berlangsung dan otomatis dihapus setelah klip selesai dibuat.' },
  { title: 'Keamanan Data', text: 'Kami menggunakan enkripsi SSL untuk semua komunikasi data. Password di-hash dengan bcrypt dan API Key disimpan dalam bentuk hash, bukan teks polos.' },
  { title: 'Hak Anda', text: 'Anda dapat meminta penghapusan data kapan saja dengan menghubungi kami.' },
];

export default function PrivacyScreen() {
  const { colors } = useTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Kebijakan Privasi" />
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <PageContainer maxWidth={720}>
          <FadeInView>
            <InfoPageHeader icon="shield-checkmark-outline" title="Kebijakan Privasi" subtitle="Bagaimana kami mengumpulkan, menggunakan, dan melindungi informasi pribadi Anda." />
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
