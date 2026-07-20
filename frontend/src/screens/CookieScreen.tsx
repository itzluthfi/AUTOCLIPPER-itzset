import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { PageContainer } from '../components/PageContainer';
import { InfoPageHeader } from '../components/InfoPageHeader';
import { LiftCard } from '../components/LiftCard';
import { FadeInView } from '../components/FadeInView';

const cookieTypes = [
  { name: 'Cookie Sesi', desc: 'Menyimpan sesi login selama Anda menggunakan aplikasi' },
  { name: 'Cookie Preferensi', desc: 'Menyimpan preferensi tema dan pengaturan' },
  { name: 'Cookie Analitik', desc: 'Membantu kami memahami penggunaan aplikasi' },
];

export default function CookieScreen() {
  const { colors } = useTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Kebijakan Cookie" />
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <PageContainer maxWidth={720}>
          <FadeInView>
            <InfoPageHeader icon="file-tray-full-outline" title="Kebijakan Cookie" subtitle="AutoClipper menggunakan cookie untuk meningkatkan pengalaman pengguna." />
          </FadeInView>

          <FadeInView delay={40}>
            <Text style={{ fontWeight: '700', color: colors.text, marginBottom: 8, fontSize: 15 }}>Cookie yang Kami Gunakan</Text>
          </FadeInView>
          {cookieTypes.map((c, i) => (
            <FadeInView key={i} delay={60 + i * 40}>
              <LiftCard style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 8 }}>
                <Text style={{ fontWeight: '700', color: colors.text, marginBottom: 4, fontSize: 14 }}>{c.name}</Text>
                <Text style={{ color: colors.muted, fontSize: 13, lineHeight: 19 }}>{c.desc}</Text>
              </LiftCard>
            </FadeInView>
          ))}

          <FadeInView delay={220}>
            <LiftCard style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginTop: 8, marginBottom: 8 }}>
              <Text style={{ fontWeight: '700', color: colors.text, marginBottom: 4, fontSize: 15 }}>Kontrol Cookie</Text>
              <Text style={{ color: colors.muted, lineHeight: 20, fontSize: 14 }}>
                Anda dapat mengontrol cookie melalui pengaturan browser. Menonaktifkan cookie dapat memengaruhi fungsionalitas aplikasi.
              </Text>
            </LiftCard>
          </FadeInView>

          <Text style={{ color: colors.muted, fontSize: 12, marginTop: 8, marginBottom: 24, textAlign: 'center' }}>Terakhir diperbarui: Juli 2026</Text>
        </PageContainer>
      </ScrollView>
    </View>
  );
}
