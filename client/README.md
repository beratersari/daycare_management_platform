# Kinder Tracker - Mobile Client

A React Native mobile application for daycare management, built with Expo and following Atomic Design principles.

## Overview

Kinder Tracker is a comprehensive daycare management platform that enables administrators, teachers, and parents to manage students, classes, events, meal menus, and more. The mobile client provides role-based dashboards and functionality tailored to each user type.

## Features

### Role-Based Access

The application supports multiple user roles, each with specific capabilities:

| Role | Description | Key Features |
|------|-------------|--------------|
| **Admin** | System administrators | Full access to all management tools, cross-school visibility, user management |
| **Director** | School directors | School-wide management, teacher/student/parent management, reports |
| **Teacher** | Classroom teachers | Class management, student attendance, meal menus, announcements |
| **Parent** | Student guardians | View children's information, meal menus, events, announcements |

### Core Functionality

- **Authentication**: Secure login and registration with JWT tokens
- **Dashboard**: Role-specific home screens with quick actions
- **Student Management**: View and manage student profiles, allergies, medical info
- **Class Management**: Create and manage classes, assign teachers
- **Teacher Management**: Manage teacher profiles and class assignments
- **Parent Management**: Link parents to students, manage contact info
- **Meal Menus**: View and manage daily meal menus by school/class
- **Events**: School events and activities calendar
- **Announcements**: School-wide announcements and notifications
- **Reports**: Analytics and reporting (coming soon)

## Tech Stack

