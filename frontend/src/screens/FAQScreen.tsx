import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { PageContainer } from '../components/PageContainer';
import { InfoPageHeader } from '../components/InfoPageHeader';
import { LiftCard } from '../components/LiftCard';
import { FadeInView } from '../components/FadeInView';

const faqData = [
  { q: 'Apa itu AutoClipper?', a: 'AutoClipper adalah platform AI yang mengubah video YouTube panjang menjadi video short (9:16) secara otomatis.' },
  { q: 'Apakah gratis?', a: 'Ya, mode Heuristik gratis dan unlimited. Mode AI Router menggunakan kredit — daftar akun baru langsung mendapat 5 kredit gratis.' },
  { q: 'Berapa lama proses?', a: 'Rata-rata 1-5 menit tergantung durasi video dan mode yang dipilih.' },
  { q: 'Format video apa yang dihasilkan?', a: 'Video MP4 H.264, resolusi 1080x1920 (9:16 portrait), maksimal 60 detik per klip.' },
  { q: 'Bisa upload langsung ke YouTube?', a: 'Ya, dengan 1 klik. Anda perlu menghubungkan akun YouTube Anda terlebih dahulu.' },
  { q: 'Apakah video saya aman?', a: 'Video sumber hanya disimpan sementara selama diproses di server kami dan otomatis dihapus setelah klip selesai dibuat.' },
  { q: 'Bagaimana cara kerja framing otomatis?', a: 'Mode Auto Mix menganalisis setiap klip dengan OpenCV untuk mendeteksi jumlah wajah dan pergerakan, lalu memilih framing terbaik: face track, split-screen, atau center crop.' },
  { q: 'Bisakah saya menggunakan API?', a: 'Ya, AutoClipper menyediakan API Key personal yang bisa dipakai untuk integrasi dengan aplikasi Anda sendiri.' },
];

export default function FAQScreen() {
  const { colors, isDark } = useTheme();
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="FAQ" />
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <PageContainer maxWidth={720}>
          <FadeInView>
            <InfoPageHeader icon="help-circle-outline" title="Pertanyaan Umum" subtitle="Semua yang perlu Anda ketahui sebelum mulai membuat klip." />
          </FadeInView>

          {faqData.map((item, i) => {
            const isOpen = openIndex === i;
            return (
              <FadeInView key={i} delay={i * 35}>
                <TouchableOpacity activeOpacity={0.7} onPress={() => setOpenIndex(isOpen ? null : i)}>
                  <LiftCard style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 8 }}>
                    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Text style={{ fontWeight: '600', color: colors.text, flex: 1, marginRight: 8 }}>{item.q}</Text>
                      <Ionicons name={isOpen ? 'chevron-up' : 'chevron-down'} size={18} color={colors.muted} />
                    </View>
                    {isOpen && (
                      <Text style={{ color: colors.muted, fontSize: 14, lineHeight: 20, marginTop: 8 }}>{item.a}</Text>
                    )}
                  </LiftCard>
                </TouchableOpacity>
              </FadeInView>
            );
          })}
        </PageContainer>
      </ScrollView>
    </View>
  );
}
