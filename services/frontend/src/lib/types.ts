export type Farm = { id: string; name: string };

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
