/**
 * Login Screen (index route)
 *
 * Integrates RTK Query's useLoginMutation with the Redux auth slice.
 * Handles loading, success (redirect to dashboard), and error states.
 */
import { useRouter } from 'expo-router';
import React, { useEffect } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/AppText';
import { Logo } from '@/components/atoms/Logo';
import { LoginForm, type LoginFormValues } from '@/components/organisms/LoginForm';
import { AuthTemplate } from '@/components/templates/AuthTemplate';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { useLoginMutation } from '@/store/api/authApi';
import {
  selectIsAuthenticated,
  selectIsHydrating,
  setCredentials,
} from '@/store/authSlice';

export default function LoginScreen() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const isHydrating = useAppSelector(selectIsHydrating);

  const [login, { isLoading, error, reset }] = useLoginMutation();

  // Redirect to dashboard once authenticated
  useEffect(() => {
    if (!isHydrating && isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [isAuthenticated, isHydrating, router]);

  const handleSubmit = async (values: LoginFormValues) => {
    reset(); // clear any previous error
    try {
      const tokens = await login(values).unwrap();
      dispatch(setCredentials({ tokens }));
      // Navigation happens via the useEffect above
    } catch {
      // error is captured by RTK Query — rendered below
    }
  };

  const navigateToRegister = () => {
    router.push('/register');
  };

  /** Extract a human-readable error message from the RTK Query error */
  const errorMessage = (() => {
    if (!error) return null;
    if ('status' in error) {
      if (error.status === 401) return 'Invalid email or password. Please try again.';
      if (error.status === 422) return 'Please check your email and password format.';
      if (error.status === 0 || error.status === 'FETCH_ERROR')
        return 'Cannot reach the server. Check your connection.';
      const data = error.data as { detail?: string } | undefined;
      if (data?.detail) return data.detail;
      return `Server error (${error.status}). Please try again.`;
    }
    return 'An unexpected error occurred. Please try again.';
  })();

  return (
    <AuthTemplate>
      {/* Hero section */}
      <View style={styles.hero}>
        <Logo />
        <View style={styles.tagline}>
          <AppText variant="body" style={styles.taglineText}>
            Sign in to manage your daycare
          </AppText>
        </View>
      </View>

      {/* Form card */}
      <View style={styles.card}>
        <AppText variant="heading" style={styles.cardTitle}>
          Welcome back
        </AppText>
        <AppText variant="body" color="#6B7280" style={styles.cardSubtitle}>
          Enter your credentials to continue
        </AppText>

        <LoginForm
          onSubmit={handleSubmit}
          isLoading={isLoading}
          errorMessage={errorMessage}
        />

        <View style={styles.footer}>
          <AppText variant="body" color="#6B7280">
            Don't have an account?{' '}
          </AppText>
          <Pressable onPress={navigateToRegister}>
            <AppText variant="body" color="#208AEF" style={styles.link}>
              Create one
            </AppText>
          </Pressable>
        </View>
      </View>
    </AuthTemplate>
  );
}

const styles = StyleSheet.create({
  hero: {
    alignItems: 'center',
    gap: 12,
  },
  tagline: {
    alignItems: 'center',
  },
  taglineText: {
    textAlign: 'center',
    color: '#6B7280',
  },
  card: {
    alignSelf: 'stretch',
    gap: 12,
  },
  cardTitle: {
    textAlign: 'center',
  },
  cardSubtitle: {
    textAlign: 'center',
    marginBottom: 4,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 8,
  },
  link: {
    fontWeight: '600',
  },
});
