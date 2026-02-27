/**
 * Atom — TextInput
 * Themed text input with optional label, error message, and secure-text toggle.
 */
import React, { useState } from 'react';
import {
  Pressable,
  StyleSheet,
  TextInput as RNTextInput,
  type TextInputProps,
  View,
} from 'react-native';

import { AppText } from '@/components/atoms/AppText';
import { useTheme } from '@/hooks/use-theme';

export interface AppTextInputProps extends TextInputProps {
  label?: string;
  error?: string;
  /** Render a show/hide toggle for password fields */
  secureToggle?: boolean;
}

export function AppTextInput({
  label,
  error,
  secureToggle = false,
  secureTextEntry,
  style,
  ...rest
}: AppTextInputProps) {
  const theme = useTheme();
  const [hidden, setHidden] = useState(secureTextEntry ?? false);

  const borderColor = error ? '#EF4444' : theme.backgroundElement;
  const inputBg = theme.backgroundElement;

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
          { backgroundColor: inputBg, borderColor },
        ]}>
        <RNTextInput
          style={[styles.input, { color: theme.text }, style]}
          placeholderTextColor={theme.textSecondary}
          secureTextEntry={secureToggle ? hidden : secureTextEntry}
          autoCapitalize="none"
          autoCorrect={false}
          {...rest}
        />
        {secureToggle ? (
          <Pressable
            onPress={() => setHidden((h) => !h)}
            style={styles.toggle}
            hitSlop={8}
            accessibilityLabel={hidden ? 'Show password' : 'Hide password'}>
            <AppText variant="caption" color={theme.textSecondary}>
              {hidden ? 'Show' : 'Hide'}
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
}

const styles = StyleSheet.create({
  wrapper: {
    gap: 6,
    alignSelf: 'stretch',
  },
  label: {
    marginLeft: 2,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1.5,
    paddingHorizontal: 16,
    height: 52,
  },
  input: {
    flex: 1,
    fontSize: 15,
    fontWeight: '400',
  },
  toggle: {
    paddingLeft: 12,
  },
  errorText: {
    marginLeft: 2,
  },
});
