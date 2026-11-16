import { getJson, type Result } from "./services";
import type { Farm, Plot } from "./types";

export const getFarms = (): Promise<Result<Farm[]>> => getJson("registry", "/v1/farms");
export const getPlots = (): Promise<Result<Plot[]>> => getJson("registry", "/v1/plots");
export const getPlot = (id: string): Promise<Result<Plot>> =>
  getJson("registry", `/v1/plots/${encodeURIComponent(id)}`);
