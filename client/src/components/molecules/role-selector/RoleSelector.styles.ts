import { StyleSheet } from 'react-native';
import { BrandColors } from '@/constants/theme';

/** Primary brand color for selected segment */
const PRIMARY_COLOR = BrandColors.coral;

export const styles = StyleSheet.create({
  wrapper: {
    gap: 6,
    alignSelf: 'stretch',
  },
  label: {
    marginLeft: 2,
  },
  track: {
    flexDirection: 'row',
    borderRadius: 12,
    padding: 4,
    gap: 4,
  },
  segment: {
    flex: 1,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 9,
  },
  segmentFirst: {
    borderTopLeftRadius: 9,
    borderBottomLeftRadius: 9,
  },
  segmentLast: {
    borderTopRightRadius: 9,
    borderBottomRightRadius: 9,
  },
  segmentSelected: {
    backgroundColor: PRIMARY_COLOR,
  },
  segmentDisabled: {
    opacity: 0.5,
  },
  segmentLabel: {
    fontWeight: '500',
  },
  segmentLabelSelected: {
    fontWeight: '700',
  },
});
