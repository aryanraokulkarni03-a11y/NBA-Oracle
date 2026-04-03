import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";

export function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const destination = (location.state as { from?: string } | null)?.from ?? "/";

  if (isAuthenticated) {
    return <Navigate to={destination} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await login(password);
      navigate(destination, { replace: true });
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught.message);
      } else if (caught instanceof Error) {
        setError(caught.message);
      } else {
        setError("unknown_error");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-screen__ambient login-screen__ambient--left" />
      <div className="login-screen__ambient login-screen__ambient--right" />
      <form className="login-card" onSubmit={handleSubmit}>
        <p className="eyebrow">Phase 4B</p>
        <h1>NBA Oracle</h1>
        <p className="login-card__copy">
          Sign in to inspect live slate state, provider health, stability, learning, and operator workflows.
        </p>
        <label className="field">
          <span>Operator password</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your dashboard password"
            autoComplete="current-password"
            required
          />
        </label>
        {error ? <div className="inline-error">{error}</div> : null}
        <button type="submit" className="button button--primary button--block" disabled={isSubmitting}>
          {isSubmitting ? "Signing in…" : "Enter dashboard"}
        </button>
      </form>
    </div>
  );
}
