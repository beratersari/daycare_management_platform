/**
 * Meal Menu Management Screen
 * Role-based functionality:
 * - ADMIN/DIRECTOR/TEACHER: Can create, edit, delete meal menus
 * - PARENT/STUDENT: Can only view meal menus
 */
import { useRouter } from 'expo-router';
import React, { useState, useMemo } from 'react';
import { ScrollView, StyleSheet, View, Pressable, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import DateTimePicker from '@react-native-community/datetimepicker';

import { AppText } from '@/components/atoms/AppText';
import { Button } from '@/components/atoms/Button';
import { Skeleton } from '@/components/atoms/Skeleton';
import { AppTextInput } from '@/components/atoms/TextInput';
import { InfoCard } from '@/components/molecules/InfoCard';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import {
  useListMealMenusQuery,
  useGetMealMenusBySchoolQuery,
  useCreateMealMenuMutation,
  useDeleteMealMenuMutation,
  type MealMenuResponse,
} from '@/store/api/mealMenuApi';
import { useGetTeacherClassesQuery } from '@/store/api/teacherApi';
import { useListSchoolsQuery } from '@/store/api/schoolApi';
import { BrandColors } from '@/constants/theme';

export default function MealMenusScreen() {
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  const user = useAppSelector(selectCurrentUser);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedSchoolId, setSelectedSchoolId] = useState<number | undefined>(user?.school_id || undefined);

  const userRole = user?.role;
  const canEdit = userRole === 'ADMIN' || userRole === 'DIRECTOR' || userRole === 'TEACHER';

  // Fetch schools for ADMIN selection
  const { data: schools } = useListSchoolsQuery(undefined, {
    skip: userRole !== 'ADMIN',
  });

  // Set default school for ADMIN if schools are loaded
  React.useEffect(() => {
    if (userRole === 'ADMIN' && schools && schools.length > 0 && !selectedSchoolId) {
      setSelectedSchoolId(schools[0].school_id);
    }
  }, [schools, userRole, selectedSchoolId]);

  // Fetch meal menus based on selected school or all for admin
  const { data: allMenus, isLoading: isLoadingAll } = useListMealMenusQuery();
  const { data: schoolMenus, isLoading: isLoadingSchool } = useGetMealMenusBySchoolQuery(
    selectedSchoolId || 0,
    { skip: !selectedSchoolId }
  );
  
  const { data: teacherClasses } = useGetTeacherClassesQuery(user?.user_id || 0, {
    skip: !user?.user_id || userRole !== 'TEACHER',
  });

  const [createMealMenu, { isLoading: isCreating }] = useCreateMealMenuMutation();
  const [deleteMealMenu, { isLoading: isDeleting }] = useDeleteMealMenuMutation();

  const isLoading = isLoadingAll || (selectedSchoolId && isLoadingSchool);

  // Filter menus for the selected date
  const dateStr = selectedDate.toISOString().split('T')[0];
  const menusForDate = useMemo(() => {
    const menus = schoolMenus || allMenus || [];
    return menus.filter((menu) => menu.menu_date === dateStr && !menu.is_deleted);
  }, [schoolMenus, allMenus, dateStr]);

  const handleDateChange = (event: any, date?: Date) => {
    setShowDatePicker(false);
    if (date) {
      setSelectedDate(date);
    }
  };

  const handleCreateMenu = async (menuData: {
    breakfast: string;
    lunch: string;
    dinner: string;
    classId?: number;
  }) => {
    const targetSchoolId = selectedSchoolId || user?.school_id;
    if (!targetSchoolId) {
      console.error('No school ID available for creating meal menu');
      return;
    }
    
    try {
      await createMealMenu({
        school_id: targetSchoolId,
        class_id: menuData.classId || null,
        menu_date: dateStr,
        breakfast: menuData.breakfast || null,
        lunch: menuData.lunch || null,
        dinner: menuData.dinner || null,
      }).unwrap();
      setShowCreateForm(false);
    } catch (error) {
      console.error('Failed to create meal menu:', error);
    }
  };

  const handleDeleteMenu = async (menuId: number) => {
    try {
      await deleteMealMenu(menuId).unwrap();
    } catch (error) {
      console.error('Failed to delete meal menu:', error);
    }
  };

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: theme.background }]} edges={['top', 'bottom']}>
      <View style={styles.header}>
        <Button label={t('common.back')} onPress={() => router.back()} variant="ghost" style={styles.backButton} />
        <AppText variant="heading" style={styles.headerTitle}>
          {t('dashboard.mealMenus')}
        </AppText>
        <View style={{ width: 60 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* School Selector (for ADMIN only) */}
        {userRole === 'ADMIN' && schools && schools.length > 0 && (
          <View style={styles.section}>
            <AppText variant="label" color={theme.textSecondary}>
              Select School
            </AppText>
            <View style={styles.selectorRow}>
              {schools.map((school) => (
                <Pressable
                  key={school.school_id}
                  onPress={() => setSelectedSchoolId(school.school_id)}
                  style={[
                    styles.selectorButton,
                    selectedSchoolId === school.school_id && { backgroundColor: BrandColors.coral },
                  ]}>
                  <AppText
                    variant="caption"
                    color={selectedSchoolId === school.school_id ? '#fff' : theme.text}>
                    {school.school_name}
                  </AppText>
                </Pressable>
              ))}
            </View>
          </View>
        )}

        {/* Date Selector */}
        <View style={styles.dateSection}>
          <AppText variant="label" color={theme.textSecondary}>
            Select Date
          </AppText>
          {Platform.OS === 'web' ? (
            <input
              type="date"
              value={dateStr}
              onChange={(e) => setSelectedDate(new Date(e.target.value))}
              style={{
                padding: 12,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: theme.backgroundElement,
                backgroundColor: theme.backgroundElement,
                color: theme.text,
                fontSize: 16,
                outline: 'none',
              } as any}
            />
          ) : (
            <>
              <Pressable
                onPress={() => setShowDatePicker(true)}
                style={[styles.dateButton, { backgroundColor: theme.backgroundElement }]}>
                <AppText variant="body">{dateStr}</AppText>
              </Pressable>
              {showDatePicker && (
                <DateTimePicker
                  value={selectedDate}
                  mode="date"
                  display="default"
                  onChange={handleDateChange}
                />
              )}
            </>
          )}
        </View>

        {/* Create Button (for ADMIN/DIRECTOR/TEACHER only) */}
        {canEdit && (
          <Button
            label={showCreateForm ? 'Cancel' : 'Add Meal Menu'}
            onPress={() => setShowCreateForm(!showCreateForm)}
            variant={showCreateForm ? 'secondary' : 'primary'}
            style={styles.createButton}
          />
        )}

        {/* Create Form */}
        {showCreateForm && canEdit && (
          <MealMenuCreateForm
            onSubmit={handleCreateMenu}
            isLoading={isCreating}
            teacherClasses={teacherClasses}
            userRole={userRole}
          />
        )}

        {/* Meal Menus List */}
        <View style={styles.listSection}>
          <AppText variant="label" color={theme.textSecondary}>
            Meal Menus for {dateStr}
          </AppText>

          {isLoading ? (
            <View style={{ gap: 12 }}>
              <Skeleton width="100%" height={120} borderRadius={16} />
              <Skeleton width="100%" height={120} borderRadius={16} />
            </View>
          ) : menusForDate.length > 0 ? (
            menusForDate.map((menu) => (
              <MealMenuCard
                key={menu.menu_id}
                menu={menu}
                canEdit={canEdit}
                onDelete={() => handleDeleteMenu(menu.menu_id)}
                isDeleting={isDeleting}
              />
            ))
          ) : (
            <InfoCard title="No meal menu found" subtitle={`No menu available for ${dateStr}`} />
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function MealMenuCard({
  menu,
  canEdit,
  onDelete,
  isDeleting,
}: {
  menu: MealMenuResponse;
  canEdit: boolean;
  onDelete: () => void;
  isDeleting: boolean;
}) {
  const theme = useTheme();

  return (
    <InfoCard
      title={menu.class_id ? `Class Menu #${menu.class_id}` : 'School-wide Menu'}
      subtitle={`Date: ${menu.menu_date}`}>
      <View style={styles.mealDetails}>
        {menu.breakfast && (
          <View style={styles.mealRow}>
            <AppText variant="caption" color={BrandColors.coral} style={styles.mealLabel}>
              Breakfast:
            </AppText>
            <AppText variant="body" style={styles.mealValue}>
              {menu.breakfast}
            </AppText>
          </View>
        )}
        {menu.lunch && (
          <View style={styles.mealRow}>
            <AppText variant="caption" color={BrandColors.orange} style={styles.mealLabel}>
              Lunch:
            </AppText>
            <AppText variant="body" style={styles.mealValue}>
              {menu.lunch}
            </AppText>
          </View>
        )}
        {menu.dinner && (
          <View style={styles.mealRow}>
            <AppText variant="caption" color={BrandColors.teal} style={styles.mealLabel}>
              Dinner:
            </AppText>
            <AppText variant="body" style={styles.mealValue}>
              {menu.dinner}
            </AppText>
          </View>
        )}
      </View>
      {canEdit && (
        <View style={styles.actionRow}>
          <Button
            label="Delete"
            onPress={onDelete}
            variant="secondary"
            isLoading={isDeleting}
            style={styles.deleteButton}
          />
        </View>
      )}
    </InfoCard>
  );
}

function MealMenuCreateForm({
  onSubmit,
  isLoading,
  teacherClasses,
  userRole,
}: {
  onSubmit: (data: { breakfast: string; lunch: string; dinner: string; classId?: number }) => void;
  isLoading: boolean;
  teacherClasses?: { class_id: number; class_name: string }[];
  userRole?: string;
}) {
  const theme = useTheme();
  const [breakfast, setBreakfast] = useState('');
  const [lunch, setLunch] = useState('');
  const [dinner, setDinner] = useState('');
  const [selectedClassId, setSelectedClassId] = useState<number | undefined>(undefined);

  const handleSubmit = () => {
    onSubmit({ breakfast, lunch, dinner, classId: selectedClassId });
    setBreakfast('');
    setLunch('');
    setDinner('');
    setSelectedClassId(undefined);
  };

  return (
    <View style={[styles.formContainer, { backgroundColor: theme.backgroundElement }]}>
      <AppText variant="subheading" style={styles.formTitle}>
        Create New Meal Menu
      </AppText>

      {/* Class Selection (for teachers who have assigned classes) */}
      {userRole === 'TEACHER' && teacherClasses && teacherClasses.length > 0 && (
        <View style={styles.inputGroup}>
          <AppText variant="caption" color={theme.textSecondary}>
            Class (optional - leave empty for school-wide)
          </AppText>
          <View style={styles.classButtons}>
            <Pressable
              onPress={() => setSelectedClassId(undefined)}
              style={[
                styles.classButton,
                selectedClassId === undefined && { backgroundColor: BrandColors.coral },
              ]}>
              <AppText
                variant="caption"
                color={selectedClassId === undefined ? '#fff' : theme.text}>
                School-wide
              </AppText>
            </Pressable>
            {teacherClasses.map((cls) => (
              <Pressable
                key={cls.class_id}
                onPress={() => setSelectedClassId(cls.class_id)}
                style={[
                  styles.classButton,
                  selectedClassId === cls.class_id && { backgroundColor: BrandColors.coral },
                ]}>
                <AppText
                  variant="caption"
                  color={selectedClassId === cls.class_id ? '#fff' : theme.text}>
                  {cls.class_name}
                </AppText>
              </Pressable>
            ))}
          </View>
        </View>
      )}

      <AppTextInput
        label="Breakfast"
        value={breakfast}
        onChangeText={setBreakfast}
        placeholder="Enter breakfast menu"
      />

      <AppTextInput
        label="Lunch"
        value={lunch}
        onChangeText={setLunch}
        placeholder="Enter lunch menu"
      />

      <AppTextInput
        label="Dinner"
        value={dinner}
        onChangeText={setDinner}
        placeholder="Enter dinner menu"
      />

      <Button label="Create Menu" onPress={handleSubmit} isLoading={isLoading} />
    </View>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backButton: {
    height: 40,
    width: 60,
    paddingHorizontal: 0,
  },
  headerTitle: {
    textAlign: 'center',
  },
  content: {
    padding: 24,
    gap: 16,
  },
  dateSection: {
    gap: 8,
  },
  dateButton: {
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  createButton: {
    marginTop: 8,
  },
  listSection: {
    gap: 12,
    marginTop: 8,
  },
  mealDetails: {
    gap: 8,
    marginTop: 8,
  },
  mealRow: {
    flexDirection: 'row',
    gap: 8,
  },
  mealLabel: {
    fontWeight: '600',
    minWidth: 70,
  },
  mealValue: {
    flex: 1,
  },
  actionRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 12,
  },
  deleteButton: {
    minWidth: 80,
  },
  formContainer: {
    padding: 16,
    borderRadius: 16,
    gap: 12,
  },
  formTitle: {
    marginBottom: 8,
  },
  classButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  classButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
});
