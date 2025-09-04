import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import { useAuthStore } from '../store/authStore';

describe('ProtectedRoute', () => {
  it('renders children when authenticated', () => {
    useAuthStore.setState({ isAuthenticated: true } as any);
    render(
      <MemoryRouter initialEntries={["/secure"]}>
        <Routes>
          <Route path="/secure" element={<ProtectedRoute><div>Secret</div></ProtectedRoute>} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText('Secret')).toBeInTheDocument();
  });
});

