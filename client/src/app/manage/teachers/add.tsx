/**
 * Add Teacher Page
 *
 * Dedicated page for admins and directors to add new teachers to the system.
 */
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { View, ScrollView, TextInput, Pressable, Text } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { PageHeader } from '@/components/molecules/page-header';
import { AlertBanner } from '@/components/molecules/alert-banner';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useTheme } from '@/hooks/use-theme';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { useListSchoolsQuery } from '@/store/api/schoolApi';
import { useRegisterMutation } from '@/store/api/authApi';
import { BrandColors } from '@/constants/theme';

// Validation helpers
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const validatePassword = (password: string): { valid: boolean; error?: string } => {
  if (password.length < 6) return { valid: false, error: 'Password must be at least 6 characters' };
  if (password.length > 50) return { valid: false, error: 'Password must be less than 50 characters' };
  return { valid: true };
};

const validateName = (name: string, fieldName: string): { valid: boolean; error?: string } => {
  if (!name.trim()) return { valid: false, error: `${fieldName} is required` };
  if (name.trim().length < 2) return { valid: false, error: `${fieldName} must be at least 2 characters` };
  if (name.trim().length > 50) return { valid: false, error: `${fieldName} must be less than 50 characters` };
  if (!/^[a-zA-Z\s'-]+$/.test(name.trim())) return { valid: false, error: `${fieldName} contains invalid characters` };
  return { valid: true };
};

const validatePhone = (phone: string): { valid: boolean; error?: string } => {
  if (!phone.trim()) return { valid: true }; // Optional field
  const phoneRegex = /^[\d\s\-+()]{7,20}$/;
  if (!phoneRegex.test(phone.trim())) return { valid: false, error: 'Invalid phone number format' };
  return { valid: true };
};

export default function AddTeacherScreen() {
  const router = useRouter();
  const theme = useTheme();
  const user = useAppSelector(selectCurrentUser);
  const userRole = user?.role;
  const canManage = userRole === 'ADMIN' || userRole === 'DIRECTOR';
  
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [selectedSchoolId, setSelectedSchoolId] = useState<number | null>(user?.school_id || null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  
  const { data: schools } = useListSchoolsQuery(undefined, { skip: userRole !== 'ADMIN' });
  const [register, { isLoading }] = useRegisterMutation();
  
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    const firstNameResult = validateName(firstName, 'First name');
    if (!firstNameResult.valid) newErrors.firstName = firstNameResult.error!;
    
    const lastNameResult = validateName(lastName, 'Last name');
    if (!lastNameResult.valid) newErrors.lastName = lastNameResult.error!;
    
    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(email.trim())) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    const passwordResult = validatePassword(password);
    if (!passwordResult.valid) newErrors.password = passwordResult.error!;
    
    const phoneResult = validatePhone(phone);
    if (!phoneResult.valid) newErrors.phone = phoneResult.error!;
    
    if (!selectedSchoolId) {
      newErrors.school = 'Please select a school';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async () => {
    setSubmitError(null);
    
    if (!validate()) return;
    
    try {
      await register({
        email: email.trim().toLowerCase(),
        password: password,
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        role: 'TEACHER',
        school_id: selectedSchoolId,
        phone: phone.trim() || null,
      }).unwrap();
      
      router.back();
    } catch (error: any) {
      const message = error?.data?.detail || error?.message || 'Failed to create teacher';
      setSubmitError(message);
    }
  };
  
  const clearError = (field: string) => {
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[field];
      return newErrors;
    });
  };
  
  if (!canManage) {
    return (
      <ScreenTemplate header={<PageHeader title="Add Teacher" onBack={() => router.back()} />}>
        <AlertBanner type="error" message="You don't have permission to add teachers." />
      </ScreenTemplate>
    );
  }
  
  return (
    <ScreenTemplate header={<PageHeader title="Add New Teacher" onBack={() => router.back()} />}>
      <ScrollView showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled">
        {submitError && <AlertBanner type="error" message={submitError} onDismiss={() => setSubmitError(null)} />}
        
        <View style={{ gap: 16, padding: 16 }}>
          <View>
            <AppText variant="label">First Name *</AppText>
            <TextInput
              style={{
                padding: 12,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: errors.firstName ? BrandColors.coral : theme.textSecondary + '40',
                color: theme.text,
                marginTop: 4,
                backgroundColor: theme.background,
              }}
              value={firstName}
              onChangeText={(text) => { setFirstName(text); clearError('firstName'); }}
              placeholder="Enter first name"
              placeholderTextColor={theme.textSecondary}
              maxLength={50}
            />
            {errors.firstName && <AppText variant="caption" color={BrandColors.coral}>{errors.firstName}</AppText>}
          </View>
          
          <View>
            <AppText variant="label">Last Name *</AppText>
            <TextInput
              style={{
                padding: 12,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: errors.lastName ? BrandColors.coral : theme.textSecondary + '40',
                color: theme.text,
                marginTop: 4,
                backgroundColor: theme.background,
              }}
              value={lastName}
              onChangeText={(text) => { setLastName(text); clearError('lastName'); }}
              placeholder="Enter last name"
              placeholderTextColor={theme.textSecondary}
              maxLength={50}
            />
            {errors.lastName && <AppText variant="caption" color={BrandColors.coral}>{errors.lastName}</AppText>}
          </View>
          
          <View>
            <AppText variant="label">Email *</AppText>
            <TextInput
              style={{
                padding: 12,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: errors.email ? BrandColors.coral : theme.textSecondary + '40',
                color: theme.text,
                marginTop: 4,
                backgroundColor: theme.background,
              }}
              value={email}
              onChangeText={(text) => { setEmail(text); clearError('email'); }}
              placeholder="Enter email address"
              placeholderTextColor={theme.textSecondary}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              maxLength={100}
            />
            {errors.email && <AppText variant="caption" color={BrandColors.coral}>{errors.email}</AppText>}
          </View>
          
          <View>
            <AppText variant="label">Password *</AppText>
            <TextInput
              style={{
                padding: 12,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: errors.password ? BrandColors.coral : theme.textSecondary + '40',
                color: theme.text,
                marginTop: 4,
                backgroundColor: theme.background,
              }}
              value={password}
              onChangeText={(text) => { setPassword(text); clearError('password'); }}
              placeholder="Enter password (min 6 characters)"
              placeholderTextColor={theme.textSecondary}
              secureTextEntry
              maxLength={50}
            />
            {errors.password && <AppText variant="caption" color={BrandColors.coral}>{errors.password}</AppText>}
          </View>
          
          <View>
            <AppText variant="label">Phone (optional)</AppText>
            <TextInput
              style={{
                padding: 12,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: errors.phone ? BrandColors.coral : theme.textSecondary + '40',
                color: theme.text,
                marginTop: 4,
                backgroundColor: theme.background,
              }}
              value={phone}
              onChangeText={(text) => { setPhone(text); clearError('phone'); }}
              placeholder="Enter phone number"
              placeholderTextColor={theme.textSecondary}
              keyboardType="phone-pad"
              maxLength={20}
            />
            {errors.phone && <AppText variant="caption" color={BrandColors.coral}>{errors.phone}</AppText>}
          </View>
          
          {userRole === 'ADMIN' && schools && (
            <View>
              <AppText variant="label">School *</AppText>
              <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
                {schools.map((school) => (
                  <Pressable
                    key={school.school_id}
                    onPress={() => { setSelectedSchoolId(school.school_id); clearError('school'); }}
                    style={{
                      paddingHorizontal: 12,
                      paddingVertical: 8,
                      borderRadius: 16,
                      backgroundColor: selectedSchoolId === school.school_id ? BrandColors.coral : theme.backgroundElement,
                      borderWidth: 1,
                      borderColor: selectedSchoolId === school.school_id ? BrandColors.coral : theme.textSecondary + '40',
                    }}
                  >
                    <AppText color={selectedSchoolId === school.school_id ? '#fff' : theme.text}>{school.school_name}</AppText>
                  </Pressable>
                ))}
              </View>
              {errors.school && <AppText variant="caption" color={BrandColors.coral}>{errors.school}</AppText>}
            </View>
          )}
          
          <View style={{ gap: 12, marginTop: 16 }}>
            <Button label={isLoading ? 'Creating...' : 'Create Teacher'} onPress={handleSubmit} isLoading={isLoading} />
            <Button label="Cancel" variant="ghost" onPress={() => router.back()} disabled={isLoading} />
          </View>
        </View>
      </ScrollView>
    </ScreenTemplate>
  );
}
