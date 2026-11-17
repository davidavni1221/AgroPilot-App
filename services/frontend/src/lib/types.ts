export type Farm = { id: string; name: string };

export type Crop = {
  id: string;
  name: string;
  kc_ini: number;
  kc_mid: number;
  kc_end: number;
  l_ini: number;
  l_dev: number;
  l_mid: number;
  l_late: number;
  root_depth_m: number;
};

export type Soil = { id: string; name: string; available_water_mm_per_m: number };

export type Emitter = { id: string; name: string; flow_lph: number };

export type NewCrop = Omit<Crop, "id">;

export type NewPlot = {
  farm_id: string;
  name: string;
  area_m2: number;
  crop_id: string;
  planting_date: string;
  soil_id: string;
  row_spacing_m: number;
  emitter_spacing_m: number;
  emitter_id: string;
  lat: number;
  lon: number;
};

export type Plot = {
  id: string;
  farm_id: string;
  name: string;
  area_m2: number;
  crop_id: string;
};

export type PlanDay = {
  date: string;
  et0_mm: number;
  rain_mm: number;
  kc: number;
  etc_mm: number;
  need_mm: number;
  litres: number;
  run_minutes: number;
  bucket_end_mm: number;
  stale: boolean;
};

export type Plan = {
  plot_id: string;
  crop_id: string;
  bucket_capacity_mm: number;
  stale: boolean;
  days: PlanDay[];
};
