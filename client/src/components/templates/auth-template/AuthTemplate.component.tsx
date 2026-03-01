/**
 * Template — AuthTemplate
 *
 * Full-screen layout wrapper for authentication screens (login, register).
 * Handles keyboard avoidance and safe area insets automatically.
 *
 * @example
 * ```tsx
 * <AuthTemplate>
 *   <LoginForm onSubmit={handleSubmit} isLoading={false} />
 * </AuthTemplate>
 * ```
 */
import React from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useTheme } from '@/hooks/use-theme';
import { AuthTemplateProps } from './AuthTemplate.types';
import { styles } from './AuthTemplate.styles';

export function AuthTemplate({ children }: AuthTemplateProps) {
  const theme = useTheme();

  return (
    <SafeAreaView
      style={[styles.safe, { backgroundColor: theme.background }]}
      edges={['top', 'bottom']}>
      <KeyboardAvoidingView
        style={styles.kav}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 24}>
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}>
          <View style={styles.inner}>{children}</View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
