/**
 * Dashboard Screen — placeholder for the authenticated home screen.
 * Displays the logged-in user's name and a logout button.
 */
import { useRouter } from 'expo-router';
import React, { useEffect } from 'react';
import { StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { AppText } from '@/components/atoms/AppText';
import { Button } from '@/components/atoms/Button';
import { useTheme } from '@/hooks/use-theme';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { useLogoutMutation } from '@/store/api/authApi';
import {
  clearCredentials,
  selectCurrentUser,
  selectIsAuthenticated,
  selectIsHydrating,
} from '@/store/authSlice';

export default function DashboardScreen() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const theme = useTheme();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const isHydrating = useAppSelector(selectIsHydrating);
  const user = useAppSelector(selectCurrentUser);

  const [logoutMutation, { isLoading: isLoggingOut }] = useLogoutMutation();

  // Guard: if not authenticated, go back to login
  useEffect(() => {
    if (!isHydrating && !isAuthenticated) {
      router.replace('/');
    }
  }, [isAuthenticated, isHydrating, router]);

  const handleLogout = async () => {
    try {
      await logoutMutation().unwrap();
    } catch {
      // Token might already be expired — proceed with local logout anyway
    } finally {
      dispatch(clearCredentials());
    }
  };

  return (
    <SafeAreaView
      style={[styles.safe, { backgroundColor: theme.background }]}
      edges={['top', 'bottom']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <AppText variant="display" style={styles.greeting}>
            👋 Hello,
          </AppText>
          <AppText variant="heading" color="#208AEF">
            {user ? `${user.first_name} ${user.last_name}` : 'there!'}
          </AppText>
          {user ? (
            <AppText variant="caption" color={theme.textSecondary}>
              {user.role} · {user.email}
            </AppText>
          ) : null}
        </View>

        <View style={styles.placeholder}>
          <AppText variant="subheading" style={styles.placeholderTitle}>
            Dashboard
          </AppText>
          <AppText variant="body" color={theme.textSecondary} style={styles.placeholderText}>
            More features are coming soon. You are successfully authenticated!
          </AppText>
        </View>

        <Button
          label="Sign Out"
          variant="secondary"
          onPress={handleLogout}
          isLoading={isLoggingOut}
          style={styles.logoutButton}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
  },
  container: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 32,
    paddingBottom: 24,
    gap: 32,
  },
  header: {
    gap: 6,
  },
  greeting: {
    fontSize: 28,
  },
  placeholder: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  placeholderTitle: {
    textAlign: 'center',
  },
  placeholderText: {
    textAlign: 'center',
    maxWidth: 280,
  },
  logoutButton: {
    marginBottom: 8,
  },
});
