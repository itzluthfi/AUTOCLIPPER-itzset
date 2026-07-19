import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import HomeScreen from '../screens/HomeScreen';
import LoginScreen from '../screens/LoginScreen';
import DashboardScreen from '../screens/DashboardScreen';
import CreateClipScreen from '../screens/CreateClipScreen';
import HistoryScreen from '../screens/HistoryScreen';
import ProfileScreen from '../screens/ProfileScreen';
import ProcessingScreen from '../screens/ProcessingScreen';
import ResultsScreen from '../screens/ResultsScreen';
import EditClipScreen from '../screens/EditClipScreen';
import AdminScreen from '../screens/AdminScreen';
import FAQScreen from '../screens/FAQScreen';
import PrivacyScreen from '../screens/PrivacyScreen';
import CookieScreen from '../screens/CookieScreen';
import TermsScreen from '../screens/TermsScreen';
import AboutScreen from '../screens/AboutScreen';
import { useTheme } from '../theme/ThemeContext';
import { TabLayout } from './TabLayout';

const Stack = createStackNavigator();

export function AppNavigator() {
  const { colors, isDark } = useTheme();

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: colors.background },
          animation: 'slide_from_right',
        }}
      >
        {/* Main Tabs (for Dashboard, CreateClip, History, Profile) */}
        <Stack.Screen name="MainTabs" options={{ headerShown: false }}>
          {({ navigation, route }) => (
            <TabLayout routeName={route.name} navigation={navigation}>
              <Stack.Navigator screenOptions={{ headerShown: false, animation: 'fade' }}>
                <Stack.Screen name="Dashboard" component={DashboardScreen} />
                <Stack.Screen name="CreateClip" component={CreateClipScreen} />
                <Stack.Screen name="History" component={HistoryScreen} />
                <Stack.Screen name="Profile" component={ProfileScreen} />
              </Stack.Navigator>
            </TabLayout>
          )}
        </Stack.Screen>

        {/* Other screens (no bottom tabs) */}
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Processing" component={ProcessingScreen} />
        <Stack.Screen name="Results" component={ResultsScreen} />
        <Stack.Screen name="EditClip" component={EditClipScreen} />
        <Stack.Screen name="Admin" component={AdminScreen} />
        <Stack.Screen name="FAQ" component={FAQScreen} />
        <Stack.Screen name="Privacy" component={PrivacyScreen} />
        <Stack.Screen name="Cookie" component={CookieScreen} />
        <Stack.Screen name="Terms" component={TermsScreen} />
        <Stack.Screen name="About" component={AboutScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
