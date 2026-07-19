import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Linking, ActivityIndicator, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { createCheckout } from '../services/api';

const packages = [
  { credits: 10, price: 50000, label: 'Paket Pemula', desc: 'Cocok untuk mencoba fitur AI Auto-Clip' },
  { credits: 30, price: 120000, label: 'Paket Kreator', desc: 'Pilihan terbaik untuk kreator konten aktif' },
  { credits: 100, price: 350000, label: 'Paket Profesional', desc: 'Sangat hemat untuk agensi & tim editor' },
];

export default function CheckoutScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [loadingPkg, setLoadingPkg] = useState<number | null>(null);

  const handleBuy = async (credits: number, price: number) => {
    setLoadingPkg(credits);
    try {
      const res = await createCheckout(credits, price);
      if (res.redirect_url) {
        if (Platform.OS === 'web') {
          window.open(res.redirect_url, '_blank');
        } else {
          await Linking.openURL(res.redirect_url);
        }
        alert('Menuju gerbang pembayaran Midtrans. Silakan selesaikan pembayaran Anda.');
      } else {
        alert('Gagal membuat transaksi pembayaran.');
      }
    } catch (e: any) {
      alert(e.message || 'Terjadi kesalahan');
    } finally {
      setLoadingPkg(null);
    }
  };

  const formatPrice = (price: number) => {
    return 'Rp ' + price.toLocaleString('id-ID');
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Beli Kredit AI" />
      <ScrollView style={{ flex: 1, padding: 20 }} contentContainerStyle={{ paddingBottom: 50 }}>
        
        <View style={{ alignItems: 'center', marginBottom: 24 }}>
          <View style={{
            width: 60, height: 60, borderRadius: 30,
            backgroundColor: colors.primary + '20',
            alignItems: 'center', justifyContent: 'center', marginBottom: 12,
          }}>
            <Ionicons name="flash" size={32} color={colors.primary} />
          </View>
          <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text, textAlign: 'center' }}>
            Isi Ulang Kredit AutoClipper
          </Text>
          <Text style={{ fontSize: 13, color: colors.muted, textAlign: 'center', marginTop: 4, paddingHorizontal: 10 }}>
            Kredit digunakan untuk memproses highlight video YouTube menggunakan kecerdasan buatan (AI)
          </Text>
        </View>

        {packages.map((pkg) => {
          const isProcessing = loadingPkg === pkg.credits;
          return (
            <View key={pkg.credits} style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
              <View style={{ flex: 1, marginRight: 10 }}>
                <Text style={{ fontSize: 16, fontWeight: '700', color: colors.text }}>{pkg.label}</Text>
                <Text style={{ fontSize: 12, color: colors.muted, marginTop: 2, marginBottom: 8 }}>{pkg.desc}</Text>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                  <Ionicons name="flash" size={16} color={colors.primary} style={{ marginRight: 4 }} />
                  <Text style={{ fontSize: 14, fontWeight: '600', color: colors.text }}>
                    {pkg.credits} Kredit AI
                  </Text>
                </View>
              </View>

              <View style={{ alignItems: 'flex-end' }}>
                <Text style={{ fontSize: 16, fontWeight: '700', color: colors.primary, marginBottom: 8 }}>
                  {formatPrice(pkg.price)}
                </Text>
                <TouchableOpacity
                  onPress={() => handleBuy(pkg.credits, pkg.price)}
                  disabled={loadingPkg !== null}
                  style={{
                    backgroundColor: colors.primary,
                    paddingHorizontal: 16, paddingVertical: 8, borderRadius: 8,
                    minWidth: 80, alignItems: 'center', justifyContent: 'center',
                  }}
                >
                  {isProcessing ? (
                    <ActivityIndicator size="small" color="#fff" />
                  ) : (
                    <Text style={{ color: '#fff', fontWeight: '600', fontSize: 13 }}>Beli</Text>
                  )}
                </TouchableOpacity>
              </View>
            </View>
          );
        })}

        <View style={{
          padding: 16, borderRadius: 12, backgroundColor: isDark ? '#1a1a1a' : '#f8fafc',
          borderWidth: 1, borderColor: colors.border, marginTop: 16, flexDirection: 'row', gap: 10
        }}>
          <Ionicons name="information-circle-outline" size={20} color={colors.muted} />
          <Text style={{ flex: 1, fontSize: 12, color: colors.muted, lineHeight: 18 }}>
            Pembayaran diproses secara instan dan aman oleh **Midtrans**. Setelah pembayaran berhasil dilakukan, kredit Anda akan langsung ditambahkan secara otomatis dalam beberapa detik.
          </Text>
        </View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 16,
    borderRadius: 14,
    borderWidth: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
});
