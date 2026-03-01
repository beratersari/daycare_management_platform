/**
 * Organism — RegisterForm
 *
 * A complete registration form with name, email, password, role selection,
 * and school ID fields. Uses React Hook Form for state management and validation.
 *
 * @example
 * ```tsx
 * <RegisterForm
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
import { RoleSelector } from '@/components/molecules/role-selector';
import { useLocalization } from '@/hooks/use-localization';
import type { UserRole } from '@/store/api/authApi';
import { RegisterFormProps, RegisterFormValues } from './RegisterForm.types';
import { styles } from './RegisterForm.styles';

/**
 * Internal form values structure.
 * Uses camelCase for form fields, converts to snake_case on submit.
 */
interface FormValues {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirm: string;
  role: UserRole;
  schoolId: string;
}

/** Email validation regex pattern */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** Minimum password length */
const MIN_PASSWORD_LENGTH = 6;

/** Default role for new users */
const DEFAULT_ROLE: UserRole = 'PARENT';

export function RegisterForm({ onSubmit, isLoading, errorMessage }: RegisterFormProps) {
  const { t } = useLocalization();

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirm: '',
      role: DEFAULT_ROLE,
      schoolId: '',
    },
  });

  const currentRole = watch('role');
  const currentPassword = watch('password');

  /**
   * Validates that a field is not empty.
   */
  const validateRequired = (value: string, label: string): string | undefined => {
    return value.trim() ? undefined : t('auth.firstNameRequired').replace('First name', label);
  };

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
   * Validates that confirmation matches password.
   */
  const validateConfirm = (confirm: string): string | undefined => {
    if (!confirm) return t('auth.confirmPassword');
    if (confirm !== currentPassword) return t('auth.passwordMismatch');
    return undefined;
  };

  /**
   * Validates school ID for non-admin roles.
   */
  const validateSchoolId = (value: string, role: UserRole): string | undefined => {
    if (role === 'ADMIN') return undefined;
    if (!value.trim()) return t('auth.schoolIdRequired');
    if (!/^\d+$/.test(value.trim())) return t('auth.schoolIdNumber');
    return undefined;
  };

  /**
   * Handles form submission with normalized data.
   */
  const handleFormSubmit = (data: FormValues) => {
    onSubmit({
      first_name: data.firstName.trim(),
      last_name: data.lastName.trim(),
      email: data.email.trim().toLowerCase(),
      password: data.password,
      role: data.role,
      school_id: data.role === 'ADMIN' ? null : parseInt(data.schoolId.trim(), 10),
    });
  };

  const showSchoolIdField = currentRole !== 'ADMIN';

  return (
    <View style={styles.container}>
      {errorMessage ? (
        <AlertBanner type="error" message={errorMessage} />
      ) : null}

      <View style={styles.row}>
        <View style={styles.halfField}>
          <Controller
            control={control}
            name="firstName"
            rules={{ validate: (v) => validateRequired(v, t('auth.firstName')) }}
            render={({ field: { onChange, onBlur, value } }) => (
              <FormField
                label={t('auth.firstName')}
                placeholder="Alice"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                error={errors.firstName?.message}
                textContentType="givenName"
                returnKeyType="next"
              />
            )}
          />
        </View>
        <View style={styles.halfField}>
          <Controller
            control={control}
            name="lastName"
            rules={{ validate: (v) => validateRequired(v, t('auth.lastName')) }}
            render={({ field: { onChange, onBlur, value } }) => (
              <FormField
                label={t('auth.lastName')}
                placeholder="Smith"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                error={errors.lastName?.message}
                textContentType="familyName"
                returnKeyType="next"
              />
            )}
          />
        </View>
      </View>

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
            textContentType="newPassword"
            returnKeyType="next"
          />
        )}
      />

      <Controller
        control={control}
        name="confirm"
        rules={{ validate: validateConfirm }}
        render={({ field: { onChange, onBlur, value } }) => (
          <FormField
            label={t('auth.confirmPassword')}
            placeholder="••••••••"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            error={errors.confirm?.message}
            secureToggle
            secureTextEntry
            textContentType="newPassword"
            returnKeyType="next"
          />
        )}
      />

      <Controller
        control={control}
        name="role"
        render={({ field: { onChange, value } }) => (
          <RoleSelector value={value} onChange={onChange} disabled={isLoading} />
        )}
      />

      {showSchoolIdField ? (
        <Controller
          control={control}
          name="schoolId"
          rules={{ validate: (v) => validateSchoolId(v, currentRole) }}
          render={({ field: { onChange, onBlur, value } }) => (
            <FormField
              label={t('auth.schoolId')}
              placeholder="e.g. 1"
              keyboardType="number-pad"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={errors.schoolId?.message}
              returnKeyType="done"
              onSubmitEditing={handleSubmit(handleFormSubmit)}
            />
          )}
        />
      ) : null}

      <Button
        label={t('auth.createAccount')}
        onPress={handleSubmit(handleFormSubmit)}
        isLoading={isLoading}
        disabled={isLoading}
        style={styles.button}
      />
    </View>
  );
}

export type { RegisterFormValues };
