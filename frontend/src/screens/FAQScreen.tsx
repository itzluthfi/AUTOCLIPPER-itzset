import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';

const faqData = [
  { q: 'Apa itu AutoClipper?', a: 'AutoClipper adalah platform AI yang mengubah video YouTube panjang menjadi video short (9:16) secara otomatis.' },
  { q: 'Apakah gratis?', a: 'Ya, mode Heuristic gratis dan unlimited. Mode AI menggunakan kredit (1x gratis, selanjutnya beli kredit).' },
  { q: 'Berapa lama proses?', a: 'Rata-rata 1-5 menit tergantung durasi video dan mode yang dipilih.' },
  { q: 'Format video apa yang dihasilkan?', a: 'Video MP4 H.264, resolusi 1080x1920 (9:16 portrait), maksimal 60 detik per klip.' },
  { q: 'Bisa upload langsung ke YouTube?', a: 'Ya, dengan 1 klik. Anda perlu login dengan akun YouTube Anda.' },
  { q: 'Apakah video saya aman?', a: 'Video hanya diproses di server kami. Kami tidak menyimpan video setelah diproses.' },
  { q: 'Tracking wajah bagaimana cara kerjanya?', a: 'Menggunakan OpenCV dan MediaPipe untuk mendeteksi dan mengikuti wajah secara real-time.' },
  { q: 'Bisakah saya menggunakan API?', a: 'Ya, AutoClipper menyediakan API untuk integrasi. Hubungi kami untuk akses.' },
];

export default function FAQScreen() {
  const { colors } = useTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="FAQ" />
      <ScrollView style={{ flex: 1, padding: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 16 }}>
          Pertanyaan Umum
        </Text>
        {faqData.map((item, i) => (
          <View key={i} style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 8 }}>
            <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 4 }}>{item.q}</Text>
            <Text style={{ color: colors.muted, fontSize: 14, lineHeight: 20 }}>{item.a}</Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}
