import React, { useState } from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { FloatingBottomTab } from '../components/FloatingBottomTab';
import DashboardScreen from '../screens/DashboardScreen';
import CreateClipScreen from '../screens/CreateClipScreen';
import HistoryScreen from '../screens/HistoryScreen';
import ProfileScreen from '../screens/ProfileScreen';

interface Props {
  navigation: any;
}

export function MainTabs({ navigation }: Props) {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const [activeTab, setActiveTab] = React.useState('Dashboard');

  const screens: Record<string, React.ReactNode> = {
    Dashboard: <DashboardScreen navigation={navigation} />,
    CreateClip: <CreateClipScreen navigation={navigation} />,
    History: <HistoryScreen navigation={navigation} />,
    Profile: <ProfileScreen navigation={navigation} />,
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{ flex: 1, paddingBottom: 80 }}>
        {screens[activeTab]}
      </View>
      <FloatingBottomTab activeTab={activeTab} onTabPress={setActiveTab} />
    </View>
  );
}
