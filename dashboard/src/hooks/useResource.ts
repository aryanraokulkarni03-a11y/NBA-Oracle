import { useCallback, useEffect, useRef, useState, type Dispatch, type SetStateAction } from "react";

import { ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { RUNTIME_REFRESH_EVENT } from "../lib/runtimeSync";

type ResourceState<T> = {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  setData: Dispatch<SetStateAction<T | null>>;
};

export function useResource<T>(loader: (token: string) => Promise<T>, enabled = true): ResourceState<T> {
  const { token, handleAuthError } = useAuth();
  const loaderRef = useRef(loader);
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(enabled);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loaderRef.current = loader;
  }, [loader]);

  const refresh = useCallback(async () => {
    if (!enabled || !token) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const next = await loaderRef.current(token);
      setData(next);
    } catch (caught) {
      handleAuthError(caught);
      if (caught instanceof ApiError) {
        setError(caught.message);
      } else if (caught instanceof Error) {
        setError(caught.message);
      } else {
        setError("unknown_error");
      }
    } finally {
      setIsLoading(false);
    }
  }, [enabled, handleAuthError, token]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    function handleRuntimeRefresh() {
      void refresh();
    }

    window.addEventListener(RUNTIME_REFRESH_EVENT, handleRuntimeRefresh);
    return () => window.removeEventListener(RUNTIME_REFRESH_EVENT, handleRuntimeRefresh);
  }, [refresh]);

  return { data, isLoading, error, refresh, setData };
}
