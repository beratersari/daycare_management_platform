/**
 * Atom — TextInput
 *
 * A themed text input with optional label, error message, and secure-text toggle.
 * Supports React Hook Form through forwardRef for proper form integration.
 *
 * @example
 * ```tsx
 * // Basic usage
 * <AppTextInput
 *   label="Email"
 *   placeholder="you@example.com"
 *   value={email}
 *   onChangeText={setEmail}
 * />
 *
 * // Password field with toggle
 * <AppTextInput
 *   label="Password"
 *   secureTextEntry
 *   secureToggle
 *   error={errors.password?.message}
 * />
 *
 * // With React Hook Form
 * <Controller
 *   control={control}
 *   name="email"
 *   render={({ field: { onChange, onBlur, value } }) => (
 *     <AppTextInput
 *       label="Email"
 *       value={value}
 *       onChangeText={onChange}
 *       onBlur={onBlur}
 *     />
 *   )}
 * />
 * ```
 */
import React, { useState, forwardRef } from 'react';
import { Pressable, TextInput as RNTextInput, View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { useTheme } from '@/hooks/use-theme';
import { AppTextInputProps } from './TextInput.types';
import { styles } from './TextInput.styles';

/** Default icon size for dashboard buttons */
const DEFAULT_ICON_SIZE = 24;

/** Default icon color (white for visibility on colored backgrounds) */
const DEFAULT_ICON_COLOR = '#000';

/** Color for error state border */
const ERROR_BORDER_COLOR = '#EF4444';

/** Accessibility labels for password toggle */
const SHOW_PASSWORD_LABEL = 'Show password';
const HIDE_PASSWORD_LABEL = 'Hide password';
const SHOW_TEXT = 'Show';
const HIDE_TEXT = 'Hide';

export const AppTextInput = forwardRef<RNTextInput, AppTextInputProps>(function AppTextInput(
  { label, error, secureToggle = false, secureTextEntry, style, ...rest },
  ref
) {
  const theme = useTheme();
  const [isHidden, setIsHidden] = useState(secureTextEntry ?? false);

  const borderColor = error ? ERROR_BORDER_COLOR : theme.backgroundElement;
  const backgroundColor = theme.backgroundElement;
  const showPasswordToggle = secureToggle && secureTextEntry;

  const togglePasswordVisibility = () => {
    setIsHidden((hidden) => !hidden);
  };

  return (
    <View style={styles.wrapper}>
      {label ? (
        <AppText variant="label" color={theme.textSecondary} style={styles.label}>
          {label}
        </AppText>
      ) : null}

      <View
        style={[
          styles.inputRow,
          { backgroundColor, borderColor },
        ]}>
        <RNTextInput
          ref={ref}
          style={[styles.input, { color: theme.text }, style]}
          placeholderTextColor={theme.textSecondary}
          secureTextEntry={secureToggle ? isHidden : secureTextEntry}
          autoCapitalize="none"
          autoCorrect={false}
          {...rest}
        />
        {showPasswordToggle ? (
          <Pressable
            onPress={togglePasswordVisibility}
            style={styles.toggle}
            hitSlop={8}
            accessibilityLabel={isHidden ? SHOW_PASSWORD_LABEL : HIDE_PASSWORD_LABEL}>
            <AppText variant="caption" color={theme.textSecondary}>
              {isHidden ? SHOW_TEXT : HIDE_TEXT}
            </AppText>
          </Pressable>
        ) : null}
      </View>

      {error ? (
        <AppText variant="error" style={styles.errorText}>
          {error}
        </AppText>
      ) : null}
    </View>
  );
});
