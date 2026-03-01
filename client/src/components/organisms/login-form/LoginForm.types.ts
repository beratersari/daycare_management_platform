/**
 * Form values for the login form.
 */
export interface LoginFormValues {
  /** User's email address */
  email: string;
  /** User's password */
  password: string;
}

/**
 * Props for the LoginForm component.
 */
export interface LoginFormProps {
  /** Callback invoked when the form is submitted with valid data */
  onSubmit: (values: LoginFormValues) => void;
  /** Whether the form is in a loading/submission state */
  isLoading: boolean;
  /** Optional error message to display at the top of the form */
  errorMessage?: string | null;
}
