/**
 * Styles for ParentClassView component
 */
import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  sectionTitle: {
    marginBottom: 12,
    marginTop: 8,
  },
  
  // Child Card
  childCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  childHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  childAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F26076',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  childInfo: {
    flex: 1,
  },
  className: {
    fontWeight: '600',
  },
  classDetails: {
    flexDirection: 'row',
    gap: 16,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  
  // Child Banner
  childBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    padding: 16,
    backgroundColor: '#fef2f2',
    borderRadius: 12,
    marginBottom: 16,
  },
  childBannerAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F26076',
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // Info Card
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  infoRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 16,
  },
  infoItem: {
    flex: 1,
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    gap: 4,
  },
  capacityInfo: {
    marginTop: 8,
  },
  capacityBar: {
    height: 6,
    backgroundColor: '#e5e7eb',
    borderRadius: 3,
    marginTop: 8,
    overflow: 'hidden',
  },
  capacityFill: {
    height: '100%',
    backgroundColor: '#22c55e',
    borderRadius: 3,
  },
  
  // Section
  section: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  
  // Teacher Card
  teacherCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#f3f4f6',
  },
  teacherAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#458B73',
    justifyContent: 'center',
    alignItems: 'center',
  },
  teacherInfo: {
    flex: 1,
  },
  
  // Classmates Grid
  classmatesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
  },
  classmateItem: {
    alignItems: 'center',
    width: 80,
  },
  myChildItem: {
    backgroundColor: '#fef2f2',
    borderRadius: 12,
    padding: 8,
  },
  classmateAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  classmateName: {
    textAlign: 'center',
  },
  myChildName: {
    fontWeight: '600',
    color: '#dc2626',
  },
  
  // Empty Card
  emptyCard: {
    padding: 24,
    alignItems: 'center',
    backgroundColor: '#f9fafb',
    borderRadius: 12,
  },
  
  // Contact Card
  contactCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    padding: 16,
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    marginTop: 8,
  },
});
