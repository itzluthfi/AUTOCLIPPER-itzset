import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, Linking, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { PageContainer } from '../components/PageContainer';
import { LiftCard } from '../components/LiftCard';
import { Button } from '../components/Button';
import { FadeInView } from '../components/FadeInView';
import { createCheckout, getPublicSettings, CreditPackage } from '../services/api';
import { toast } from '../components/Toast';

// Fallback jika endpoint settings belum bisa dijangkau — harga final tetap divalidasi server
const defaultPackages: CreditPackage[] = [
  { id: 'starter', credits: 10, amount: 50000, label: 'Paket Pemula', desc: 'Cocok untuk mencoba fitur AI Auto-Clip' },
  { id: 'creator', credits: 30, amount: 120000, label: 'Paket Kreator', desc: 'Pilihan terbaik untuk kreator konten aktif' },
  { id: 'pro', credits: 100, amount: 350000, label: 'Paket Profesional', desc: 'Sangat hemat untuk agensi & tim editor' },
];

export default function CheckoutScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [packages, setPackages] = useState<CreditPackage[]>(defaultPackages);
  const [loadingPkg, setLoadingPkg] = useState<string | null>(null);

  useEffect(() => {
    getPublicSettings()
      .then((s) => { if (s.packages?.length) setPackages(s.packages); })
      .catch(() => {});
  }, []);

  const handleBuy = async (packageId: string) => {
    setLoadingPkg(packageId);
    try {
      const res = await createCheckout(packageId);
      if (res.redirect_url) {
        if (Platform.OS === 'web') {
          window.open(res.redirect_url, '_blank');
        } else {
          await Linking.openURL(res.redirect_url);
        }
        toast.info('Menuju Pembayaran 💳', 'Membuka gerbang pembayaran Midtrans...');
      } else {
        toast.error('Gagal Transaksi ❌', 'Gagal membuat transaksi pembayaran.');
      }
    } catch (e: any) {
      toast.error('Terjadi Kesalahan ❌', e.message || 'Gagal memproses pembayaran');
    } finally {
      setLoadingPkg(null);
    }
  };

  const formatPrice = (price: number) => 'Rp ' + price.toLocaleString('id-ID');

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header showBack title="Beli Kredit AI" />
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 50 }}>
        <PageContainer maxWidth={640}>

          <FadeInView>
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
          </FadeInView>

          {packages.map((pkg, i) => {
            const isProcessing = loadingPkg === pkg.id;
            return (
              <FadeInView key={pkg.id} delay={i * 60}>
                <LiftCard style={{
                  padding: 16, borderRadius: 14, borderWidth: 1,
                  backgroundColor: colors.card, borderColor: colors.border,
                  flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
                  marginBottom: 12,
                }}>
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
                      {formatPrice(pkg.amount)}
                    </Text>
                    <Button
                      label="Beli"
                      size="md"
                      loading={isProcessing}
                      disabled={loadingPkg !== null}
                      onPress={() => handleBuy(pkg.id)}
                    />
                  </View>
                </LiftCard>
              </FadeInView>
            );
          })}

          <View style={{
            padding: 16, borderRadius: 12, backgroundColor: isDark ? '#1a1a1a' : '#f8fafc',
            borderWidth: 1, borderColor: colors.border, marginTop: 16, flexDirection: 'row', gap: 10
          }}>
            <Ionicons name="information-circle-outline" size={20} color={colors.muted} />
            <Text style={{ flex: 1, fontSize: 12, color: colors.muted, lineHeight: 18 }}>
              Pembayaran diproses secara instan dan aman oleh <Text style={{ fontWeight: '700' }}>Midtrans</Text>. Setelah pembayaran berhasil dilakukan, kredit Anda akan langsung ditambahkan secara otomatis dalam beberapa detik.
            </Text>
          </View>

        </PageContainer>
      </ScrollView>
    </View>
  );
}
