import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '../theme/ThemeContext';
import { Header } from '../components/Header';
import { API_BASE } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

const features = [
  { title: 'AI Auto-Detect', desc: 'Deteksi momen penting dari video secara otomatis pake AI atau heuristik' },
  { title: 'Face Tracking', desc: 'Tracking wajah otomatis untuk portrait 9:16' },
  { title: 'Auto Subtitle', desc: 'Subtitle otomatis pake Whisper AI' },
  { title: 'YouTube Upload', desc: 'Upload langsung ke YouTube dengan 1 klik' },
  { title: 'Multi Format', desc: 'Dukung semua jenis video: musik, podcast, olahraga, gaming' },
  { title: 'AI Optimization', desc: 'Optimasi judul, deskripsi, dan tag untuk performa Shorts' },
];

export default function HomeScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [featuredClips, setFeaturedClips] = useState<any[]>([]);
  const [playingClipId, setPlayingClipId] = useState<number | null>(null);

  useEffect(() => {
    // If user is already logged in, navigate to Dashboard directly
    const checkLoginStatus = async () => {
      if (Platform.OS === 'web') {
        const params = new URLSearchParams(window.location.search);
        const urlKey = params.get('api_key');
        if (urlKey) {
          await AsyncStorage.setItem('api_key', urlKey);
          navigation.replace('MainTabs');
          return;
        }
      }
      const token = await AsyncStorage.getItem('api_key');
      if (token) {
        navigation.replace('MainTabs');
      }
    };
    checkLoginStatus();
    
    // Fetch featured clips for showcase
    fetch(`${API_BASE}/clips/public/featured`)
      .then(r => r.json())
      .then(data => setFeaturedClips(data || []))
      .catch(() => {});
  }, []);

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <Header />

      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {/* Hero */}
        <View style={{
          padding: 24,
          borderRadius: 16,
          backgroundColor: colors.card,
          borderWidth: 1,
          borderColor: colors.border,
          marginBottom: 24,
        }}>
          <Text style={{ fontSize: 28, fontWeight: '700', color: colors.text, marginBottom: 8 }}>
            Ubah Video YouTube Jadi Shorts
          </Text>
          <Text style={{ fontSize: 15, color: colors.muted, lineHeight: 22, marginBottom: 20 }}>
            AutoClipper adalah platform AI yang mengubah video YouTube panjang menjadi 
            video short (9:16) secara otomatis. Cukup paste link, biarkan AI yang 
            memilih momen terbaik, lalu upload ke YouTube dengan 1 klik.
          </Text>

          <TouchableOpacity
            onPress={() => {
              console.log('Mulai Sekarang pressed');
              if (Platform.OS === 'web') {
                // Try native navigation first
                try {
                  navigation.navigate('Login');
                  console.log('Navigation called');
                } catch(e) {
                  console.error('Navigation error:', e);
                  window.location.href = '/Login';
                }
                return;
              }
              navigation.navigate('Login');
            }}
            style={{
              backgroundColor: colors.primary,
              paddingVertical: 14,
              paddingHorizontal: 24,
              borderRadius: 12,
              alignItems: 'center',
            }}
          >
            <Text style={{ color: '#fff', fontSize: 16, fontWeight: '600' }}>
              Mulai Sekarang
            </Text>
          </TouchableOpacity>
        </View>

        {/* How it works */}
        <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 12 }}>
          Cara Kerja
        </Text>

        {[
          { step: '1', title: 'Paste Link', desc: 'Masukkan URL YouTube yang ingin diklip' },
          { step: '2', title: 'AI Mendeteksi', desc: 'AI otomatis pilih momen paling menarik' },
          { step: '3', title: 'Auto-Clip', desc: 'Video diklip, di-tracking, dan diresize ke 9:16' },
          { step: '4', title: 'Upload', desc: 'Preview, edit, lalu upload ke YouTube dengan 1 klik' },
        ].map((item, i) => (
          <View key={i} style={{
            flexDirection: 'row',
            padding: 16,
            borderRadius: 12,
            backgroundColor: colors.card,
            borderWidth: 1,
            borderColor: colors.border,
            marginBottom: 8,
          }}>
            <View style={{
              width: 36,
              height: 36,
              borderRadius: 18,
              backgroundColor: colors.primary,
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: 12,
            }}>
              <Text style={{ color: '#fff', fontWeight: '700', fontSize: 16 }}>{item.step}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 2 }}>{item.title}</Text>
              <Text style={{ color: colors.muted, fontSize: 13 }}>{item.desc}</Text>
            </View>
          </View>
        ))}

        {/* Features */}
        <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text, marginTop: 24, marginBottom: 12 }}>
          Fitur Unggulan
        </Text>

        <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -4 }}>
          {features.map((f, i) => (
            <View key={i} style={{
              width: '50%',
              paddingHorizontal: 4,
              marginBottom: 8,
            }}>
              <View style={{
                padding: 12,
                borderRadius: 12,
                backgroundColor: colors.card,
                borderWidth: 1,
                borderColor: colors.border,
                minHeight: 100,
              }}>
                <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 4, fontSize: 13 }}>{f.title}</Text>
                <Text style={{ color: colors.muted, fontSize: 12, lineHeight: 17 }}>{f.desc}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Featured Showcase Clips (Admin Chosen) */}
        {featuredClips.length > 0 && (
          <View style={{ marginTop: 32 }}>
            <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 4 }}>
              🔥 Contoh Klip Buatan AI
            </Text>
            <Text style={{ color: colors.muted, marginBottom: 16, fontSize: 14 }}>
              Klip pilihan admin yang di-generate menggunakan AutoClipper
            </Text>
            <View style={{ gap: 10 }}>
              {featuredClips.map((clip) => (
                <View key={clip.id} style={{
                  padding: 16, borderRadius: 12, backgroundColor: colors.card,
                  borderWidth: 1, borderColor: colors.border,
                  flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
                }}>
                  <View style={{ flex: 1, marginRight: 12 }}>
                    <Text style={{ fontWeight: '600', color: colors.text, fontSize: 14 }} numberOfLines={1}>
                      {clip.title}
                    </Text>
                    <Text style={{ color: colors.muted, fontSize: 12, marginTop: 2 }}>
                      Durasi: {Math.floor((clip.end - clip.start))} detik
                    </Text>
                  </View>
                  <TouchableOpacity
                    onPress={() => setPlayingClipId(clip.id)}
                    style={{
                      backgroundColor: colors.primary,
                      paddingHorizontal: 16, paddingVertical: 8, borderRadius: 8,
                    }}
                  >
                    <Text style={{ color: '#fff', fontSize: 13, fontWeight: '600' }}>Tonton</Text>
                  </TouchableOpacity>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Bottom nav links */}
        <View style={{
          flexDirection: 'row',
          justifyContent: 'center',
          flexWrap: 'wrap',
          gap: 8,
          marginTop: 32,
          marginBottom: 16,
        }}>
          {[
            { name: 'FAQ', screen: 'FAQ' },
            { name: 'Kebijakan Privasi', screen: 'Privacy' },
            { name: 'Cookie', screen: 'Cookie' },
            { name: 'Syarat & Ketentuan', screen: 'Terms' },
            { name: 'Tentang', screen: 'About' },
          ].map((link, i) => (
            <TouchableOpacity key={i} onPress={() => navigation.navigate(link.screen)}>
              <Text style={{ color: colors.primary, fontSize: 13, fontWeight: '500' }}>{link.name}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={{ textAlign: 'center', color: colors.muted, fontSize: 12, marginBottom: 20 }}>
          &copy; 2026 AutoClipper. All rights reserved.
        </Text>
      </ScrollView>

      {/* Video Player Modal Overlay */}
      {playingClipId !== null && (
        <View style={{
          position: 'absolute', top: 0, bottom: 0, left: 0, right: 0,
          backgroundColor: 'rgba(0,0,0,0.85)', justifyContent: 'center', alignItems: 'center',
          padding: 20, zIndex: 9999,
        }}>
          <View style={{
            width: '100%', maxWidth: 500, backgroundColor: colors.card,
            borderRadius: 16, padding: 16, borderWidth: 1, borderColor: colors.border,
          }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <Text style={{ fontWeight: '700', color: colors.text, fontSize: 16 }}>Contoh Klip Showcase</Text>
              <TouchableOpacity onPress={() => setPlayingClipId(null)} style={{ padding: 4 }}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>

            {Platform.OS === 'web' ? (
              <video
                src={`${API_BASE}/clips/${playingClipId}/file/public`}
                controls
                autoPlay
                style={{ width: '100%', borderRadius: 8, maxHeight: 400, backgroundColor: '#000' }}
              />
            ) : (
              <View style={{ height: 200, backgroundColor: '#000', borderRadius: 8, justifyContent: 'center', alignItems: 'center' }}>
                <Ionicons name="play-circle" size={48} color={colors.primary} />
                <Text style={{ color: '#fff', marginTop: 8, fontSize: 12 }}>Pemutar video diaktifkan di Web Browser</Text>
              </View>
            )}
          </View>
        </View>
      )}
    </View>
  );
}
