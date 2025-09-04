import type { Meta, StoryObj } from '@storybook/react';
import ProtectedRoute from './ProtectedRoute';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import React from 'react';

const meta: Meta<typeof ProtectedRoute> = {
  title: 'Auth/ProtectedRoute',
  component: ProtectedRoute,
};

export default meta;
type Story = StoryObj<typeof ProtectedRoute>;

const ProtectedContent = () => <div>Protected content</div>;
const Login = () => <div>Login page</div>;

export const Authenticated: Story = {
  render: () => {
    // Prime store with authenticated state
    useAuthStore.setState({
      isAuthenticated: true,
      user: { id: 1, username: 'demo', email: 'demo@acme.test', full_name: 'Demo User', role: 'admin' },
      token: 'test',
      isLoading: false,
    } as any);
    return (
      <MemoryRouter initialEntries={["/secure"]}>
        <Routes>
          <Route path="/secure" element={<ProtectedRoute><ProtectedContent /></ProtectedRoute>} />
        </Routes>
      </MemoryRouter>
    );
  },
};

export const Unauthenticated: Story = {
  render: () => {
    useAuthStore.setState({ isAuthenticated: false, user: null, token: null, isLoading: false } as any);
    return (
      <MemoryRouter initialEntries={["/secure"]}>
        <Routes>
          <Route path="/secure" element={<ProtectedRoute><ProtectedContent /></ProtectedRoute>} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </MemoryRouter>
    );
  },
};

