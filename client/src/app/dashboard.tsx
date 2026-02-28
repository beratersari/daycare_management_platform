/**
 * Dashboard Screen — role-based authenticated home screen.
 * Displays content based on the user's role (Parent, Teacher, Admin, Director).
 */
import { useRouter } from 'expo-router';
import React, { useEffect } from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { AppText } from '@/components/atoms/AppText';
import { Button } from '@/components/atoms/Button';
import { Skeleton } from '@/components/atoms/Skeleton';
import { RoleBasedDashboard } from '@/components/organisms/RoleBasedDashboard';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { useLogoutMutation, useGetMeQuery } from '@/store/api/authApi';
import { authApi } from '@/store/api/authApi';
import { studentApi } from '@/store/api/studentApi';
import { classApi } from '@/store/api/classApi';
import { teacherApi } from '@/store/api/teacherApi';
import { parentApi } from '@/store/api/parentApi';
import { mealMenuApi } from '@/store/api/mealMenuApi';
import { persistor } from '@/store';
import {
  clearCredentials,
  setUser,
  selectCurrentUser,
  selectIsAuthenticated,
  selectIsHydrating,
} from '@/store/authSlice';
import { BrandColors } from '@/constants/theme';

export default function DashboardScreen() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const theme = useTheme();
  const { t } = useLocalization();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const isHydrating = useAppSelector(selectIsHydrating);
  const user = useAppSelector(selectCurrentUser);

  const { data: me, isLoading: isMeLoading } = useGetMeQuery(undefined, {
    skip: !isAuthenticated || !!user,
  });

  const [logoutMutation, { isLoading: isLoggingOut }] = useLogoutMutation();

  // Guard: if not authenticated, go back to login
  useEffect(() => {
    if (!isHydrating && !isAuthenticated) {
      router.replace('/');
    }
  }, [isAuthenticated, isHydrating, router]);

  // Sync user data if fetched
  useEffect(() => {
    if (me) {
      dispatch(setUser(me));
    }
  }, [me, dispatch]);

  const handleLogout = async () => {
    try {
      await logoutMutation().unwrap();
    } catch {
      // Token might already be expired — proceed with local logout anyway
    } finally {
      // Reset all RTK Query caches to clear stale data
      dispatch(authApi.util.resetApiState());
      dispatch(studentApi.util.resetApiState());
      dispatch(classApi.util.resetApiState());
      dispatch(teacherApi.util.resetApiState());
      dispatch(parentApi.util.resetApiState());
      dispatch(mealMenuApi.util.resetApiState());
      
      // Clear credentials and reset Redux state
      dispatch(clearCredentials());
      
      // Purge persisted storage to ensure no old data remains
      await persistor.purge();
    }
  };

  const getRoleLabel = (role: string): string => {
    switch (role) {
      case 'ADMIN':
        return t('roles.admin');
      case 'DIRECTOR':
        return t('roles.director');
      case 'TEACHER':
        return t('roles.teacher');
      case 'PARENT':
        return t('roles.parent');
      default:
        return role;
    }
  };

  const isLoading = isHydrating || (isAuthenticated && !user && isMeLoading);

  return (
    <SafeAreaView
      style={[styles.safe, { backgroundColor: theme.background }]}
      edges={['top', 'bottom']}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <AppText variant="display" style={styles.greeting}>
            {t('dashboard.greeting')}
          </AppText>
          {isLoading ? (
            <Skeleton width={200} height={32} style={{ marginVertical: 4 }} />
          ) : (
            <AppText variant="heading" color={BrandColors.coral}>
              {user ? `${user.first_name} ${user.last_name}` : 'there!'}
            </AppText>
          )}
          {isLoading ? (
            <Skeleton width={150} height={16} />
          ) : user ? (
            <AppText variant="caption" color={theme.textSecondary}>
              {getRoleLabel(user.role)} · {user.email}
            </AppText>
          ) : null}
        </View>

        {/* Role-based Dashboard Content */}
        <View style={styles.content}>
          {isLoading ? (
            <View style={{ gap: 16 }}>
              <Skeleton width="100%" height={100} />
              <Skeleton width="100%" height={150} />
              <Skeleton width="100%" height={100} />
            </View>
          ) : (
            <RoleBasedDashboard />
          )}
        </View>

        {/* Sign Out Button */}
        <Button
          label={t('auth.signOut')}
          variant="secondary"
          onPress={handleLogout}
          isLoading={isLoggingOut}
          style={styles.logoutButton}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
  },
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 20,
    paddingBottom: 16,
    gap: 16,
  },
  header: {
    gap: 4,
    paddingBottom: 8,
  },
  greeting: {
    fontSize: 24,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  logoutButton: {
    marginTop: 4,
  },
});
