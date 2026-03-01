import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  listContent: {
    paddingBottom: 24,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 32,
  },
  headerContainer: {
    gap: 16,
    marginBottom: 8,
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
  childDetails: {
    marginTop: 8,
    gap: 4,
  },
  allergyContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  activeItem: {
    opacity: 0.7,
  },
  pressedItem: {
    opacity: 0.9,
  },
});
