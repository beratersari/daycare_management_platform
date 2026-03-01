import type { UserRole } from '@/store/api/authApi';

/**
 * Props for the RoleSelector component.
 */
export interface RoleSelectorProps {
  /** The currently selected role */
  value: UserRole;
  /** Callback invoked when a role is selected */
  onChange: (role: UserRole) => void;
  /** Whether the selector is disabled. Defaults to false */
  disabled?: boolean;
  /** Override which roles appear as options. Defaults to SELECTABLE_ROLES (TEACHER, PARENT) */
  roles?: UserRole[];
}
