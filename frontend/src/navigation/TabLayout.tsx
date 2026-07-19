import React from 'react';
import { View, Text, Pressable, useWindowDimensions, Platform } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { FloatingBottomTab } from '../components/FloatingBottomTab';
import { Ionicons } from '@expo/vector-icons';

const TAB_SCREENS = ['Dashboard', 'CreateClip', 'History', 'Profile'];

const TABS = [
  { key: 'Dashboard', label: 'Dashboard', icon: 'grid-outline', activeIcon: 'grid' },
  { key: 'CreateClip', label: 'Buat Klip', icon: 'add-circle-outline', activeIcon: 'add-circle' },
  { key: 'History', label: 'Riwayat', icon: 'time-outline', activeIcon: 'time' },
  { key: 'Profile', label: 'Profil', icon: 'person-outline', activeIcon: 'person' },
];

interface Props {
  children: React.ReactNode;
  routeName: string;
  navigation: any;
}

const webTransition = Platform.OS === 'web'
  ? ({ transitionProperty: 'background-color, transform', transitionDuration: '150ms' } as any)
  : {};

export function TabLayout({ children, routeName, navigation }: Props) {
  const { colors, isDark } = useTheme();
  const { width } = useWindowDimensions();
  const isDesktop = width >= 768;
  const showTab = TAB_SCREENS.includes(routeName);

  const goTab = (key: string) => navigation.navigate('MainTabs', { screen: key });

  return (
    <View style={{
      flex: 1,
      backgroundColor: colors.background,
      flexDirection: isDesktop && showTab ? 'row' : 'column'
    }}>
      {/* Sidebar untuk desktop */}
      {isDesktop && showTab && (
        <View style={{
          width: 240,
          borderRightWidth: 1,
          borderRightColor: colors.border,
          backgroundColor: colors.card,
          padding: 20,
          justifyContent: 'space-between',
        }}>
          <View>
            {/* Logo / Brand */}
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 28, gap: 10 }}>
              <View style={{
                width: 36, height: 36, borderRadius: 10,
                backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center'
              }}>
                <Ionicons name="film" size={20} color="#fff" />
              </View>
              <Text style={{ fontSize: 18, fontWeight: '700', color: colors.text }}>AutoClipper</Text>
            </View>

            <Text style={{
              fontSize: 11, fontWeight: '600', color: colors.muted,
              letterSpacing: 1, textTransform: 'uppercase', marginBottom: 8, marginLeft: 12,
            }}>
              Menu
            </Text>

            {/* Menu Items */}
            <View style={{ gap: 4 }}>
              {TABS.map((tab) => {
                const isActive = routeName === tab.key;
                return (
                  <Pressable
                    key={tab.key}
                    onPress={() => goTab(tab.key)}
                    style={({ hovered }: any) => ({
                      flexDirection: 'row',
                      alignItems: 'center',
                      paddingHorizontal: 12,
                      paddingVertical: 10,
                      borderRadius: 10,
                      backgroundColor: isActive
                        ? colors.primary + '18'
                        : hovered
                          ? (isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)')
                          : 'transparent',
                      gap: 12,
                      ...webTransition,
                    })}
                  >
                    {/* Aksen kiri untuk item aktif */}
                    <View style={{
                      position: 'absolute', left: 0, top: 9, bottom: 9, width: 3,
                      borderRadius: 2,
                      backgroundColor: isActive ? colors.primary : 'transparent',
                    }} />
                    <Ionicons
                      name={isActive ? (tab.activeIcon as any) : (tab.icon as any)}
                      size={20}
                      color={isActive ? colors.primary : colors.muted}
                    />
                    <Text style={{
                      fontSize: 14,
                      color: isActive ? colors.primary : colors.text,
                      fontWeight: isActive ? '600' : '500',
                    }}>
                      {tab.label}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          </View>

          {/* Footer Info */}
          <Text style={{ color: colors.muted, fontSize: 11, textAlign: 'center' }}>
            AutoClipper v1.0.0
          </Text>
        </View>
      )}

      {/* Konten utama — beri ruang bawah di mobile agar tidak tertutup floating tab */}
      <View style={{ flex: 1, paddingBottom: showTab && !isDesktop ? 84 : 0 }}>
        {children}
      </View>

      {/* Floating Bottom Tab untuk mobile */}
      {showTab && !isDesktop && (
        <FloatingBottomTab
          activeTab={routeName}
          onTabPress={goTab}
        />
      )}
    </View>
  );
}
