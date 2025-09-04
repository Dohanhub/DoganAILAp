import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from './authStore';

describe('authStore', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, token: null, isAuthenticated: false, isLoading: false } as any);
  });

  it('has initial unauthenticated state', () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
  });

  it('logout clears auth state', () => {
    useAuthStore.setState({ token: 't', user: { id: 1 } as any, isAuthenticated: true } as any);
    useAuthStore.getState().logout();
    const s = useAuthStore.getState();
    expect(s.isAuthenticated).toBe(false);
    expect(s.user).toBeNull();
    expect(s.token).toBeNull();
  });

  it('checkAuth enables auth when token present', () => {
    useAuthStore.setState({ token: 't', isAuthenticated: false } as any);
    useAuthStore.getState().checkAuth();
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
  });
});

