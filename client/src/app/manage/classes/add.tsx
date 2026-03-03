/**
 * Add Class Page
 *
 * Dedicated page for admins and directors to add new classes to the system.
 */
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { View, ScrollView, TextInput, Pressable } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { PageHeader } from '@/components/molecules/page-header';
import { AlertBanner } from '@/components/molecules/alert-banner';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useTheme } from '@/hooks/use-theme';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { useListSchoolsQuery } from '@/store/api/schoolApi';
import { useCreateClassMutation } from '@/store/api/classApi';
import { BrandColors } from '@/constants/theme';

// Validation helpers
const validateClassName = (name: string): { valid: boolean; error?: string } => {
  if (!name.trim()) return { valid: false, error: 'Class name is required' };
  if (name.trim().length < 2) return { valid: false, error: 'Class name must be at least 2 characters' };
  if (name.trim().length > 100) return { valid: false, error: 'Class name must be less than 100 characters' };
  return { valid: true };
};

const validateCapacity = (capacity: string): { valid: boolean; error?: string } => {
  if (!capacity.trim()) return { valid: false, error: 'Capacity is required' };
  const num = parseInt(capacity, 10);
  if (isNaN(num)) return { valid: false, error: 'Capacity must be a number' };
  if (num < 1) return { valid: false, error: 'Capacity must be at least 1' };
  if (num > 200) return { valid: false, error: 'Capacity cannot exceed 200' };
  return { valid: true };
};

const validateRoomNumber = (room: string): { valid: boolean; error?: string } => {
  if (!room.trim()) return { valid: true }; // Optional
  if (room.trim().length > 20) return { valid: false, error: 'Room number must be less than 20 characters' };
  if (!/^[\w\s-]+$/.test(room.trim())) return { valid: false, error: 'Room number contains invalid characters' };
  return { valid: true };
};

const validateSchedule = (schedule: string): { valid: boolean; error?: string } => {
  if (!schedule.trim()) return { valid: true }; // Optional
  if (schedule.trim().length > 200) return { valid: false, error: 'Schedule must be less than 200 characters' };
  return { valid: true };
};

