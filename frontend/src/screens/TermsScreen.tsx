import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';

export default function TermsScreen() {
  const { colors } = useTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Syarat & Ketentuan" />
      <ScrollView style={{ flex: 1, padding: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 16 }}>Syarat & Ketentuan</Text>
        {[
          { title: 'Penggunaan Layanan', text: 'Dengan menggunakan AutoClipper, Anda menyetujui syarat dan ketentuan ini. Layanan ini hanya untuk tujuan hukum dan tidak boleh digunakan untuk melanggar hak cipta.' },
          { title: 'Hak Kekayaan Intelektual', text: 'Anda bertanggung jawab penuh atas video yang Anda proses. AutoClipper hanya menyediakan alat pemrosesan.' },
          { title: 'Batasan Tanggung Jawab', text: 'AutoClipper tidak bertanggung jawab atas kerugian yang timbul dari penggunaan layanan ini. Layanan disediakan "sebagaimana adanya".' },
          { title: 'Akun Pengguna', text: 'Anda bertanggung jawab menjaga kerahasiaan API Key dan aktivitas akun Anda. Beritahu kami jika ada akses tidak sah.' },
          { title: 'Pembatasan Layanan', text: 'Kami berhak membatasi atau menghentikan akses jika melanggar ketentuan atau menyalahgunakan layanan.' },
          { title: 'Perubahan Ketentuan', text: 'Kami dapat memperbarui ketentuan ini sewaktu-waktu. Penggunaan lanjutan berarti menyetujui perubahan.' },
        ].map((s, i) => (
          <View key={i} style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 8 }}>
            <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 4, fontSize: 15 }}>{s.title}</Text>
            <Text style={{ color: colors.muted, lineHeight: 20, fontSize: 14 }}>{s.text}</Text>
          </View>
        ))}
        <Text style={{ color: colors.muted, fontSize: 12, marginTop: 16, marginBottom: 24 }}>Terakhir diperbarui: Juli 2026</Text>
      </ScrollView>
    </View>
  );
}
