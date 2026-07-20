import React, { useRef } from 'react';
import { Animated, Text, ActivityIndicator, Pressable, Platform, StyleProp, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';

let Haptics: typeof import('expo-haptics') | null = null;
if (Platform.OS !== 'web') {
  try { Haptics = require('expo-haptics'); } catch { Haptics = null; }
}

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
type Size = 'md' | 'lg';

interface Props {
  label: string;
  onPress?: () => void;
  variant?: Variant;
  size?: Size;
  icon?: keyof typeof Ionicons.glyphMap;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  style?: StyleProp<ViewStyle>;
}

/**
 * Tombol CTA reusable dengan micro-motion (scale-down on press) via Animated
 * native driver — konsisten di semua layar, murah, tanpa GSAP/lib eksternal.
 */
export function Button({
  label, onPress, variant = 'primary', size = 'lg', icon, iconPosition = 'left',
  loading, disabled, fullWidth, style,
}: Props) {
  const { colors } = useTheme();
  const scale = useRef(new Animated.Value(1)).current;
  const isDisabled = disabled || loading;

  const press = (toValue: number) => {
    Animated.spring(scale, { toValue, useNativeDriver: true, speed: 40, bounciness: 6 }).start();
  };

  const palette: Record<Variant, { bg: string; fg: string; border?: string }> = {
    primary: { bg: colors.primary, fg: '#fff' },
    secondary: { bg: 'transparent', fg: colors.text, border: colors.border },
    ghost: { bg: colors.primary + '15', fg: colors.primary },
    danger: { bg: colors.error, fg: '#fff' },
  };
  const p = palette[variant];
  const padV = size === 'lg' ? 15 : 11;
  const padH = size === 'lg' ? 24 : 16;
  const fontSize = size === 'lg' ? 15 : 13;

  return (
    <Animated.View style={[{ transform: [{ scale }] }, fullWidth && { width: '100%' }, style]}>
      <Pressable
        onPress={() => {
          if (isDisabled) return;
          if (Haptics) Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light).catch(() => {});
          onPress?.();
        }}
        onPressIn={() => !isDisabled && press(0.96)}
        onPressOut={() => !isDisabled && press(1)}
        disabled={isDisabled}
        style={({ hovered }: any) => [
          {
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            paddingVertical: padV,
            paddingHorizontal: padH,
            borderRadius: 12,
            backgroundColor: p.bg,
            borderWidth: p.border ? 1 : 0,
            borderColor: p.border,
            opacity: isDisabled ? 0.55 : hovered ? 0.92 : 1,
          },
          variant === 'primary' && {
            shadowColor: colors.primary,
            shadowOffset: { width: 0, height: 6 },
            shadowOpacity: 0.28,
            shadowRadius: 14,
          },
          Platform.OS === 'web' && ({ transitionProperty: 'opacity, transform', transitionDuration: '120ms', cursor: isDisabled ? 'default' : 'pointer' } as any),
        ]}
      >
        {loading ? (
          <ActivityIndicator size="small" color={p.fg} />
        ) : (
          <>
            {icon && iconPosition === 'left' && <Ionicons name={icon} size={size === 'lg' ? 18 : 16} color={p.fg} />}
            <Text style={{ color: p.fg, fontWeight: '700', fontSize }}>{label}</Text>
            {icon && iconPosition === 'right' && <Ionicons name={icon} size={size === 'lg' ? 18 : 16} color={p.fg} />}
          </>
        )}
      </Pressable>
    </Animated.View>
  );
}
