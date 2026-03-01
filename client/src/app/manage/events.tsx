/**
 * Events Screen
 *
 * Family-friendly events page showing events relevant to the current user.
 * - Students see events from their enrolled classes
 * - Parents see events from their children's classes
 * - Teachers see events from their assigned classes
 * - Admins/Directors see all events (with school filtering for admins)
 */
import { useRouter } from 'expo-router';
import React, { useMemo, useState, useEffect } from 'react';
import { View, FlatList, RefreshControl, Pressable, Platform, StyleSheet } from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { AppTextInput } from '@/components/atoms/text-input';
import { PageHeader } from '@/components/molecules/page-header';
import { EmptyState } from '@/components/molecules/empty-state';
import { EventCard } from '@/components/molecules/event-card';
import { LoadingState } from '@/components/molecules/loading-state';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useLocalization } from '@/hooks/use-localization';
import { useTheme } from '@/hooks/use-theme';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import {
  useGetMyEventsQuery,
  useCreateClassEventMutation,
  useListClassesQuery,
  type ClassEventResponse,
  type ClassEventCreateRequest,
} from '@/store/api/classApi';
import { useGetTeacherClassesQuery } from '@/store/api/teacherApi';
import { useListSchoolsQuery } from '@/store/api/schoolApi';
import { BrandColors } from '@/constants/theme';

const CLASS_PAGE_SIZE = 100;

