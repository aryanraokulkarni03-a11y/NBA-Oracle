import type {
  ApiErrorPayload,
  AuthLoginResponse,
  HealthSnapshot,
  LearningOperatorResponse,
  LearningResponse,
  OperatorLiveSlateResponse,
  OperatorSchedulerResponse,
  OutcomeResponse,
  PickHistoryResponse,
  ProvidersHealthResponse,
  StabilityResponse,
  TodayResponse,
} from "./types";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

type JsonBody = Record<string, unknown> | undefined;

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() ?? "";

function withApiBase(path: string) {
  if (!API_BASE_URL) {
    return path;
  }
  return `${API_BASE_URL.replace(/\/$/, "")}${path}`;
}

async function request<T>(path: string, init: RequestInit = {}, token?: string | null): Promise<T> {
  const headers = new Headers(init.headers ?? {});
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(withApiBase(path), { ...init, headers });
  const text = await response.text();
  const payload = text ? (JSON.parse(text) as T | ApiErrorPayload) : ({} as T);

  if (!response.ok) {
    const retryAfter = response.headers.get("Retry-After");
    const detail =
      typeof payload === "object" && payload && "detail" in payload && typeof payload.detail === "string"
        ? payload.detail
        : response.status === 429
          ? `rate_limited${retryAfter ? `_retry_after_${retryAfter}s` : ""}`
        : `request_failed_${response.status}`;
    throw new ApiError(response.status, detail);
  }

  return payload as T;
}

function postJson<T>(path: string, body: JsonBody, token?: string | null): Promise<T> {
  return request<T>(
    path,
    {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    },
    token,
  );
}

export function login(password: string) {
  return postJson<AuthLoginResponse>("/api/auth/login", { password });
}

export function getHealth(token: string) {
  return request<HealthSnapshot>("/api/health", {}, token);
}

export function getToday(token: string) {
  return request<TodayResponse>("/api/today", {}, token);
}

export function getPickHistory(token: string, limit = 10) {
  return request<PickHistoryResponse>(`/api/picks/history?limit=${limit}`, {}, token);
}

export function getStability(token: string) {
  return request<StabilityResponse>("/api/stability/latest", {}, token);
}

export function getLearning(token: string) {
  return request<LearningResponse>("/api/learning/status", {}, token);
}

export function getProviders(token: string) {
  return request<ProvidersHealthResponse>("/api/providers/health", {}, token);
}

export function runLiveSlate(token: string, live = true) {
  return postJson<OperatorLiveSlateResponse>("/api/operator/run-live-slate", { live }, token);
}

export function runScheduler(token: string, force = false) {
  return postJson<OperatorSchedulerResponse>("/api/operator/run-scheduler-once", { force }, token);
}

export function runOutcomeGrading(token: string) {
  return postJson<OutcomeResponse>("/api/operator/grade-outcomes", undefined, token);
}

export function runStabilityReview(token: string, forceRefreshBaseline = false) {
  return postJson<StabilityResponse>("/api/operator/review-stability", { force_refresh_baseline: forceRefreshBaseline }, token);
}

export function runLearningReview(token: string) {
  return postJson<LearningOperatorResponse>("/api/operator/run-learning-review", undefined, token);
}
