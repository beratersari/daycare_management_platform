/**
 * English translations for the Kinder Tracker app.
 */
export const en = {
  // Common
  common: {
    loading: 'Loading...',
    error: 'An error occurred',
    retry: 'Retry',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    close: 'Close',
    back: 'Back',
    next: 'Next',
    submit: 'Submit',
    search: 'Search',
    noResults: 'No results found',
  },

  // Authentication
  auth: {
    signIn: 'Sign In',
    signOut: 'Sign Out',
    createAccount: 'Create Account',
    email: 'Email',
    password: 'Password',
    confirmPassword: 'Confirm Password',
    firstName: 'First Name',
    lastName: 'Last Name',
    accountType: 'Account Type',
    schoolId: 'School ID',
    forgotPassword: 'Forgot Password?',
    noAccount: "Don't have an account?",
    hasAccount: 'Already have an account?',
    signInToManage: 'Sign in to manage your daycare',
    welcomeBack: 'Welcome back',
    enterCredentials: 'Enter your credentials to continue',
    createOne: 'Create one',
    emailRequired: 'Email is required',
    emailInvalid: 'Please enter a valid email address',
    passwordRequired: 'Password is required',
    passwordMinLength: 'Password must be at least 6 characters',
    passwordMismatch: 'Passwords do not match',
    firstNameRequired: 'First name is required',
    lastNameRequired: 'Last name is required',
    schoolIdRequired: 'School ID is required for your role',
    schoolIdNumber: 'School ID must be a number',
    invalidCredentials: 'Invalid email or password. Please try again.',
    checkFormat: 'Please check your email and password format.',
    serverError: 'Server error. Please try again.',
    cannotReachServer: 'Cannot reach the server. Check your connection.',
    registrationSuccess: 'Account created for {name}! Redirecting to sign in…',
    registrationFailed: 'Registration failed. Please check your details.',
    schoolNotFound: 'School not found. Please check the School ID.',
  },

  // Dashboard
  dashboard: {
    title: 'Dashboard',
    greeting: '👋 Hello,',
    welcomeMessage: 'More features are coming soon. You are successfully authenticated!',
    myChildren: 'My Children',
    myClasses: 'My Classes',
    myStudents: 'My Students',
    managementTools: 'Management Tools',
    manageTeachers: 'Manage Teachers',
    manageStudents: 'Manage Students',
    manageClasses: 'Manage Classes',
    manageParents: 'Manage Parents',
    attendance: 'Attendance',
    events: 'Events',
    mealMenus: 'Meal Menus',
    reports: 'Reports',
    announcements: 'Announcements',
    quickActions: 'Quick Actions',
    viewAll: 'View All',
    noChildren: 'No children linked to your account',
    noClasses: 'No classes assigned to you',
    noStudents: 'No students in your classes',
    childInfo: 'Child Information',
    classInfo: 'Class Information',
    studentInfo: 'Student Information',
  },

  // Roles
  roles: {
    admin: 'Admin',
    director: 'Director',
    teacher: 'Teacher',
    parent: 'Parent',
    student: 'Student',
  },

  // Student details
  student: {
    allergies: 'Allergies',
    noAllergies: 'No known allergies',
    dateOfBirth: 'Date of Birth',
    enrollmentDate: 'Enrollment Date',
    emergencyContact: 'Emergency Contact',
    medicalInfo: 'Medical Information',
  },

  // Class details
  class: {
    name: 'Class Name',
    capacity: 'Capacity',
    enrolled: 'Enrolled',
    teacher: 'Teacher',
    schedule: 'Schedule',
    room: 'Room',
  },

  // Navigation
  nav: {
    home: 'Home',
    profile: 'Profile',
    settings: 'Settings',
    notifications: 'Notifications',
  },
} as const;

export type Translations = typeof en;
