import React from 'react';
import { View, StyleProp, ViewStyle } from 'react-native';

interface Props {
  children: React.ReactNode;
  maxWidth?: number;
  style?: StyleProp<ViewStyle>;
}

/**
 * Wrapper lebar responsif: konten aplikasi (dashboard, form, dsb.) dibatasi
 * max-width dan di-center di layar besar, tapi full-width di mobile.
 * Dipakai di semua layar dalam-app supaya tidak melebar mentah di desktop.
 */
export function PageContainer({ children, maxWidth = 880, style }: Props) {
  return (
    <View style={{ width: '100%', alignItems: 'center' }}>
      <View style={[{ width: '100%', maxWidth }, style]}>
        {children}
      </View>
    </View>
  );
}
