import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backButton: {
    height: 40,
    width: 60,
    paddingHorizontal: 0,
  },
  headerTitle: {
    textAlign: 'center',
    flex: 1,
  },
  placeholder: {
    width: 60,
  },
});
