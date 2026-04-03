import { createContext, useCallback, useContext, useEffect, useMemo, useState, type PropsWithChildren } from "react";

import { ApiError, login as loginRequest } from "./api";

const STORAGE_KEY = "nba-oracle-token";

type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  login: (password: string) => Promise<void>;
  logout: () => void;
  handleAuthError: (error: unknown) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [token, setToken] = useState<string | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) {
      setToken(stored);
    }
    setIsHydrated(true);
  }, []);

  const logout = useCallback(() => {
    window.localStorage.removeItem(STORAGE_KEY);
    setToken(null);
  }, []);

  const login = useCallback(async (password: string) => {
    const payload = await loginRequest(password);
    window.localStorage.setItem(STORAGE_KEY, payload.access_token);
    setToken(payload.access_token);
  }, []);

  const handleAuthError = useCallback(
    (error: unknown) => {
      if (error instanceof ApiError && error.status === 401) {
        logout();
      }
    },
    [logout],
  );

  const value = useMemo<AuthContextValue>(
    () => ({ token, isAuthenticated: Boolean(token), isHydrated, login, logout, handleAuthError }),
    [handleAuthError, isHydrated, login, logout, token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
