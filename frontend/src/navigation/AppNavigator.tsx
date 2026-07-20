import React, { useEffect } from 'react';
import { NavigationContainer, getFocusedRouteNameFromRoute } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getVideo } from '../services/api';
import { toast } from '../components/Toast';

import HomeScreen from '../screens/HomeScreen';
import LoginScreen from '../screens/LoginScreen';
import DashboardScreen from '../screens/DashboardScreen';
import CreateClipScreen from '../screens/CreateClipScreen';
import HistoryScreen from '../screens/HistoryScreen';
import ProfileScreen from '../screens/ProfileScreen';
import ProcessingScreen from '../screens/ProcessingScreen';
import ResultsScreen from '../screens/ResultsScreen';
import EditClipScreen from '../screens/EditClipScreen';
import AdminScreen from '../screens/AdminScreen';
import FAQScreen from '../screens/FAQScreen';
import PrivacyScreen from '../screens/PrivacyScreen';
import CookieScreen from '../screens/CookieScreen';
import TermsScreen from '../screens/TermsScreen';
import AboutScreen from '../screens/AboutScreen';
import CheckoutScreen from '../screens/CheckoutScreen';
import { useTheme } from '../theme/ThemeContext';
import { TabLayout } from './TabLayout';

// Catatan: pakai native-stack, bukan @react-navigation/stack.
// CardSheet milik stack versi JS tidak membatasi tinggi konten di web,
// sehingga ScrollView ikut melar dan halaman tidak pernah bisa di-scroll.
const Stack = createNativeStackNavigator();
const Tabs = createNativeStackNavigator();

export function AppNavigator() {
  const { colors } = useTheme();

  useEffect(() => {
    const pollInterval = setInterval(async () => {
      try {
        const apiKey = await AsyncStorage.getItem('api_key');
        if (!apiKey) return;

        const activeJobsStr = await AsyncStorage.getItem('active_jobs');
        if (!activeJobsStr) return;

        let activeJobs: number[] = JSON.parse(activeJobsStr);
        if (activeJobs.length === 0) return;

        const updatedJobs: number[] = [...activeJobs];

        for (const videoId of activeJobs) {
          let video: any = null;
          try {
            video = await getVideo(videoId);
          } catch (fetchErr: any) {
            // 404 / video tidak ada di DB → hapus dari active_jobs agar berhenti poll
            const status = fetchErr?.status ?? fetchErr?.response?.status;
            if (!status || status === 404 || status >= 400) {
              console.warn(`[Poll] Video #${videoId} tidak ditemukan (${status}), dihapus dari active_jobs.`);
              const index = updatedJobs.indexOf(videoId);
              if (index > -1) updatedJobs.splice(index, 1);
            }
            continue;
          }

          if (!video) {
            // Hapus juga jika response kosong / null
            const index = updatedJobs.indexOf(videoId);
            if (index > -1) updatedJobs.splice(index, 1);
            continue;
          }

          if (video.status === 'completed') {
            toast.success('Pemrosesan Selesai 🎉', `Video "${video.title || 'Video YouTube'}" telah selesai diproses.`);
            const index = updatedJobs.indexOf(videoId);
            if (index > -1) updatedJobs.splice(index, 1);
          } else if (video.status === 'failed') {
            toast.error('Gagal Memproses Video ❌', video.error_message || 'Terjadi kesalahan saat pemrosesan.');
            const index = updatedJobs.indexOf(videoId);
            if (index > -1) updatedJobs.splice(index, 1);
          }
        }

        await AsyncStorage.setItem('active_jobs', JSON.stringify(updatedJobs));
      } catch (e) {
        console.error('Background polling error:', e);
      }
    }, 7000);

    return () => clearInterval(pollInterval);
  }, []);

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: colors.background },
        }}
      >
        {/* Main Tabs (Dashboard, CreateClip, History, Profile) */}
        <Stack.Screen name="MainTabs" options={{ headerShown: false }}>
          {({ navigation, route }) => {
            const activeTab = getFocusedRouteNameFromRoute(route) ?? 'Dashboard';
            return (
              <TabLayout routeName={activeTab} navigation={navigation}>
                <Tabs.Navigator
                  screenOptions={{
                    headerShown: false,
                    contentStyle: { backgroundColor: colors.background },
                    animation: 'fade',
                  }}
                >
                  <Tabs.Screen name="Dashboard" component={DashboardScreen} />
                  <Tabs.Screen name="CreateClip" component={CreateClipScreen} />
                  <Tabs.Screen name="History" component={HistoryScreen} />
                  <Tabs.Screen name="Profile" component={ProfileScreen} />
                </Tabs.Navigator>
              </TabLayout>
            );
          }}
        </Stack.Screen>

        {/* Other screens (no bottom tabs) */}
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Processing" component={ProcessingScreen} />
        <Stack.Screen name="Results" component={ResultsScreen} />
        <Stack.Screen name="EditClip" component={EditClipScreen} />
        <Stack.Screen name="Checkout" component={CheckoutScreen} />
        <Stack.Screen name="Admin" component={AdminScreen} />
        <Stack.Screen name="FAQ" component={FAQScreen} />
        <Stack.Screen name="Privacy" component={PrivacyScreen} />
        <Stack.Screen name="Cookie" component={CookieScreen} />
        <Stack.Screen name="Terms" component={TermsScreen} />
        <Stack.Screen name="About" component={AboutScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
