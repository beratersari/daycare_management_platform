import type { UserRole } from '@/store/api/authApi';

/**
 * Form values for the registration form.
 */
export interface RegisterFormValues {
  /** User's first name */
  first_name: string;
  /** User's last name */
  last_name: string;
  /** User's email address */
  email: string;
  /** User's password */
  password: string;
  /** Selected user role */
  role: UserRole;
  /** Numeric school ID entered by the user; null for ADMIN role */
  school_id: number | null;
}

/**
 * Props for the RegisterForm component.
 */
export interface RegisterFormProps {
  /** Callback invoked when the form is submitted with valid data */
  onSubmit: (values: RegisterFormValues) => void;
  /** Whether the form is in a loading/submission state */
  isLoading: boolean;
  /** Optional error message to display at the top of the form */
  errorMessage?: string | null;
}
