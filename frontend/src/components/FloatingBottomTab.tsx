import React from 'react';
import { View, Text, TouchableOpacity, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';

type TabRoute = {
  key: string;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  activeIcon: keyof typeof Ionicons.glyphMap;
};

const TABS: TabRoute[] = [
  { key: 'Dashboard', label: 'Dashboard', icon: 'grid-outline', activeIcon: 'grid' },
  { key: 'CreateClip', label: 'Buat', icon: 'add-circle-outline', activeIcon: 'add-circle' },
  { key: 'History', label: 'Riwayat', icon: 'time-outline', activeIcon: 'time' },
  { key: 'Profile', label: 'Profil', icon: 'person-outline', activeIcon: 'person' },
];

interface Props {
  activeTab: string;
  onTabPress: (key: string) => void;
}

export function FloatingBottomTab({ activeTab, onTabPress }: Props) {
  const { colors, isDark } = useTheme();
  const insets = useSafeAreaInsets();

  return (
    <View style={{
      position: 'absolute', bottom: 0, left: 0, right: 0,
      alignItems: 'center',
      paddingBottom: insets.bottom > 0 ? insets.bottom - 4 : 12,
      pointerEvents: 'box-none',
    }}>
      <View style={{
        flexDirection: 'row',
        marginHorizontal: 16,
        paddingVertical: 8,
        paddingHorizontal: 6,
        borderRadius: 28,
        backgroundColor: isDark ? 'rgba(24,24,24,0.95)' : 'rgba(255,255,255,0.95)',
        borderWidth: 1,
        borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -4 },
        shadowOpacity: isDark ? 0.4 : 0.12,
        shadowRadius: 16,
        elevation: 16,
        ...(Platform.OS === 'web' ? {
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
        } : {}),
      }}>
        {TABS.map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <TouchableOpacity
              key={tab.key}
              onPress={() => onTabPress(tab.key)}
              style={{
                flex: 1,
                alignItems: 'center',
                justifyContent: 'center',
                paddingVertical: 8,
                position: 'relative',
              }}
              activeOpacity={0.6}
            >
              {isActive && (
                <View style={{
                  position: 'absolute',
                  top: -8,
                  width: 20,
                  height: 3,
                  borderRadius: 1.5,
                  backgroundColor: colors.primary,
                }} />
              )}
              <Ionicons
                name={isActive ? tab.activeIcon : tab.icon}
                size={isActive ? 24 : 22}
                color={isActive ? colors.primary : colors.muted}
              />
              <Text style={{
                fontSize: 10,
                marginTop: 2,
                color: isActive ? colors.primary : colors.muted,
                fontWeight: isActive ? '600' : '400',
              }}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}
