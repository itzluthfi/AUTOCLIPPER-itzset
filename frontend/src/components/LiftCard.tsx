import React from 'react';
import { Pressable, Platform, StyleProp, ViewStyle } from 'react-native';

interface Props {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  onPress?: () => void;
}

const webStyles = Platform.OS === 'web'
  ? ({
      transitionProperty: 'transform, box-shadow, border-color',
      transitionDuration: '180ms',
      transitionTimingFunction: 'ease-out',
      willChange: 'transform',
    } as any)
  : {};

/**
 * Kartu dengan efek hover-lift halus di web (CSS transition murni, tanpa JS per-frame).
 * Di native berperilaku seperti View biasa (atau Pressable jika onPress diberikan).
 */
export function LiftCard({ children, style, onPress }: Props) {
  return (
    <Pressable
      onPress={onPress}
      disabled={!onPress}
      style={({ hovered }: any) => ([
        style,
        webStyles,
        hovered && Platform.OS === 'web'
          ? {
              transform: [{ translateY: -3 }],
              shadowColor: '#000',
              shadowOffset: { width: 0, height: 8 },
              shadowOpacity: 0.12,
              shadowRadius: 20,
            }
          : null,
      ])}
    >
      {children}
    </Pressable>
  );
}
