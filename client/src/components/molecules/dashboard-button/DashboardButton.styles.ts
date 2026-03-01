import { StyleSheet } from 'react-native';
import { BrandColors } from '@/constants/theme';
import { ButtonColorVariant } from './DashboardButton.types';

/**
 * Maps color variants to their corresponding brand colors.
 */
export const VARIANT_COLORS: Record<ButtonColorVariant, string> = {
  coral: BrandColors.coral,
  orange: BrandColors.orange,
  yellow: BrandColors.yellow,
  teal: BrandColors.teal,
};

export const styles = StyleSheet.create({
  container: {
    borderRadius: 16,
    paddingVertical: 12,
    paddingHorizontal: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 72,
    flex: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 4,
    elevation: 3,
  },
  pressed: {
    opacity: 0.85,
    transform: [{ scale: 0.97 }],
  },
  disabled: {
    opacity: 0.5,
  },
  icon: {
    marginBottom: 4,
  },
  label: {
    textAlign: 'center',
    fontWeight: '600',
    fontSize: 13,
  },
});
