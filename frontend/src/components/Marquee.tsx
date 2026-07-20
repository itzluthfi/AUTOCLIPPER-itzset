import React, { useEffect, useRef, useState } from 'react';
import { View, Animated, Easing, LayoutChangeEvent } from 'react-native';

interface Props {
  children: React.ReactNode;
  speed?: number; // px per second
  gap?: number;
}

/**
 * Strip yang bergulir horizontal tanpa henti (dua salinan konten berdampingan,
 * digeser dengan Animated.loop native-driver). Dipakai untuk "trusted by" /
 * baris logo di landing page — animasi kontinu murah, tidak membebani JS thread.
 */
export function Marquee({ children, speed = 40, gap = 40 }: Props) {
  const [contentWidth, setContentWidth] = useState(0);
  const translateX = useRef(new Animated.Value(0)).current;

  const onLayout = (e: LayoutChangeEvent) => {
    const w = e.nativeEvent.layout.width;
    if (w > 0 && w !== contentWidth) setContentWidth(w);
  };

  useEffect(() => {
    if (!contentWidth) return;
    translateX.setValue(0);
    const duration = (contentWidth / speed) * 1000;
    const anim = Animated.loop(
      Animated.timing(translateX, {
        toValue: -(contentWidth + gap),
        duration,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    );
    anim.start();
    return () => anim.stop();
  }, [contentWidth]);

  return (
    <View style={{ overflow: 'hidden', width: '100%' }}>
      <Animated.View style={{ flexDirection: 'row', transform: [{ translateX }] }}>
        <View onLayout={onLayout} style={{ flexDirection: 'row', gap, paddingRight: gap }}>
          {children}
        </View>
        <View style={{ flexDirection: 'row', gap, paddingRight: gap }}>
          {children}
        </View>
      </Animated.View>
    </View>
  );
}
