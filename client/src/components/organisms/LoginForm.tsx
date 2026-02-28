/**
 * Organism — LoginForm
 * Handles email + password inputs, validation, and submission.
 * Delegates all API calls and state management to the parent via onSubmit.
 */
import React, { useState } from 'react';
import { StyleSheet, View } from 'react-native';

import { Button } from '@/components/atoms/Button';
import { AlertBanner } from '@/components/molecules/AlertBanner';
import { FormField } from '@/components/molecules/FormField';
import { useLocalization } from '@/hooks/use-localization';

export interface LoginFormValues {
  email: string;
  password: string;
}

interface LoginFormProps {
  onSubmit: (values: LoginFormValues) => void;
  isLoading: boolean;
  errorMessage?: string | null;
}

export function LoginForm({ onSubmit, isLoading, errorMessage }: LoginFormProps) {
  const { t } = useLocalization();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState<string | undefined>();
  const [passwordError, setPasswordError] = useState<string | undefined>();
  const [touched, setTouched] = useState({ email: false, password: false });

  const validateEmail = (email: string): string | undefined => {
    if (!email.trim()) return t('auth.emailRequired');
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!re.test(email)) return t('auth.emailInvalid');
    return undefined;
  };

  const validatePassword = (password: string): string | undefined => {
    if (!password) return t('auth.passwordRequired');
    if (password.length < 6) return t('auth.passwordMinLength');
    return undefined;
  };

  const handleEmailBlur = () => {
    setTouched((t) => ({ ...t, email: true }));
    setEmailError(validateEmail(email));
  };

  const handlePasswordBlur = () => {
    setTouched((t) => ({ ...t, password: true }));
    setPasswordError(validatePassword(password));
  };

  const handleEmailChange = (text: string) => {
    setEmail(text);
    if (touched.email) setEmailError(validateEmail(text));
  };

  const handlePasswordChange = (text: string) => {
    setPassword(text);
    if (touched.password) setPasswordError(validatePassword(text));
  };

  const handleSubmit = () => {
    const eErr = validateEmail(email);
    const pErr = validatePassword(password);
    setEmailError(eErr);
    setPasswordError(pErr);
    setTouched({ email: true, password: true });
    if (eErr || pErr) return;
    onSubmit({ email: email.trim().toLowerCase(), password });
  };

  return (
    <View style={styles.container}>
      {errorMessage ? (
        <AlertBanner type="error" message={errorMessage} />
      ) : null}

      <FormField
        label={t('auth.email')}
        placeholder="you@example.com"
        keyboardType="email-address"
        value={email}
        onChangeText={handleEmailChange}
        onBlur={handleEmailBlur}
        error={emailError}
        textContentType="emailAddress"
        returnKeyType="next"
      />

      <FormField
        label={t('auth.password')}
        placeholder="••••••••"
        value={password}
        onChangeText={handlePasswordChange}
        onBlur={handlePasswordBlur}
        error={passwordError}
        secureToggle
        secureTextEntry
        textContentType="password"
        returnKeyType="done"
        onSubmitEditing={handleSubmit}
      />

      <Button
        label={t('auth.signIn')}
        onPress={handleSubmit}
        isLoading={isLoading}
        disabled={isLoading}
        style={styles.button}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 16,
    alignSelf: 'stretch',
  },
  button: {
    marginTop: 8,
  },
});
