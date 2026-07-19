import React from 'react';
import { View, Text, TouchableOpacity, useWindowDimensions, Platform } from 'react-native';
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

export function TabLayout({ children, routeName, navigation }: Props) {
  const { colors, isDark } = useTheme();
  const { width } = useWindowDimensions();
  const isDesktop = Platform.OS === 'web' && width >= 768;
  const showTab = TAB_SCREENS.includes(routeName);

  return (
    <View style={{ 
      flex: 1, 
      backgroundColor: colors.background, 
      flexDirection: isDesktop && showTab ? 'row' : 'column' 
    }}>
      {/* Sidebar for Desktop */}
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
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 30, gap: 10 }}>
              <View style={{
                width: 36, height: 36, borderRadius: 10,
                backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center'
              }}>
                <Ionicons name="film" size={20} color="#fff" />
              </View>
              <Text style={{ fontSize: 18, fontWeight: '700', color: colors.text }}>AutoClipper</Text>
            </View>

            {/* Menu Items */}
            <View style={{ gap: 6 }}>
              {TABS.map((tab) => {
                const isActive = routeName === tab.key;
                return (
                  <TouchableOpacity
                    key={tab.key}
                    onPress={() => navigation.navigate(tab.key)}
                    style={{
                      flexDirection: 'row',
                      alignItems: 'center',
                      paddingHorizontal: 12,
                      paddingVertical: 10,
                      borderRadius: 10,
                      backgroundColor: isActive ? colors.primary + '15' : 'transparent',
                      gap: 12,
                    }}
                    activeOpacity={0.7}
                  >
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
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>

          {/* Footer Info */}
          <Text style={{ color: colors.muted, fontSize: 11, textAlign: 'center' }}>
            AutoClipper SaaS v1.0.0
          </Text>
        </View>
      )}

      {/* Main Screen Content */}
      <View style={{ flex: 1 }}>
        {children}
      </View>

      {/* Floating Bottom Tab for Mobile */}
      {showTab && !isDesktop && (
        <FloatingBottomTab
          activeTab={routeName}
          onTabPress={(key) => navigation.navigate(key)}
        />
      )}
    </View>
  );
}
