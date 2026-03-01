/**
 * Organism — LoginForm
 *
 * A complete login form with email and password fields, validation, and submission.
 * Uses React Hook Form for form state management and validation.
 *
 * @example
 * ```tsx
 * <LoginForm
 *   onSubmit={(values) => console.log(values)}
 *   isLoading={false}
 *   errorMessage={null}
 * />
 * ```
 */
import React from 'react';
import { View } from 'react-native';
import { useForm, Controller } from 'react-hook-form';

import { Button } from '@/components/atoms/button';
import { AlertBanner } from '@/components/molecules/alert-banner';
import { FormField } from '@/components/molecules/form-field';
import { useLocalization } from '@/hooks/use-localization';
import { LoginFormProps, LoginFormValues } from './LoginForm.types';
import { styles } from './LoginForm.styles';

/** Email validation regex pattern */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** Minimum password length */
const MIN_PASSWORD_LENGTH = 6;

export function LoginForm({ onSubmit, isLoading, errorMessage }: LoginFormProps) {
  const { t } = useLocalization();

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    defaultValues: {
      email: '',
      password: '',
    },
  });

  /**
   * Validates email format and presence.
   */
  const validateEmail = (email: string): string | undefined => {
    if (!email.trim()) return t('auth.emailRequired');
    if (!EMAIL_PATTERN.test(email)) return t('auth.emailInvalid');
    return undefined;
  };

  /**
   * Validates password presence and minimum length.
   */
  const validatePassword = (password: string): string | undefined => {
    if (!password) return t('auth.passwordRequired');
    if (password.length < MIN_PASSWORD_LENGTH) return t('auth.passwordMinLength');
    return undefined;
  };

  /**
   * Handles form submission with normalized email.
   */
  const handleFormSubmit = (data: LoginFormValues) => {
    onSubmit({
      email: data.email.trim().toLowerCase(),
      password: data.password,
    });
  };

  return (
    <View style={styles.container}>
      {errorMessage ? (
        <AlertBanner type="error" message={errorMessage} />
      ) : null}

      <Controller
        control={control}
        name="email"
        rules={{ validate: validateEmail }}
        render={({ field: { onChange, onBlur, value } }) => (
          <FormField
            label={t('auth.email')}
            placeholder="you@example.com"
            keyboardType="email-address"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            error={errors.email?.message}
            textContentType="emailAddress"
            returnKeyType="next"
          />
        )}
      />

      <Controller
        control={control}
        name="password"
        rules={{ validate: validatePassword }}
        render={({ field: { onChange, onBlur, value } }) => (
          <FormField
            label={t('auth.password')}
            placeholder="••••••••"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            error={errors.password?.message}
            secureToggle
            secureTextEntry
            textContentType="password"
            returnKeyType="done"
            onSubmitEditing={handleSubmit(handleFormSubmit)}
          />
        )}
      />

      <Button
        label={t('auth.signIn')}
        onPress={handleSubmit(handleFormSubmit)}
        isLoading={isLoading}
        disabled={isLoading}
        style={styles.button}
      />
    </View>
  );
}

export type { LoginFormValues };
