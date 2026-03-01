/**
 * Register Screen
 *
 * Accessible from the Login screen via "Create account" link.
 * Uses RegisterForm organism + RTK Query useRegisterMutation.
 *
 * Flow:
 *   1. User fills in the form and taps "Create Account"
 *   2. POST /api/v1/auth/register is called
 *   3. On success → show success banner → redirect to login after 1.5 s
 *   4. On error   → show error banner (field-level or server-level)
 */
import { useRouter } from 'expo-router';
import React, { useEffect, useRef, useState } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Logo } from '@/components/atoms/logo';
import { AlertBanner } from '@/components/molecules/alert-banner';
import { RegisterForm, type RegisterFormValues } from '@/components/organisms/register-form';
import { AuthTemplate } from '@/components/templates/auth-template';
import { useRegisterMutation } from '@/store/api/authApi';
import { useLocalization } from '@/hooks/use-localization';
import { BrandColors } from '@/constants/theme';

const BRAND = BrandColors.coral;

export default function RegisterScreen() {
  const router = useRouter();
  const { t } = useLocalization();
  const [register, { isLoading, reset }] = useRegisterMutation();

  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage,   setErrorMessage]   = useState<string | null>(null);

  // Auto-redirect to login after successful registration
  const redirectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => { if (redirectTimer.current) clearTimeout(redirectTimer.current); }, []);

  const handleSubmit = async (values: RegisterFormValues) => {
    reset();
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const created = await register(values).unwrap();
      setSuccessMessage(
        t('auth.registrationSuccess', { name: `${created.first_name} ${created.last_name}` }),
      );
      redirectTimer.current = setTimeout(() => router.replace('/'), 1500);
    } catch (err: unknown) {
      setErrorMessage(extractError(err));
    }
  };

  const goToLogin = () => {
    reset();
    router.replace('/');
  };

  return (
    <AuthTemplate>
      {/* Hero */}
      <View style={styles.hero}>
        <Logo />
        <AppText variant="body" color="#6B7280" style={styles.subtitle}>
          Create your Kinder Tracker account
        </AppText>
      </View>

      {/* Card */}
      <View style={styles.card}>
        <AppText variant="heading" style={styles.cardTitle}>
          {t('auth.createAccount')}
        </AppText>
        <AppText variant="body" color="#6B7280" style={styles.cardSubtitle}>
          Fill in the details below to get started
        </AppText>

        {successMessage ? (
          <AlertBanner type="success" message={successMessage} />
        ) : null}

        <RegisterForm
          onSubmit={handleSubmit}
          isLoading={isLoading}
          errorMessage={successMessage ? null : errorMessage}
        />
      </View>

      {/* Back to login */}
      <View style={styles.footer}>
        <AppText variant="body" color="#6B7280">
          {t('auth.hasAccount')}{' '}
        </AppText>
        <Pressable onPress={goToLogin} hitSlop={8}>
          <AppText variant="body" color={BRAND} style={styles.link}>
            {t('auth.signIn')}
          </AppText>
        </Pressable>
      </View>
    </AuthTemplate>
  );
}

// ---------------------------------------------------------------------------
// Error extraction helper
// ---------------------------------------------------------------------------

function extractError(err: unknown): string {
  if (!err || typeof err !== 'object') return 'An unexpected error occurred.';
  const e = err as { status?: number | string; data?: unknown };

  if (e.status === 400) {
    const detail = (e.data as { detail?: string })?.detail;
    if (detail) return detail;
    return 'Registration failed. Please check your details.';
  }
  if (e.status === 404) return 'School not found. Please check the School ID.';
  if (e.status === 422) {
    // Pydantic validation error — extract first message
    const errors = (e.data as { detail?: Array<{ msg: string }> })?.detail;
    if (Array.isArray(errors) && errors.length > 0) return errors[0].msg;
    return 'Please check your input and try again.';
  }
  if (e.status === 0 || e.status === 'FETCH_ERROR')
    return 'Cannot reach the server. Check your connection.';

  return `Server error (${e.status ?? 'unknown'}). Please try again.`;
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles = StyleSheet.create({
  hero: {
    alignItems: 'center',
    gap: 12,
  },
  subtitle: {
    textAlign: 'center',
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
    alignItems: 'center',
    justifyContent: 'center',
  },
  link: {
    fontWeight: '600',
  },
});
