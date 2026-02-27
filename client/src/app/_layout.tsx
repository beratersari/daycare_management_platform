/**
 * Root Layout
 *
 * expo-router's entry point (expo-router/entry) mounts ExpoRoot which creates
 * its own NavigationContainer — that is where LinkingContext and ThemeProvider
 * live.  Our _layout.tsx is rendered *inside* that container, so:
 *
 *   ✗ DO NOT import ThemeProvider / DarkTheme / DefaultTheme from
 *     @react-navigation/native here — expo-router already provides them and
 *     importing a second copy (even the same version) would create a context
 *     mismatch.
 *
 *   ✓ DO wrap the Stack in Redux Provider + PersistGate so every screen has
 *     access to the store.  These providers are transparent to navigation.
 *
 * The HydrationWatcher side-effect component dispatches setHydrated() once
 * PersistGate finishes reading AsyncStorage, which unblocks auth-redirect
 * logic in the screens.
 */
import { Stack } from 'expo-router';
import React, { useEffect } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { Provider, useDispatch } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';

import { persistor, store } from '@/store';
import { setHydrated } from '@/store/authSlice';

/** Dispatches setHydrated() as soon as PersistGate renders its children. */
function HydrationWatcher() {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(setHydrated());
  }, [dispatch]);
  return null;
}

/** Shown by PersistGate while AsyncStorage is read on the very first launch. */
function HydrationLoader() {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <ActivityIndicator size="large" color="#208AEF" />
    </View>
  );
}

export default function RootLayout() {
  return (
    <Provider store={store}>
      <PersistGate loading={<HydrationLoader />} persistor={persistor}>
        <HydrationWatcher />
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="index" options={{ title: 'Sign In' }} />
          <Stack.Screen name="dashboard" options={{ title: 'Dashboard' }} />
        </Stack>
      </PersistGate>
    </Provider>
  );
}
