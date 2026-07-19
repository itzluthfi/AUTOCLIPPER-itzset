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

  const bottomOffset = Platform.OS === 'web' ? 16 : insets.bottom > 0 ? insets.bottom : 12;

  return (
    <View
      style={{
        position: (Platform.OS === 'web' ? 'fixed' : 'absolute') as any,
        bottom: bottomOffset,
        left: 0,
        right: 0,
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        pointerEvents: 'box-none',
      }}
    >
      <View
        style={{
          width: '92%',
          maxWidth: 420,
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'space-around',
          paddingVertical: 10,
          paddingHorizontal: 8,
          borderRadius: 32,
          backgroundColor: isDark ? 'rgba(18, 18, 22, 0.95)' : 'rgba(255, 255, 255, 0.95)',
          borderWidth: 1,
          borderColor: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)',
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 10 },
          shadowOpacity: isDark ? 0.5 : 0.15,
          shadowRadius: 20,
          elevation: 12,
          ...(Platform.OS === 'web'
            ? {
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
              }
            : {}),
        }}
      >
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
                paddingVertical: 4,
                position: 'relative',
              }}
              activeOpacity={0.7}
            >
              {isActive && (
                <View
                  style={{
                    position: 'absolute',
                    top: -10,
                    width: 24,
                    height: 3,
                    borderRadius: 2,
                    backgroundColor: colors.primary,
                  }}
                />
              )}
              <Ionicons
                name={isActive ? tab.activeIcon : tab.icon}
                size={22}
                color={isActive ? colors.primary : colors.muted}
              />
              <Text
                style={{
                  fontSize: 11,
                  marginTop: 3,
                  color: isActive ? colors.primary : colors.muted,
                  fontWeight: isActive ? '700' : '500',
                  textAlign: 'center',
                }}
                numberOfLines={1}
              >
                {tab.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}
