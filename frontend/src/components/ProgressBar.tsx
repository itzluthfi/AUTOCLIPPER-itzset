import React from 'react';
import { View, Text, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';

interface Props {
  progress: number;
  label?: string;
  step?: string;
}

const steps = [
  { min: 0, label: 'Mengunduh video...', icon: 'download' },
  { min: 20, label: 'Mengekstrak subtitle...', icon: 'document-text' },
  { min: 40, label: 'Mendeteksi momen penting...', icon: 'locate' },
  { min: 60, label: 'Mengklip video...', icon: 'cut' },
  { min: 80, label: 'Memproses tracking...', icon: 'videocam' },
  { min: 95, label: 'Menyelesaikan...', icon: 'checkmark-circle' },
];

export function ProgressBar({ progress, label, step }: Props) {
  const { colors, isDark } = useTheme();

  const currentStep = steps.reduce((prev, curr) => {
    return progress >= curr.min ? curr : prev;
  }, steps[0]);

  const barColor = progress >= 100 ? colors.success : colors.primary;

  return (
    <View style={{ padding: 16 }}>
      <View style={{
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 8,
      }}>
        <Text style={{ color: colors.text, fontSize: 14, fontWeight: '500' }}>
          {step || currentStep.label}
        </Text>
        <Text style={{ color: colors.primary, fontSize: 14, fontWeight: '600' }}>
          {Math.round(progress)}%
        </Text>
      </View>

      <View style={{
        height: 8,
        borderRadius: 4,
        backgroundColor: isDark ? '#2a2a2a' : '#e2e8f0',
        overflow: 'hidden',
      }}>
        <View style={{
          width: `${Math.min(100, progress)}%`,
          height: '100%',
          borderRadius: 4,
          backgroundColor: barColor,
        }} />
      </View>

      {progress < 100 && (
        <Text style={{ color: colors.muted, fontSize: 12, marginTop: 4 }}>
          Proses ini memakan waktu 1-5 menit. Anda bisa meninggalkan halaman ini.
        </Text>
      )}
    </View>
  );
}

export function StepIndicator({ current, total }: { current: number; total: number }) {
  const { colors, isDark } = useTheme();
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 4 }}>
      {Array.from({ length: total }).map((_, i) => (
        <View key={i} style={{
          width: i === current ? 24 : 8,
          height: 8,
          borderRadius: 4,
          backgroundColor: i <= current ? colors.primary : isDark ? '#333' : '#ddd',
        }} />
      ))}
      <Text style={{ color: colors.muted, fontSize: 12, marginLeft: 8 }}>
        {current + 1}/{total}
      </Text>
    </View>
  );
}
