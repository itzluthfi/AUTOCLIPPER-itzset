import React, { useEffect, useRef } from 'react';
import { View, Animated, Easing, StyleSheet, Platform } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

interface Props {
  /** Warna blob, biasanya 2-3 warna brand */
  colors?: string[];
  /** Intensitas opacity keseluruhan (0-1) */
  intensity?: number;
}

/**
 * Backdrop "aurora" bergaya produk SaaS modern: beberapa blob gradient besar
 * yang melayang perlahan. Dibangun dari View + LinearGradient (bukan gambar),
 * dianimasikan dengan Animated.loop di native driver — murah di CPU/GPU dan
 * tidak butuh library tambahan (no SVG/three.js/GSAP).
 */
export function Aurora({ colors = ['#8b5cf6', '#3b82f6', '#06b6d4'], intensity = 1 }: Props) {
  const t1 = useRef(new Animated.Value(0)).current;
  const t2 = useRef(new Animated.Value(0)).current;
  const t3 = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const loop = (val: Animated.Value, duration: number) =>
      Animated.loop(
        Animated.sequence([
          Animated.timing(val, { toValue: 1, duration, easing: Easing.inOut(Easing.sin), useNativeDriver: true }),
          Animated.timing(val, { toValue: 0, duration, easing: Easing.inOut(Easing.sin), useNativeDriver: true }),
        ])
      ).start();
    loop(t1, 9000);
    loop(t2, 12000);
    loop(t3, 15000);
  }, []);

  const blob = (
    val: Animated.Value,
    size: number,
    color: string,
    top: string | number,
    left: string | number,
    range: number
  ) => (
    <Animated.View
      pointerEvents="none"
      style={{
        position: 'absolute',
        top,
        left,
        width: size,
        height: size,
        borderRadius: size / 2,
        opacity: 0.35 * intensity,
        transform: [
          { translateX: val.interpolate({ inputRange: [0, 1], outputRange: [-range, range] }) },
          { translateY: val.interpolate({ inputRange: [0, 1], outputRange: [range * 0.6, -range * 0.6] }) },
        ],
        // Blur murni-CSS di web (tidak ada di native, tetap terlihat baik tanpanya)
        ...(Platform.OS === 'web' ? ({ filter: 'blur(60px)' } as any) : {}),
      }}
    >
      <LinearGradient
        colors={[color, color + '00']}
        style={{ width: '100%', height: '100%', borderRadius: size / 2 }}
        start={{ x: 0.3, y: 0.2 }}
        end={{ x: 1, y: 1 }}
      />
    </Animated.View>
  );

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {blob(t1, 420, colors[0], '-8%', '-10%', 40)}
      {blob(t2, 380, colors[1], '30%', '55%', 55)}
      {blob(t3, 320, colors[2] ?? colors[0], '55%', '5%', 35)}
    </View>
  );
}
