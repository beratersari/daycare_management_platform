/**
 * Organism — RegisterForm
 *
 * Full registration form following the same patterns as LoginForm.
 * Fields: first name, last name, email, password, confirm password,
 *         role (RoleSelector molecule), school_id (for non-ADMIN roles).
 *
 * Validation is inline, on-blur and on-submit.
 * The component is purely presentational — all API calls happen in the
 * parent screen via the onSubmit callback.
 */
import React, { useState } from 'react';
import { StyleSheet, View } from 'react-native';

import { Button } from '@/components/atoms/Button';
import { AlertBanner } from '@/components/molecules/AlertBanner';
import { FormField } from '@/components/molecules/FormField';
import { RoleSelector } from '@/components/molecules/RoleSelector';
import type { UserRole } from '@/store/api/authApi';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface RegisterFormValues {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  role: UserRole;
  /** Numeric school ID entered by the user; null for ADMIN */
  school_id: number | null;
}

interface RegisterFormProps {
  onSubmit: (values: RegisterFormValues) => void;
  isLoading: boolean;
  errorMessage?: string | null;
}

// ---------------------------------------------------------------------------
// Validation helpers
// ---------------------------------------------------------------------------

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateRequired(value: string, label: string): string | undefined {
  return value.trim() ? undefined : `${label} is required`;
}

function validateEmail(email: string): string | undefined {
  if (!email.trim()) return 'Email is required';
  if (!EMAIL_RE.test(email)) return 'Please enter a valid email address';
  return undefined;
}

function validatePassword(password: string): string | undefined {
  if (!password) return 'Password is required';
  if (password.length < 6) return 'Password must be at least 6 characters';
  return undefined;
}

function validateConfirm(password: string, confirm: string): string | undefined {
  if (!confirm) return 'Please confirm your password';
  if (confirm !== password) return 'Passwords do not match';
  return undefined;
}