export default function EventsScreen() {
  const router = useRouter();
  const { t } = useLocalization();
  const theme = useTheme();
  const user = useAppSelector(selectCurrentUser);
  const userRole = user?.role;
  const canCreate = userRole === 'ADMIN' || userRole === 'DIRECTOR' || userRole === 'TEACHER';

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedSchoolId, setSelectedSchoolId] = useState<number | undefined>(user?.school_id || undefined);
  const [selectedClassId, setSelectedClassId] = useState<number | undefined>(undefined);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [photoUrl, setPhotoUrl] = useState('');
  const [eventDate, setEventDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);

  const { data: events, isLoading, error, refetch } = useGetMyEventsQuery();
  const [createEvent, { isLoading: isCreating }] = useCreateClassEventMutation();

  const { data: schools } = useListSchoolsQuery(undefined, {
    skip: userRole !== 'ADMIN',
  });

  const { data: teacherClasses } = useGetTeacherClassesQuery(user?.user_id || 0, {
    skip: !user?.user_id || userRole !== 'TEACHER',
  });

  const { data: classesData } = useListClassesQuery(
    { page: 1, pageSize: CLASS_PAGE_SIZE },
    { skip: !canCreate || userRole === 'TEACHER' }
  );

  useEffect(() => {
    if (userRole === 'ADMIN' && schools && schools.length > 0 && !selectedSchoolId) {
      setSelectedSchoolId(schools[0].school_id);
      setSelectedClassId(undefined);
    }
  }, [schools, userRole, selectedSchoolId]);

  useEffect(() => {
    setSelectedClassId(undefined);
  }, [selectedSchoolId]);

  const classes = useMemo(() => {
    if (userRole === 'TEACHER') return teacherClasses || [];
    const list = classesData?.data || [];
    if (userRole === 'DIRECTOR' && user?.school_id) {
      return list.filter((cls) => cls.school_id === user.school_id);
    }
    if (userRole === 'ADMIN') {
      if (selectedSchoolId) {
        return list.filter((cls) => cls.school_id === selectedSchoolId);
      }
      return list;
    }
    return list;
  }, [classesData, teacherClasses, userRole, selectedSchoolId, user?.school_id]);

  const classMap = useMemo(() => {
    const map = new Map<number, number>();
    (classesData?.data || []).forEach((cls) => {
      map.set(cls.class_id, cls.school_id);
    });
    return map;
  }, [classesData]);

  const filteredEvents = useMemo(() => {
    if (!events) return [];
    if (userRole === 'ADMIN' && selectedSchoolId) {
      return events.filter((event) => classMap.get(event.class_id) === selectedSchoolId);
    }
    if (userRole === 'DIRECTOR' && user?.school_id) {
      return events.filter((event) => classMap.get(event.class_id) === user.school_id);
    }
    return events;
  }, [events, classMap, selectedSchoolId, userRole, user?.school_id]);

  const handleDateChange = (_event: unknown, date?: Date) => {
    setShowDatePicker(false);
    if (date) setEventDate(date);
  };

  const handleCreateEvent = async () => {
    if (!selectedClassId) return;
    const payload: ClassEventCreateRequest = {
      title: title.trim(),
      description: description.trim() || undefined,
      photo_url: photoUrl.trim() || undefined,
      event_date: eventDate.toISOString(),
    };

    try {
      await createEvent({ classId: selectedClassId, data: payload }).unwrap();
      setShowCreateForm(false);
      setTitle('');
      setDescription('');
      setPhotoUrl('');
      setSelectedClassId(undefined);
      refetch();
    } catch (err) {
      console.error('Failed to create event:', err);
    }
  };

  const renderEvent = ({ item }: { item: ClassEventResponse }) => (
    <EventCard
      title={item.title}
      eventDate={item.event_date}
      className={item.class_name}
      description={item.description}
      photoUrl={item.photo_url}
    />
  );

  const renderContent = () => {
    if (isLoading) {
      return <LoadingState cardCount={4} cardHeight={200} />;
    }

    if (error) {
      return (
        <EmptyState
          icon="alert-circle"
          message={t('common.error')}
          subtitle={t('common.retry')}
        />
      );
    }

    if (!filteredEvents || filteredEvents.length === 0) {
      return (
        <EmptyState
          emoji="🎉"
          message={t('events.noEvents')}
          subtitle={t('events.noEventsSubtitle')}
        />
      );
    }

    return (
      <FlatList
        data={filteredEvents}
        keyExtractor={(item) => item.event_id.toString()}
        renderItem={renderEvent}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={refetch}
            tintColor={theme.primary}
          />
        }
      />
    );
  };

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('events.title')}
          onBack={() => router.back()}
        />
      }
    >
      {userRole === 'ADMIN' && schools && schools.length > 0 ? (
        <View style={styles.section}>
          <AppText variant="label" color={theme.textSecondary}>
            {t('events.selectSchool')}
          </AppText>
          <View style={styles.selectorRow}>
            {schools.map((school) => (
              <Pressable
                key={school.school_id}
                onPress={() => setSelectedSchoolId(school.school_id)}
                style={[
                  styles.selectorButton,
                  selectedSchoolId === school.school_id && { backgroundColor: BrandColors.coral },
                ]}
              >
                <AppText
                  variant="caption"
                  color={selectedSchoolId === school.school_id ? '#fff' : theme.text}
                >
                  {school.school_name}
                </AppText>
              </Pressable>
            ))}
          </View>
        </View>
      ) : null}

      {canCreate ? (
        <Button
          label={showCreateForm ? t('common.cancel') : t('events.createEvent')}
          onPress={() => setShowCreateForm(!showCreateForm)}
          variant={showCreateForm ? 'secondary' : 'primary'}
          style={styles.createButton}
        />
      ) : null}

      {showCreateForm && canCreate ? (
        <View style={[styles.formContainer, { backgroundColor: theme.backgroundElement }]}
          >
          <AppText variant="subheading" style={styles.formTitle}>
            {t('events.createEvent')}
          </AppText>

          <View style={styles.inputGroup}>
            <AppText variant="caption" color={theme.textSecondary}>
              {t('events.selectClass')}
            </AppText>
            {classes.length > 0 ? (
              <View style={styles.selectorRow}>
                {classes.map((cls) => (
                  <Pressable
                    key={cls.class_id}
                    onPress={() => setSelectedClassId(cls.class_id)}
                    style={[
                      styles.selectorButton,
                      selectedClassId === cls.class_id && { backgroundColor: BrandColors.coral },
                    ]}
                  >
                    <AppText
                      variant="caption"
                      color={selectedClassId === cls.class_id ? '#fff' : theme.text}
                    >
                      {cls.class_name}
                    </AppText>
                  </Pressable>
                ))}
              </View>
            ) : (
              <View style={[styles.emptyClassCard, { backgroundColor: theme.backgroundElement }]}
                >
                <AppText variant="caption" color={theme.textSecondary}>
                  {t('events.noClassesAvailable')}
                </AppText>
              </View>
            )}
          </View>

          <AppTextInput
            label={t('events.eventTitle')}
            value={title}
            onChangeText={setTitle}
            placeholder="Field Trip to the Zoo"
          />

          <AppTextInput
            label={t('events.eventDescription')}
            value={description}
            onChangeText={setDescription}
            placeholder={t('events.eventDescription')}
            multiline
            numberOfLines={4}
            style={styles.textArea}
            textAlignVertical="top"
          />

          <AppTextInput
            label={t('events.eventPhoto')}
            value={photoUrl}
            onChangeText={setPhotoUrl}
            placeholder="https://example.com/photo.jpg"
          />

          <View style={styles.inputGroup}>
            <AppText variant="label" color={theme.textSecondary}>
              {t('events.eventDate')}
            </AppText>
            {Platform.OS === 'web' ? (
              <input
                type="datetime-local"
                value={eventDate.toISOString().slice(0, 16)}
                onChange={(e) => setEventDate(new Date(e.target.value))}
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
                  style={[styles.dateButton, { backgroundColor: theme.backgroundElement }]}
                >
                  <AppText variant="body">{eventDate.toLocaleString()}</AppText>
                </Pressable>
                {showDatePicker && (
                  <DateTimePicker
                    value={eventDate}
                    mode="datetime"
                    display="default"
                    onChange={handleDateChange}
                  />
                )}
              </>
            )}
          </View>

          <Button
            label={t('events.createEvent')}
            onPress={handleCreateEvent}
            isLoading={isCreating}
            disabled={!selectedClassId || !title.trim() || isCreating}
          />
        </View>
      ) : null}

      {renderContent()}
    </ScreenTemplate>
  );
}

const styles = StyleSheet.create({
  listContent: {
    paddingBottom: 24,
  },
  section: {
    gap: 8,
  },
  selectorRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  selectorButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  createButton: {
    marginTop: 8,
  },
  formContainer: {
    padding: 16,
    borderRadius: 16,
    gap: 12,
    marginBottom: 12,
  },
  formTitle: {
    marginBottom: 8,
  },
  inputGroup: {
    gap: 8,
  },
  dateButton: {
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  textArea: {
    minHeight: 120,
    textAlignVertical: 'top',
    paddingVertical: 12,
    paddingTop: 12,
  },
  emptyClassCard: {
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#ddd',
  },
});

