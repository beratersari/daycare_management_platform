import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  wrapper: {
    gap: 6,
    alignSelf: 'stretch',
  },
  label: {
    marginLeft: 2,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1.5,
    paddingHorizontal: 16,
    height: 52,
  },
  input: {
    flex: 1,
    fontSize: 15,
    fontWeight: '400',
  },
  toggle: {
    paddingLeft: 12,
  },
  errorText: {
    marginLeft: 2,
  },
});
