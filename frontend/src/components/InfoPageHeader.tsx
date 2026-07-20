import React from 'react';
import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';

interface Props {
  icon: keyof typeof Ionicons.glyphMap;
  title: string;
  subtitle?: string;
}

/** Header konsisten untuk halaman statis (FAQ, Privacy, Terms, About, Cookie). */
export function InfoPageHeader({ icon, title, subtitle }: Props) {
  const { colors } = useTheme();
  return (
    <View style={{ alignItems: 'center', marginBottom: 24, marginTop: 8 }}>
      <View style={{
        width: 52, height: 52, borderRadius: 16,
        backgroundColor: colors.primary + '18',
        alignItems: 'center', justifyContent: 'center', marginBottom: 14,
      }}>
        <Ionicons name={icon} size={26} color={colors.primary} />
      </View>
      <Text style={{ fontSize: 20, fontWeight: '800', color: colors.text, textAlign: 'center' }}>{title}</Text>
      {subtitle && (
        <Text style={{ fontSize: 13, color: colors.muted, textAlign: 'center', marginTop: 6, maxWidth: 420 }}>{subtitle}</Text>
      )}
    </View>
  );
}
