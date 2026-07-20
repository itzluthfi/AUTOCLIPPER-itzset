import React from 'react';
import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  label: string;
  color?: string;
  icon?: keyof typeof Ionicons.glyphMap;
}

/** Pill badge kecil dengan ikon asli (bukan emoji) — dipakai di landing & status. */
export function Badge({ label, color = '#8b5cf6', icon }: Props) {
  return (
    <View style={{
      alignSelf: 'flex-start',
      flexDirection: 'row',
      alignItems: 'center',
      gap: 6,
      backgroundColor: color + '18',
      borderColor: color + '40',
      borderWidth: 1,
      paddingHorizontal: 12,
      paddingVertical: 6,
      borderRadius: 20,
    }}>
      {icon && <Ionicons name={icon} size={12} color={color} />}
      <Text style={{ color, fontSize: 12, fontWeight: '700' }}>{label}</Text>
    </View>
  );
}
