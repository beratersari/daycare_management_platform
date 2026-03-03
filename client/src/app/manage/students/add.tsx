import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { View, ScrollView, TextInput, Pressable, Platform } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { PageHeader } from '@/components/molecules/page-header';
import { AlertBanner } from '@/components/molecules/alert-banner';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { useCreateStudentMutation } from '@/store/api/studentApi';
import { useListSchoolsQuery } from '@/store/api/schoolApi';
import { BrandColors } from '@/constants/theme';

// Validation helpers
const validateName = (name: string, fieldName: string): { valid: boolean; error?: string } => {
  if (!name.trim()) return { valid: false, error: `${fieldName} is required` };
  if (name.trim().length < 2) return { valid: false, error: `${fieldName} must be at least 2 characters` };
  if (name.trim().length > 50) return { valid: false, error: `${fieldName} must be less than 50 characters` };
  if (!/^[a-zA-Z\s'-]+$/.test(name.trim())) return { valid: false, error: `${fieldName} contains invalid characters` };
  return { valid: true };
};

const validateDateOfBirth = (dob: string): { valid: boolean; error?: string } => {
  if (!dob.trim()) return { valid: false, error: 'Date of birth is required' };
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!dateRegex.test(dob.trim())) return { valid: false, error: 'Date must be in YYYY-MM-DD format' };
  const date = new Date(dob);
  if (isNaN(date.getTime())) return { valid: false, error: 'Invalid date' };
  const today = new Date();
  if (date > today) return { valid: false, error: 'Date of birth cannot be in the future' };
  const minDate = new Date();
  minDate.setFullYear(minDate.getFullYear() - 18);
  if (date < minDate) return { valid: false, error: 'Student cannot be older than 18 years' };
  return { valid: true };
};

export default function AddStudentScreen() {
  const router = useRouter();
  const theme = useTheme();
  const user = useAppSelector(selectCurrentUser);
  const userRole = user?.role;
  const canManage = userRole === 'ADMIN' || userRole === 'DIRECTOR';
  
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [selectedSchoolId, setSelectedSchoolId] = useState<number | null>(user?.school_id || null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  
  const { data: schools } = useListSchoolsQuery(undefined, { skip: userRole !== 'ADMIN' });
  const [createStudent, { isLoading }] = useCreateStudentMutation();
  
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    const firstNameResult = validateName(firstName, 'First name');
    if (!firstNameResult.valid) newErrors.firstName = firstNameResult.error!;
    
    const lastNameResult = validateName(lastName, 'Last name');
    if (!lastNameResult.valid) newErrors.lastName = lastNameResult.error!;
    
    const dobResult = validateDateOfBirth(dateOfBirth);
    if (!dobResult.valid) newErrors.dateOfBirth = dobResult.error!;
    
    if (!selectedSchoolId) newErrors.school = 'Please select a school';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async () => {
    setSubmitError(null);
    if (!validate()) return;
    
    try {
      await createStudent({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        school_id: selectedSchoolId!,
        date_of_birth: dateOfBirth,
      }).unwrap();
      router.back();
    } catch (error: any) {
      setSubmitError(error?.data?.detail || 'Failed to create student');
    }
  };
  
  const clearError = (field: string) => setErrors((prev) => { const n = { ...prev }; delete n[field]; return n; });
  
  if (!canManage) {
    return (
      <ScreenTemplate header={<PageHeader title="Add Student" onBack={() => router.back()} />}>
        <AlertBanner type="error" message="You don't have permission to add students." />
      </ScreenTemplate>
    );
  }
  
  return (
    <ScreenTemplate header={<PageHeader title="Add New Student" onBack={() => router.back()} />}>
      <ScrollView showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled">
        {submitError && <AlertBanner type="error" message={submitError} onDismiss={() => setSubmitError(null)} />}
        
        <View style={{ gap: 16, padding: 16 }}>
          <View>
            <AppText variant="label">First Name *</AppText>
            <TextInput
              style={{ padding: 12, borderRadius: 8, borderWidth: 1, borderColor: errors.firstName ? BrandColors.coral : theme.textSecondary + '40', color: theme.text, marginTop: 4, backgroundColor: theme.background }}
              value={firstName}
              onChangeText={(t) => { setFirstName(t); clearError('firstName'); }}
              placeholder="Enter first name"
              placeholderTextColor={theme.textSecondary}
              maxLength={50}
            />
            {errors.firstName && <AppText variant="caption" color={BrandColors.coral}>{errors.firstName}</AppText>}
          </View>
          
          <View>
            <AppText variant="label">Last Name *</AppText>
            <TextInput
              style={{ padding: 12, borderRadius: 8, borderWidth: 1, borderColor: errors.lastName ? BrandColors.coral : theme.textSecondary + '40', color: theme.text, marginTop: 4, backgroundColor: theme.background }}
              value={lastName}
              onChangeText={(t) => { setLastName(t); clearError('lastName'); }}
              placeholder="Enter last name"
              placeholderTextColor={theme.textSecondary}
              maxLength={50}
            />
            {errors.lastName && <AppText variant="caption" color={BrandColors.coral}>{errors.lastName}</AppText>}
          </View>
          
          <View>
            <AppText variant="label">Date of Birth *</AppText>
            {Platform.OS === 'web' ? (
              <input
                type="date"
                value={dateOfBirth}
                onChange={(e) => { setDateOfBirth(e.target.value); clearError('dateOfBirth'); }}
                style={{ padding: 12, borderRadius: 8, borderWidth: 1, fontSize: 16, marginTop: 4, width: '100%', borderColor: errors.dateOfBirth ? '#FF6B6B' : '#ccc' }}
                max={new Date().toISOString().split('T')[0]}
              />
            ) : (
              <TextInput
                style={{ padding: 12, borderRadius: 8, borderWidth: 1, borderColor: errors.dateOfBirth ? BrandColors.coral : theme.textSecondary + '40', color: theme.text, marginTop: 4, backgroundColor: theme.background }}
                value={dateOfBirth}
                onChangeText={(t) => { setDateOfBirth(t); clearError('dateOfBirth'); }}
                placeholder="YYYY-MM-DD"
                placeholderTextColor={theme.textSecondary}
                maxLength={10}
              />
            )}
            {errors.dateOfBirth && <AppText variant="caption" color={BrandColors.coral}>{errors.dateOfBirth}</AppText>}
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
            <Button label={isLoading ? 'Creating...' : 'Create Student'} onPress={handleSubmit} isLoading={isLoading} />
            <Button label="Cancel" variant="ghost" onPress={() => router.back()} disabled={isLoading} />
          </View>
        </View>
      </ScrollView>
    </ScreenTemplate>
  );
}
