import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    gap: 20,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 32,
  },
  section: {
    gap: 12,
  },
  sectionLabel: {
    marginBottom: 4,
    fontSize: 13,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 10,
  },
  classDetails: {
    marginTop: 4,
  },
  allergyContainer: {
    marginTop: 4,
  },
});
