import React, { useEffect, useRef, useState } from 'react';
import { Text, Animated, TextStyle, StyleProp } from 'react-native';

interface Props {
  value: number;
  suffix?: string;
  prefix?: string;
  duration?: number;
  style?: StyleProp<TextStyle>;
}

/**
 * Angka yang menghitung naik dari 0 ke `value` sekali saat mount.
 * Pakai satu Animated.Value + listener (bukan setInterval), dibulatkan supaya
 * re-render hanya terjadi saat digit yang ditampilkan benar-benar berubah.
 */
export function StatCounter({ value, suffix = '', prefix = '', duration = 1400, style }: Props) {
  const anim = useRef(new Animated.Value(0)).current;
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const id = anim.addListener(({ value: v }) => {
      const next = Math.round(v);
      setDisplay((prev) => (prev === next ? prev : next));
    });
    Animated.timing(anim, {
      toValue: value,
      duration,
      useNativeDriver: false, // perlu JS-driven karena menulis ke state, bukan style
    }).start();
    return () => anim.removeListener(id);
  }, [value]);

  return <Text style={style}>{prefix}{display.toLocaleString('id-ID')}{suffix}</Text>;
}