function validateSchoolId(value: string, role: UserRole): string | undefined {
  if (role === 'ADMIN') return undefined; // not required
  if (!value.trim()) return 'School ID is required for your role';
  if (!/^\d+$/.test(value.trim())) return 'School ID must be a number';
  return undefined;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function RegisterForm({ onSubmit, isLoading, errorMessage }: RegisterFormProps) {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName]   = useState('');
  const [email, setEmail]         = useState('');
  const [password, setPassword]   = useState('');
  const [confirm, setConfirm]     = useState('');
  const [role, setRole]           = useState<UserRole>('PARENT');
  const [schoolIdStr, setSchoolIdStr] = useState('');

  const [errors, setErrors] = useState<Record<string, string | undefined>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // ---- per-field blur handlers ----

  const touch = (field: string) =>
    setTouched((t) => ({ ...t, [field]: true }));

  const setError = (field: string, msg: string | undefined) =>
    setErrors((e) => ({ ...e, [field]: msg }));

  const handleFirstNameBlur  = () => { touch('firstName');  setError('firstName',  validateRequired(firstName, 'First name')); };
  const handleLastNameBlur   = () => { touch('lastName');   setError('lastName',   validateRequired(lastName,  'Last name'));  };
  const handleEmailBlur      = () => { touch('email');      setError('email',      validateEmail(email));                     };
  const handlePasswordBlur   = () => { touch('password');   setError('password',   validatePassword(password));               };
  const handleConfirmBlur    = () => { touch('confirm');    setError('confirm',    validateConfirm(password, confirm));        };
  const handleSchoolIdBlur   = () => { touch('schoolId');   setError('schoolId',   validateSchoolId(schoolIdStr, role));       };

  // ---- live-update handlers (only re-validate if already touched) ----

  const onFirstName  = (v: string) => { setFirstName(v);  if (touched.firstName)  setError('firstName',  validateRequired(v, 'First name')); };
  const onLastName   = (v: string) => { setLastName(v);   if (touched.lastName)   setError('lastName',   validateRequired(v, 'Last name'));  };
  const onEmail      = (v: string) => { setEmail(v);      if (touched.email)      setError('email',      validateEmail(v));                  };
  const onPassword   = (v: string) => { setPassword(v);   if (touched.password)   setError('password',   validatePassword(v));               };
  const onConfirm    = (v: string) => { setConfirm(v);    if (touched.confirm)    setError('confirm',    validateConfirm(password, v));       };
  const onSchoolId   = (v: string) => { setSchoolIdStr(v); if (touched.schoolId)  setError('schoolId',   validateSchoolId(v, role));          };

  const onRoleChange = (r: UserRole) => {
    setRole(r);
    // Re-validate school_id whenever role changes
    if (touched.schoolId) setError('schoolId', validateSchoolId(schoolIdStr, r));
  };

  // ---- submit ----

  const handleSubmit = () => {
    const allTouched = { firstName: true, lastName: true, email: true, password: true, confirm: true, schoolId: true };
    setTouched(allTouched);

    const newErrors = {
      firstName:  validateRequired(firstName, 'First name'),
      lastName:   validateRequired(lastName,  'Last name'),
      email:      validateEmail(email),
      password:   validatePassword(password),
      confirm:    validateConfirm(password, confirm),
      schoolId:   validateSchoolId(schoolIdStr, role),
    };
    setErrors(newErrors);

    if (Object.values(newErrors).some(Boolean)) return;

    onSubmit({
      first_name: firstName.trim(),
      last_name:  lastName.trim(),
      email:      email.trim().toLowerCase(),
      password,
      role,
      school_id:  role === 'ADMIN' ? null : parseInt(schoolIdStr.trim(), 10),
    });
  };

  return (
    <View style={styles.container}>
      {errorMessage ? (
        <AlertBanner type="error" message={errorMessage} />
      ) : null}

      {/* Name row */}
      <View style={styles.row}>
        <View style={styles.halfField}>
          <FormField
            label="First Name"
            placeholder="Alice"
            value={firstName}
            onChangeText={onFirstName}
            onBlur={handleFirstNameBlur}
            error={errors.firstName}
            textContentType="givenName"
            returnKeyType="next"
          />
        </View>
        <View style={styles.halfField}>
          <FormField
            label="Last Name"
            placeholder="Smith"
            value={lastName}
            onChangeText={onLastName}
            onBlur={handleLastNameBlur}
            error={errors.lastName}
            textContentType="familyName"
            returnKeyType="next"
          />
        </View>
      </View>

      <FormField
        label="Email"
        placeholder="you@example.com"
        keyboardType="email-address"
        value={email}
        onChangeText={onEmail}
        onBlur={handleEmailBlur}
        error={errors.email}
        textContentType="emailAddress"
        returnKeyType="next"
      />

      <FormField
        label="Password"
        placeholder="••••••••"
        value={password}
        onChangeText={onPassword}
        onBlur={handlePasswordBlur}
        error={errors.password}
        secureToggle
        secureTextEntry
        textContentType="newPassword"
        returnKeyType="next"
      />

      <FormField
        label="Confirm Password"
        placeholder="••••••••"
        value={confirm}
        onChangeText={onConfirm}
        onBlur={handleConfirmBlur}
        error={errors.confirm}
        secureToggle
        secureTextEntry
        textContentType="newPassword"
        returnKeyType="next"
      />

      <RoleSelector value={role} onChange={onRoleChange} disabled={isLoading} />

      {role !== 'ADMIN' ? (
        <FormField
          label="School ID"
          placeholder="e.g. 1"
          keyboardType="number-pad"
          value={schoolIdStr}
          onChangeText={onSchoolId}
          onBlur={handleSchoolIdBlur}
          error={errors.schoolId}
          returnKeyType="done"
          onSubmitEditing={handleSubmit}
        />
      ) : null}

      <Button
        label="Create Account"
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
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  halfField: {
    flex: 1,
  },
  button: {
    marginTop: 8,
  },
});
