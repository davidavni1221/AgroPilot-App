import { deleteResource, getJson, patchJson, postJson, type Result } from "./services";
import type { Crop, Emitter, Farm, NewCrop, NewPlot, Plot, PlotChanges, Soil } from "./types";

export const getFarms = (): Promise<Result<Farm[]>> => getJson("registry", "/v1/farms");
export const getFarm = (id: string): Promise<Result<Farm>> =>
  getJson("registry", `/v1/farms/${encodeURIComponent(id)}`);
export const getPlots = (): Promise<Result<Plot[]>> => getJson("registry", "/v1/plots");
export const getPlot = (id: string): Promise<Result<Plot>> =>
  getJson("registry", `/v1/plots/${encodeURIComponent(id)}`);
export const getCrops = (): Promise<Result<Crop[]>> => getJson("registry", "/v1/crops");
export const getSoils = (): Promise<Result<Soil[]>> => getJson("registry", "/v1/soils");
export const getEmitters = (): Promise<Result<Emitter[]>> => getJson("registry", "/v1/emitters");

export const createFarm = (name: string): Promise<Result<Farm>> => postJson("registry", "/v1/farms", { name });
export const createCrop = (crop: NewCrop): Promise<Result<Crop>> => postJson("registry", "/v1/crops", crop);
export const createPlot = (plot: NewPlot): Promise<Result<Plot>> => postJson("registry", "/v1/plots", plot);
export const updateFarm = (id: string, name: string): Promise<Result<Farm>> =>
  patchJson("registry", `/v1/farms/${encodeURIComponent(id)}`, { name });
export const updatePlot = (id: string, changes: PlotChanges): Promise<Result<Plot>> =>
  patchJson("registry", `/v1/plots/${encodeURIComponent(id)}`, changes);

export const deleteFarm = (id: string): Promise<Result<null>> => deleteResource("registry", `/v1/farms/${encodeURIComponent(id)}`);
export const deletePlot = (id: string): Promise<Result<null>> => deleteResource("registry", `/v1/plots/${encodeURIComponent(id)}`);
