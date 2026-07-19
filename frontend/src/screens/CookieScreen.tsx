import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';

export default function CookieScreen() {
  const { colors } = useTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Kebijakan Cookie" />
      <ScrollView style={{ flex: 1, padding: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 16 }}>Kebijakan Cookie</Text>
        <Text style={{ color: colors.text, lineHeight: 22, marginBottom: 16 }}>
          AutoClipper menggunakan cookie untuk meningkatkan pengalaman pengguna. Cookie adalah file kecil yang disimpan di perangkat Anda.
        </Text>
        <Section title="Cookie yang Kami Gunakan" colors={colors}>
          {[
            { name: 'Cookie Sesi', desc: 'Menyimpan sesi login selama Anda menggunakan aplikasi' },
            { name: 'Cookie Preferensi', desc: 'Menyimpan preferensi tema dan pengaturan' },
            { name: 'Cookie Analitik', desc: 'Membantu kami memahami penggunaan aplikasi' },
          ]}
        </Section>
        <Section title="Kontrol Cookie" colors={colors}>
          <Text style={{ color: colors.muted, lineHeight: 20, fontSize: 14 }}>
            Anda dapat mengontrol cookie melalui pengaturan browser. Menonaktifkan cookie dapat mempengaruhi fungsionalitas aplikasi.
          </Text>
        </Section>
        <Text style={{ color: colors.muted, fontSize: 12, marginTop: 16 }}>Terakhir diperbarui: Juli 2026</Text>
      </ScrollView>
    </View>
  );
}

function Section({ title, colors, children }: any) {
  return (
    <View style={{ marginBottom: 16 }}>
      <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 15 }}>{title}</Text>
      {children}
    </View>
  );
}