export default function AddClassScreen() {
  const router = useRouter();
  const theme = useTheme();
  const user = useAppSelector(selectCurrentUser);
  const userRole = user?.role;
  const canManage = userRole === 'ADMIN' || userRole === 'DIRECTOR';
  
  const [className, setClassName] = useState('');
  const [capacity, setCapacity] = useState('');
  const [roomNumber, setRoomNumber] = useState('');
  const [schedule, setSchedule] = useState('');
  const [selectedSchoolId, setSelectedSchoolId] = useState<number | null>(user?.school_id || null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  
  const { data: schools } = useListSchoolsQuery(undefined, { skip: userRole !== 'ADMIN' });
  const [createClass, { isLoading }] = useCreateClassMutation();
  
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    const classNameResult = validateClassName(className);
    if (!classNameResult.valid) newErrors.className = classNameResult.error!;
    
    const capacityResult = validateCapacity(capacity);
    if (!capacityResult.valid) newErrors.capacity = capacityResult.error!;
    
    const roomResult = validateRoomNumber(roomNumber);
    if (!roomResult.valid) newErrors.roomNumber = roomResult.error!;
    
    const scheduleResult = validateSchedule(schedule);
    if (!scheduleResult.valid) newErrors.schedule = scheduleResult.error!;
    
    if (!selectedSchoolId) newErrors.school = 'Please select a school';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async () => {
    setSubmitError(null);
    if (!validate()) return;
    
    try {
      await createClass({
        class_name: className.trim(),
        school_id: selectedSchoolId!,
        capacity: parseInt(capacity, 10),
        room_number: roomNumber.trim() || null,
        schedule: schedule.trim() || null,
      }).unwrap();
      router.back();
    } catch (error: any) {
      setSubmitError(error?.data?.detail || 'Failed to create class');
    }
  };
  
  const clearError = (field: string) => setErrors((prev) => { const n = { ...prev }; delete n[field]; return n; });
  
  if (!canManage) {
    return (
      <ScreenTemplate header={<PageHeader title="Add Class" onBack={() => router.back()} />}>
        <AlertBanner type="error" message="You don't have permission to add classes." />
      </ScreenTemplate>
    );
  }
  
  return (
    <ScreenTemplate header={<PageHeader title="Add New Class" onBack={() => router.back()} />}>
      <ScrollView showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled">
        {submitError && <AlertBanner type="error" message={submitError} onDismiss={() => setSubmitError(null)} />}
        
        <View style={{ gap: 16, padding: 16 }}>
          <View>
            <AppText variant="label">Class Name *</AppText>
            <TextInput
              style={{ padding: 12, borderRadius: 8, borderWidth: 1, borderColor: errors.className ? BrandColors.coral : theme.textSecondary + '40', color: theme.text, marginTop: 4, backgroundColor: theme.background }}
              value={className}
              onChangeText={(t) => { setClassName(t); clearError('className'); }}
              placeholder="e.g., Sunshine Toddlers"
              placeholderTextColor={theme.textSecondary}
              maxLength={100}
            />
            {errors.className && <AppText variant="caption" color={BrandColors.coral}>{errors.className}</AppText>}
          </View>
          
          <View>
            <AppText variant="label">Capacity *</AppText>
            <TextInput
              style={{ padding: 12, borderRadius: 8, borderWidth: 1, borderColor: errors.capacity ? BrandColors.coral : theme.textSecondary + '40', color: theme.text, marginTop: 4, backgroundColor: theme.background }}
              value={capacity}
              onChangeText={(t) => { setCapacity(t.replace(/[^0-9]/g, '')); clearError('capacity'); }}
              placeholder="Maximum number of students (1-200)"
              placeholderTextColor={theme.textSecondary}
              keyboardType="numeric"
              maxLength={3}
            />
            {errors.capacity && <AppText variant="caption" color={BrandColors.coral}>{errors.capacity}</AppText>}
          </View>
          
          <View>
            <AppText variant="label">Room Number (optional)</AppText>
            <TextInput
              style={{ padding: 12, borderRadius: 8, borderWidth: 1, borderColor: errors.roomNumber ? BrandColors.coral : theme.textSecondary + '40', color: theme.text, marginTop: 4, backgroundColor: theme.background }}
              value={roomNumber}
              onChangeText={(t) => { setRoomNumber(t); clearError('roomNumber'); }}
              placeholder="e.g., Room 101"
              placeholderTextColor={theme.textSecondary}
              maxLength={20}
            />
            {errors.roomNumber && <AppText variant="caption" color={BrandColors.coral}>{errors.roomNumber}</AppText>}
          </View>
          
          <View>
            <AppText variant="label">Schedule (optional)</AppText>
            <TextInput
              style={{ padding: 12, borderRadius: 8, borderWidth: 1, borderColor: errors.schedule ? BrandColors.coral : theme.textSecondary + '40', color: theme.text, marginTop: 4, backgroundColor: theme.background }}
              value={schedule}
              onChangeText={(t) => { setSchedule(t); clearError('schedule'); }}
              placeholder="e.g., Mon-Fri 9:00 AM - 3:00 PM"
              placeholderTextColor={theme.textSecondary}
              maxLength={200}
            />
            {errors.schedule && <AppText variant="caption" color={BrandColors.coral}>{errors.schedule}</AppText>}
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
            <Button label={isLoading ? 'Creating...' : 'Create Class'} onPress={handleSubmit} isLoading={isLoading} />
            <Button label="Cancel" variant="ghost" onPress={() => router.back()} disabled={isLoading} />
          </View>
        </View>
      </ScrollView>
    </ScreenTemplate>
  );
}
