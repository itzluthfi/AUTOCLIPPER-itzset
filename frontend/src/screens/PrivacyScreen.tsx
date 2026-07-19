import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';

export default function PrivacyScreen() {
  const { colors } = useTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Kebijakan Privasi" />
      <ScrollView style={{ flex: 1, padding: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 16 }}>Kebijakan Privasi</Text>
        <Text style={{ color: colors.text, lineHeight: 22, marginBottom: 12 }}>
          AutoClipper menghormati privasi Anda. Kebijakan ini menjelaskan bagaimana kami mengumpulkan, menggunakan, dan melindungi informasi pribadi Anda.
        </Text>
        <Section title="Informasi yang Kami Kumpulkan" text="Kami mengumpulkan informasi yang Anda berikan saat mendaftar: nama, email, dan data akun Google/YouTube. Kami juga mengumpulkan data penggunaan layanan seperti URL video yang diproses." colors={colors} />
        <Section title="Penggunaan Informasi" text="Informasi digunakan untuk: memproses video, mengelola akun, meningkatkan layanan, dan komunikasi terkait layanan." colors={colors} />
        <Section title="Penyimpanan Video" text="Video yang diunduh hanya disimpan sementara selama proses. Hasil klip disimpan selama 7 hari setelah itu dihapus otomatis." colors={colors} />
        <Section title="Keamanan Data" text="Kami menggunakan enkripsi SSL untuk semua komunikasi data. API Key dan token autentikasi disimpan dengan aman." colors={colors} />
        <Section title="Hak Anda" text="Anda dapat meminta penghapusan data kapan saja dengan menghubungi kami." colors={colors} />
        <Text style={{ color: colors.muted, fontSize: 12, marginTop: 16 }}>Terakhir diperbarui: Juli 2026</Text>
      </ScrollView>
    </View>
  );
}

function Section({ title, text, colors }: any) {
  return (
    <View style={{ marginBottom: 12 }}>
      <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 4, fontSize: 15 }}>{title}</Text>
      <Text style={{ color: colors.muted, lineHeight: 20, fontSize: 14 }}>{text}</Text>
    </View>
  );
}
