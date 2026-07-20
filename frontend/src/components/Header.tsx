import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { useNavigation } from '@react-navigation/native';

interface Props {
  title?: string;
  showBack?: boolean;
  rightAction?: React.ReactNode;
}

export function Header({ title = 'AutoClipper', showBack, rightAction }: Props) {
  const { colors, isDark, theme, setTheme } = useTheme();
  const navigation = useNavigation();

  const toggleTheme = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  const themeIcon = theme === 'light' ? 'sunny' : theme === 'dark' ? 'moon' : 'laptop';

  return (
    <View style={{
      paddingHorizontal: 16,
      paddingVertical: 12,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      backgroundColor: colors.background,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
        {showBack && (
          <TouchableOpacity onPress={() => {
            if (navigation.canGoBack()) {
              navigation.goBack();
            } else {
              (navigation as any).navigate('MainTabs');
            }
          }} style={{ marginRight: 12, padding: 4 }}>
            <Ionicons name="arrow-back" size={22} color={colors.primary} />
          </TouchableOpacity>
        )}
        <Text style={{
          fontSize: 20,
          fontWeight: '700',
          color: colors.text,
        }}>{title}</Text>
      </View>

      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
        {rightAction}
        <TouchableOpacity onPress={toggleTheme} style={{
          padding: 8,
          borderRadius: 8,
          backgroundColor: colors.card,
          borderWidth: 1,
          borderColor: colors.border,
        }}>
          <Ionicons name={themeIcon} size={18} color={colors.text} />
        </TouchableOpacity>
      </View>
    </View>
  );
}