- **Framework**: [React Native](https://reactnative.dev/) with [Expo](https://expo.dev/)
- **Navigation**: [expo-router](https://docs.expo.dev/router/introduction/) (file-based routing)
- **State Management**: [Redux Toolkit](https://redux-toolkit.js.org/) + [RTK Query](https://redux-toolkit.js.org/rtk-query/overview)
- **Persistence**: [redux-persist](https://github.com/rt2zz/redux-persist) with AsyncStorage
- **Form Handling**: [React Hook Form](https://react-hook-form.com/) for performant form validation
- **Icons**: [@expo/vector-icons](https://icons.expo.fyi/) (Ionicons icon family)
- **UI Components**: Custom component library following Atomic Design
- **Styling**: React Native StyleSheet with theme support
- **Localization**: Custom i18n implementation

## Project Structure

```
client/
├── app/                    # Expo Router pages (file-based routing)
│   ├── _layout.tsx         # Root layout with providers
│   ├── index.tsx           # Login screen (entry point)
│   ├── dashboard.tsx       # Main dashboard
│   ├── register.tsx        # Registration screen
│   ├── student/
│   │   └── [id].tsx        # Student detail (dynamic route)
│   └── manage/             # Management screens
│       ├── _layout.tsx
│       ├── students.tsx
│       ├── teachers.tsx
│       ├── classes.tsx
│       ├── parents.tsx
│       ├── events.tsx
│       ├── announcements.tsx
│       ├── meal-menus.tsx
│       └── reports.tsx
│
├── components/             # Reusable UI components
│   ├── atoms/              # Basic building blocks
│   │   ├── app-text/
│   │   │   ├── AppText.component.tsx
│   │   │   ├── AppText.styles.ts
│   │   │   ├── AppText.types.ts
│   │   │   └── index.ts
│   │   ├── button/
│   │   ├── icon/
│   │   ├── logo/
│   │   ├── skeleton/
│   │   └── text-input/
│   │
│   ├── molecules/          # Combinations of atoms
│   │   ├── alert-banner/
│   │   │   ├── AlertBanner.component.tsx
│   │   │   ├── AlertBanner.styles.ts
│   │   │   ├── AlertBanner.types.ts
│   │   │   └── index.ts
│   │   ├── dashboard-button/
│   │   ├── empty-state/
│   │   ├── form-field/
│   │   ├── info-card/
│   │   ├── loading-state/
│   │   ├── page-header/
│   │   └── role-selector/
│   │
│   ├── organisms/          # Complex UI sections
│   │   ├── admin-dashboard/
│   │   │   ├── AdminDashboard.component.tsx
│   │   │   ├── AdminDashboard.styles.ts
│   │   │   ├── AdminDashboard.types.ts
│   │   │   └── index.ts
│   │   ├── login-form/
│   │   ├── parent-dashboard/
│   │   ├── register-form/
│   │   ├── role-based-dashboard/
│   │   ├── student-dashboard/
│   │   └── teacher-dashboard/
│   │
│   └── templates/          # Page layouts
│       ├── auth-template/
│       │   ├── AuthTemplate.component.tsx
│       │   ├── AuthTemplate.styles.ts
│       │   ├── AuthTemplate.types.ts
│       │   └── index.ts
│       └── screen-template/
│
├── constants/
│   └── theme.ts            # Design tokens (colors, spacing, fonts)
│
├── hooks/
│   ├── use-theme.ts        # Theme access hook
│   ├── use-localization.ts # Translation hook
│   └── use-color-scheme.ts # System theme detection
│
├── localization/
│   ├── index.ts            # i18n utilities
│   └── en.ts               # English translations
│
├── store/                  # Redux store
│   ├── index.ts            # Store configuration
│   ├── authSlice.ts        # Auth state
│   ├── hooks.ts            # Typed hooks
│   └── api/                # RTK Query APIs
│       ├── authApi.ts
│       ├── studentApi.ts
│       ├── teacherApi.ts
│       ├── parentApi.ts
│       ├── classApi.ts
│       ├── mealMenuApi.ts
│       └── schoolApi.ts
│
└── assets/
    └── images/             # App icons and images
```

## Atomic Design Architecture

This project follows [Atomic Design](https://bradfrost.com/blog/post/atomic-web-design/) principles for component organization:

### Atoms
The smallest, most basic UI building blocks. They serve no functional purpose on their own but are the foundation of all UI.

- **AppText**: Themed text with variants (display, heading, body, caption, label, error)
- **Button**: Pressable button with primary/secondary/ghost variants
- **Icon**: Vector icon wrapper using Ionicons from @expo/vector-icons
- **Skeleton**: Animated loading placeholder
- **TextInput**: Form input with label, error, and secure text toggle (forwardRef for React Hook Form)
- **Logo**: Brand logo component

### Molecules
Simple combinations of atoms that work together as a unit. They have simple functionality and are often reusable.

- **AlertBanner**: Error/success/info message display
- **DashboardButton**: Colored action button with icon
- **EmptyState**: Placeholder for empty data states
- **FormField**: Form input wrapper (re-export of TextInput)
- **InfoCard**: Card component with title, subtitle, and content
- **LoadingState**: Predefined loading skeleton layouts
- **PageHeader**: Consistent page header with back button
- **RoleSelector**: Role selection segmented control

### Organisms
Complex UI sections composed of molecules and atoms. They have specific functionality and business logic.

- **AdminDashboard**: Admin management tools and stats
- **LoginForm**: Complete login form with validation
- **ParentDashboard**: Children list with quick actions
- **RegisterForm**: Registration form with role selection
- **RoleBasedDashboard**: Routes to appropriate dashboard by role
- **StudentDashboard**: Student class view
- **TeacherDashboard**: Teacher classes and students view

### Templates
Page-level layouts that define structure without content. They provide consistent scaffolding for pages.

- **AuthTemplate**: Centered layout for login/register screens
- **ScreenTemplate**: Standard layout with header and scrollable content

### Pages
Actual screens that use templates and populate them with real content. They connect to state and handle navigation.

- Login, Register, Dashboard, Student Detail
- Management screens (Students, Teachers, Classes, Parents, etc.)

## State Management

### Redux Store Structure

```typescript
{
  auth: {
    accessToken: string | null,
    refreshToken: string | null,
    tokenExpiresAt: number | null,
    user: UserResponse | null,
    isHydrating: boolean,
  },
  [api.reducerPath]: RTKQueryState, // For each API
}
```

### RTK Query APIs

Each API module handles a specific domain:

- **authApi**: Login, register, logout, get current user
- **studentApi**: CRUD operations for students
- **teacherApi**: CRUD operations for teachers
- **parentApi**: CRUD operations for parents
- **classApi**: CRUD operations for classes
- **mealMenuApi**: CRUD operations for meal menus
- **schoolApi**: School listing and details

### Persistence

Only authentication state is persisted using `redux-persist` with AsyncStorage. RTK Query cache is intentionally not persisted to ensure fresh data from the server.

## Theming

### Design Tokens

Located in `constants/theme.ts`:

```typescript
// Brand Colors
export const BrandColors = {
  coral: '#F26076',   // Primary accent
  orange: '#FF9760',  // Secondary accent
  yellow: '#FFD150',  // Tertiary accent
  teal: '#458B73',    // Success/action color
};

// Theme Colors (light/dark)
export const Colors = {
  light: { text, background, backgroundElement, ... },
  dark: { text, background, backgroundElement, ... },
};

// Spacing Scale
export const Spacing = {
  half: 2, one: 4, two: 8, three: 16,
  four: 24, five: 32, six: 64,
};
```

### Theme Hook

```typescript
import { useTheme } from '@/hooks/use-theme';

function Component() {
  const theme = useTheme(); // Returns light or dark colors
  return <View style={{ backgroundColor: theme.background }} />;
}
```

## Localization

### Translation Structure

Translations are organized by feature in `localization/en.ts`:

```typescript
export const en = {
  common: { loading, error, retry, cancel, save, ... },
  auth: { signIn, signOut, createAccount, ... },
  dashboard: { title, greeting, manageTeachers, ... },
  roles: { admin, director, teacher, parent, student },
  student: { allergies, dateOfBirth, emergencyContact, ... },
  class: { name, capacity, enrolled, teacher, ... },
  nav: { home, profile, settings, notifications },
};
```

### Usage

```typescript
import { useLocalization } from '@/hooks/use-localization';

function Component() {
  const { t } = useLocalization();
  return <AppText>{t('auth.signIn')}</AppText>;
}

// With interpolation
t('auth.registrationSuccess', { name: 'John' });
```

## Icons

The app uses `@expo/vector-icons` for consistent iconography across platforms. The Icon atom component wraps Ionicons for easy use throughout the app.

### Available Icons

All icons from the Ionicons family are available. Browse the full set at [icons.expo.fyi](https://icons.expo.fyi/).

Common icons used in the app:

| Icon Name | Usage |
|-----------|-------|
| `school` | Teachers, education |
| `happy` | Students, children |
| `library` | Classes, rooms |
| `people` | Parents, groups |
| `bar-chart` | Reports, analytics |
| `megaphone` | Announcements |
| `calendar` | Events, attendance |
| `restaurant` | Meal menus |
| `clipboard` | Attendance, lists |
| `warning` | Allergies, alerts |

### Usage

```typescript
import { Icon, IconName } from '@/components/atoms/icon';

// Basic usage
<Icon name="school" size={24} color="#F26076" />

// In a DashboardButton
<DashboardButton
  label="Manage Teachers"
  icon="school"
  colorVariant="coral"
  onPress={() => router.push('/manage/teachers')}
/>
```

### Type Safety

The Icon component is fully typed. The `IconName` type ensures only valid Ionicons names are accepted:

```typescript
import { IconName } from '@/components/atoms/icon';

const myIcon: IconName = 'school'; // ✓ Valid
const badIcon: IconName = 'invalid-icon'; // ✗ TypeScript error
```

## Form Handling

Forms are built with [React Hook Form](https://react-hook-form.com/) for performant, type-safe form validation.

### Form Components

- **LoginForm**: Email/password login with validation
- **RegisterForm**: Full registration with role selection

### Using Forms with React Hook Form

Forms use the `Controller` component to connect inputs to the form state:

```typescript
import { useForm, Controller } from 'react-hook-form';

interface FormValues {
  email: string;
  password: string;
}

function MyForm() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = (data: FormValues) => {
    console.log(data);
  };

  return (
    <View>
      <Controller
        control={control}
        name="email"
        rules={{
          required: 'Email is required',
          pattern: {
            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Invalid email',
          },
        }}
        render={({ field: { onChange, onBlur, value } }) => (
          <FormField
            label="Email"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            error={errors.email?.message}
          />
        )}
      />
      <Button label="Submit" onPress={handleSubmit(onSubmit)} />
    </View>
  );
}
```

### Validation

Forms use custom validation functions that integrate with the localization system:

```typescript
const validateEmail = (email: string): string | undefined => {
  if (!email.trim()) return t('auth.emailRequired');
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!re.test(email)) return t('auth.emailInvalid');
  return undefined;
};
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (Mac) or Android Emulator

### Installation

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start development server
npm start
```

### Available Scripts

```bash
npm start        # Start Expo dev server
npm run android  # Start on Android
npm run ios      # Start on iOS
npm run web      # Start on web
npm run lint     # Run ESLint
```

### Environment Configuration

The app connects to the backend API. Configure the base URL in `store/api/baseQuery.ts`:

```typescript
const BASE_URL = 'http://localhost:8000/api/v1';
```

## Component Guidelines

### Folder Structure

Each component follows a consistent folder structure:

```
component-name/
├── ComponentName.component.tsx  # Main component implementation
├── ComponentName.styles.ts      # StyleSheet definitions
├── ComponentName.types.ts       # TypeScript interfaces and types
└── index.ts                     # Public exports
```

This structure provides:
- **Separation of concerns**: Logic, styling, and types are cleanly separated
- **Easy navigation**: Clear file naming makes it easy to find what you need
- **Scalability**: Adding new files (tests, stories, etc.) doesn't clutter the codebase

### Creating New Components

1. **Identify the level**: Is it an atom, molecule, organism, or template?
2. **Create the folder**: `components/<level>/component-name/`
3. **Create the files**:
   - `ComponentName.component.tsx` - Main component
   - `ComponentName.styles.ts` - Styles
   - `ComponentName.types.ts` - Types
   - `index.ts` - Exports
4. **Use existing atoms/molecules**: Compose from lower-level components
5. **Follow naming conventions**: PascalCase for components, kebab-case for folders

### Example Component

**ComponentName.types.ts:**
```typescript
export interface ComponentNameProps {
  title: string;
  onPress: () => void;
}
```

**ComponentName.styles.ts:**
```typescript
import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    padding: 16,
    borderRadius: 12,
  },
});
```

**ComponentName.component.tsx:**
```typescript
/**
 * Molecule — ComponentName
 * Brief description of what it does.
 */
import React from 'react';
import { View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { useTheme } from '@/hooks/use-theme';
import { ComponentNameProps } from './ComponentName.types';
import { styles } from './ComponentName.styles';

export function ComponentName({ title, onPress }: ComponentNameProps) {
  const theme = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: theme.backgroundElement }]}>
      <AppText variant="subheading">{title}</AppText>
      <Button label="Action" onPress={onPress} />
    </View>
  );
}
```

**index.ts:**
```typescript
export * from './ComponentName.component';
export * from './ComponentName.types';
```

### Page Template

All management pages follow this pattern:

```typescript
/**
 * PageName Screen
 *
 * Page (Atomic Design):
 * - Uses ScreenTemplate for consistent layout
 * - Uses PageHeader for navigation
 * - Uses appropriate molecules for content
 */
import { useRouter } from 'expo-router';
import React from 'react';

import { PageHeader } from '@/components/molecules/page-header';
import { LoadingState } from '@/components/molecules/loading-state';
import { EmptyState } from '@/components/molecules/empty-state';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useLocalization } from '@/hooks/use-localization';

export default function PageNameScreen() {
  const router = useRouter();
  const { t } = useLocalization();
  const { data, isLoading } = useSomeQuery();

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('page.title')}
          onBack={() => router.back()}
        />
      }>
      {isLoading ? (
        <LoadingState />
      ) : !data?.length ? (
        <EmptyState icon="📋" message="No data" />
      ) : (
        // Render content
      )}
    </ScreenTemplate>
  );
}
```

## Contributing

1. Follow Atomic Design principles for all components
2. Use TypeScript for type safety
3. Write JSDoc comments for all components
4. Test on both iOS and Android
5. Run lint before committing: `npm run lint`

## License

Private - All rights reserved
