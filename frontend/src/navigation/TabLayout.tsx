import React, { useState } from 'react';
import { View, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { FloatingBottomTab } from '../components/FloatingBottomTab';

const TAB_SCREENS = ['Dashboard', 'CreateClip', 'History', 'Profile'];

interface Props {
  children: React.ReactNode;
  routeName: string;
  navigation: any;
}

export function TabLayout({ children, routeName, navigation }: Props) {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const showTab = TAB_SCREENS.includes(routeName);

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{ flex: 1 }}>
        {children}
      </View>
      {showTab && (
        <FloatingBottomTab
          activeTab={routeName}
          onTabPress={(key) => navigation.navigate(key)}
        />
      )}
    </View>
  );
}
