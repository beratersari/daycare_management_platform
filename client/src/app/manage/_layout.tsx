import { Stack } from 'expo-router';
import React from 'react';

export default function ManageLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
      }}
    />
  );
}
