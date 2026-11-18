// All calls to the backend services live in src/lib. They run on the server only: the browser never calls a service.

export type ServiceName = "registry" | "weather" | "planner";

const ENV_NAMES: Record<ServiceName, string> = {
  registry: "REGISTRY_URL",
  weather: "WEATHER_URL",
  planner: "PLANNER_URL",
};

// The planner may wait for the weather-service, which retries its provider, so it gets more time.
const TIMEOUT_MS: Record<ServiceName, number> = { registry: 5000, weather: 5000, planner: 30000 };

export type Failure = {
  ok: false;
  service: ServiceName;
  // "not-found" is a 404 from the service. The others are things to show to the user.
  kind: "config" | "unreachable" | "timeout" | "problem" | "invalid" | "not-found";
  status?: number;
  detail: string;
};

export type Result<T> = { ok: true; data: T } | Failure;

export const serviceLabel: Record<ServiceName, string> = {
  registry: "registry-service",
  weather: "weather-service",
  planner: "planner-service",
};

/** One plain sentence for the user. Never a stack trace. */
export function describeFailure(failure: Failure): string {
  const name = serviceLabel[failure.service];
  switch (failure.kind) {
    case "config":
      return failure.detail;
    case "unreachable":
      return `${name} is not reachable.`;
    case "timeout":
      return `${name} did not answer in time.`;
    case "invalid":
      return `${name} sent an answer this page cannot read.`;
    case "not-found":
      return "Not found.";
    default:
      return failure.detail;
  }
}

function fail(service: ServiceName, kind: Failure["kind"], detail: string, status?: number): Failure {
  return { ok: false, service, kind, detail, status };
}

async function requestJson<T>(
  service: ServiceName,
  path: string,
  init?: { method: "POST" | "PATCH" | "DELETE"; body?: unknown },
): Promise<Result<T>> {
  const base = process.env[ENV_NAMES[service]];
  if (!base) {
    return fail(service, "config", `${ENV_NAMES[service]} is not set. Copy .env.example to .env.local.`);
  }

  let response: Response;
  try {
    response = await fetch(new URL(path, base), {
      cache: "no-store",
      signal: AbortSignal.timeout(TIMEOUT_MS[service]),
      ...(init
        ? {
            method: init.method,
            ...(init.body === undefined
              ? {}
              : { headers: { "content-type": "application/json" }, body: JSON.stringify(init.body) }),
          }
        : {}),
    });
  } catch (error) {
    const timedOut = error instanceof Error && (error.name === "TimeoutError" || error.name === "AbortError");
    return timedOut ? fail(service, "timeout", "timeout") : fail(service, "unreachable", "unreachable");
  }

  if (response.status === 204) return { ok: true, data: null as T };

  let answer: unknown;
  try {
    answer = await response.json();
  } catch {
    return response.ok
      ? fail(service, "invalid", "The answer is not JSON.", response.status)
      : fail(service, "problem", `${serviceLabel[service]} answered with status ${response.status}.`, response.status);
  }

  if (response.status === 404) return fail(service, "not-found", "Not found.", 404);
  if (!response.ok) {
    const detail = (answer as { detail?: unknown })?.detail;
    return fail(
      service,
      "problem",
      typeof detail === "string" ? detail : `${serviceLabel[service]} answered with status ${response.status}.`,
      response.status,
    );
  }
  return { ok: true, data: answer as T };
}

export const getJson = <T>(service: ServiceName, path: string): Promise<Result<T>> => requestJson<T>(service, path);

/** POST a JSON body. A 409 or 422 comes back as a "problem" failure whose detail is the service's own sentence. */
export const postJson = <T>(service: ServiceName, path: string, body: unknown): Promise<Result<T>> =>
  requestJson<T>(service, path, { method: "POST", body });

/** PATCH a JSON body. A 404 means it is gone; a 409 or 422 comes back as a "problem" with the service's own sentence. */
export const patchJson = <T>(service: ServiceName, path: string, body: unknown): Promise<Result<T>> =>
  requestJson<T>(service, path, { method: "PATCH", body });

/** DELETE. Success is a 204 with no body. A 404 means it is already gone; a 409 comes back with the service's own sentence. */
export const deleteResource = (service: ServiceName, path: string): Promise<Result<null>> =>
  requestJson<null>(service, path, { method: "DELETE" });

export type ServiceStatus = { service: ServiceName; up: boolean };

/** GET /health on each service. A service that does not answer is down. */
export async function getServiceStatuses(): Promise<ServiceStatus[]> {
  const names: ServiceName[] = ["registry", "weather", "planner"];
  return Promise.all(
    names.map(async (service) => {
      const result = await getJson<{ status?: string }>(service, "/health");
      return { service, up: result.ok && result.data.status === "ok" };
    }),
  );
}
