import React, { useEffect, useRef } from 'react';
import { View, Animated, StyleSheet } from 'react-native';
import { useTheme } from '../theme/ThemeContext';

interface Props {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: any;
}

export function SkeletonLoader({ width = '100%', height = 20, borderRadius = 8, style }: Props) {
  const { colors, isDark } = useTheme();
  const opacity = useRef(new Animated.Value(0.5)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, { toValue: 1, duration: 800, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 0.3, duration: 800, useNativeDriver: true }),
      ])
    );
    animation.start();
    return () => animation.stop();
  }, []);

  return React.createElement(Animated.View, {
    style: [{
      width: width as any,
      height,
      borderRadius,
      backgroundColor: isDark ? '#2a2a2a' : '#e2e8f0',
      opacity: opacity as any,
    }, style]
  });
}

export function CardSkeleton() {
  const { colors } = useTheme();
  return React.createElement(View, {
    style: {
      backgroundColor: colors.card,
      borderRadius: 12,
      padding: 16,
      marginBottom: 12,
      borderWidth: 1,
      borderColor: colors.border,
    }
  }, [
    React.createElement(SkeletonLoader, { key: 's1', height: 16, width: '60%', style: { marginBottom: 8 } }),
    React.createElement(SkeletonLoader, { key: 's2', height: 14, width: '40%', style: { marginBottom: 4 } }),
    React.createElement(SkeletonLoader, { key: 's3', height: 14, width: '80%' }),
  ]);
}

export function ClipCardSkeleton() {
  const { colors } = useTheme();
  return React.createElement(View, {
    style: {
      backgroundColor: colors.card,
      borderRadius: 12,
      marginBottom: 16,
      borderWidth: 1,
      borderColor: colors.border,
      overflow: 'hidden',
    }
  }, [
    React.createElement(SkeletonLoader, { key: 'cl1', height: 180, borderRadius: 12 }),
    React.createElement(View, { key: 'cl2', style: { padding: 12 } },
      React.createElement(SkeletonLoader, { height: 14, width: '70%', style: { marginBottom: 6 } }),
      React.createElement(SkeletonLoader, { height: 12, width: '50%' })
    ),
  ]);
}
