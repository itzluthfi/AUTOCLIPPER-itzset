import React, { useEffect, useRef } from 'react';
import { Animated, Easing, StyleProp, ViewStyle } from 'react-native';

interface Props {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  offset?: number;
  style?: StyleProp<ViewStyle>;
}

/**
 * Entrance animation ringan: fade + slide-up satu kali saat mount.
 * Pakai RN Animated bawaan (native driver) — tanpa dependency tambahan,
 * di web dirender sebagai transform/opacity yang murah.
 */
export function FadeInView({ children, delay = 0, duration = 450, offset = 16, style }: Props) {
  const progress = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(progress, {
      toValue: 1,
      duration,
      delay,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();
  }, []);

  return (
    <Animated.View
      style={[
        style,
        {
          opacity: progress,
          transform: [{
            translateY: progress.interpolate({ inputRange: [0, 1], outputRange: [offset, 0] }),
          }],
        },
      ]}
    >
      {children}
    </Animated.View>
  );
}
