import React from 'react';
import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { StatCounter } from './StatCounter';
import { LiftCard } from './LiftCard';

interface Props {
  icon: keyof typeof Ionicons.glyphMap;
  color: string;
  label: string;
  value: number;
  suffix?: string;
}

export function StatTile({ icon, color, label, value, suffix }: Props) {
  const { colors, isDark } = useTheme();
  return (
    <LiftCard style={{
      flex: 1,
      minWidth: 140,
      padding: 16,
      borderRadius: 14,
      borderWidth: 1,
      borderColor: colors.border,
      backgroundColor: isDark ? '#121214' : '#ffffff',
    }}>
      <View style={{
        width: 36, height: 36, borderRadius: 10,
        backgroundColor: color + '18',
        alignItems: 'center', justifyContent: 'center', marginBottom: 10,
      }}>
        <Ionicons name={icon} size={18} color={color} />
      </View>
      <StatCounter value={value} suffix={suffix} style={{ fontSize: 22, fontWeight: '800', color: colors.text }} />
      <Text style={{ fontSize: 12, color: colors.muted, marginTop: 2 }}>{label}</Text>
    </LiftCard>
  );
}
