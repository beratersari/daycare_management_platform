/**
 * Login Screen (index route)
 *
 * Integrates RTK Query's useLoginMutation with the Redux auth slice.
 * Handles loading, success (redirect to dashboard), and error states.
 */
import { useRouter } from 'expo-router';
import React, { useEffect } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Logo } from '@/components/atoms/logo';
import { LoginForm, type LoginFormValues } from '@/components/organisms/login-form';
import { AuthTemplate } from '@/components/templates/auth-template';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { useLoginMutation } from '@/store/api/authApi';
import {
  selectIsAuthenticated,
  selectIsHydrating,
  setCredentials,
} from '@/store/authSlice';
import { useLocalization } from '@/hooks/use-localization';
import { BrandColors } from '@/constants/theme';

export default function LoginScreen() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const isHydrating = useAppSelector(selectIsHydrating);
  const { t } = useLocalization();

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
      if (error.status === 401) return t('auth.invalidCredentials');
      if (error.status === 422) return t('auth.checkFormat');
      if (error.status === 0 || error.status === 'FETCH_ERROR')
        return t('auth.cannotReachServer');
      const data = error.data as { detail?: string } | undefined;
      if (data?.detail) return data.detail;
      return `${t('auth.serverError')} (${error.status})`;
    }
    return t('common.error');
  })();

  return (
    <AuthTemplate>
      {/* Hero section */}
      <View style={styles.hero}>
        <Logo />
        <View style={styles.tagline}>
          <AppText variant="body" style={styles.taglineText}>
            {t('auth.signInToManage')}
          </AppText>
        </View>
      </View>

      {/* Form card */}
      <View style={styles.card}>
        <AppText variant="heading" style={styles.cardTitle}>
          {t('auth.welcomeBack')}
        </AppText>
        <AppText variant="body" color="#6B7280" style={styles.cardSubtitle}>
          {t('auth.enterCredentials')}
        </AppText>

        <LoginForm
          onSubmit={handleSubmit}
          isLoading={isLoading}
          errorMessage={errorMessage}
        />

        <View style={styles.footer}>
          <AppText variant="body" color="#6B7280">
            {t('auth.noAccount')}{' '}
          </AppText>
          <Pressable onPress={navigateToRegister}>
            <AppText variant="body" color={BrandColors.coral} style={styles.link}>
              {t('auth.createOne')}
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
