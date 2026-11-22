import { getJson, type Result } from "./services";
import type { Plan } from "./types";

export const getPlan = (plotId: string): Promise<Result<Plan>> =>
  getJson("planner", `/v1/plots/${encodeURIComponent(plotId)}/plan?days=7`);
