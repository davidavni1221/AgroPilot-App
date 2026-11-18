/**
 * The plots that came with the database (seed_registry.sh and seed_postgres.py). The farmer's home page shows only these.
 * Anything added through the app is kept in the registry as usual, but is seen on the admin page only.
 * There is no login and no owner in the registry yet, so this list stands in for "the plots of the farmer who is looking".
 */
export const SEEDED_PLOT_IDS: ReadonlySet<string> = new Set([
  "c8f3d1b0-4d2e-5a1b-8b22-1d6e3f702002",
  "d9a4e2c1-5e3f-4b6a-9c33-2e7f4a803003",
  "e0b5f3d2-6f40-4c7b-8d44-3f8a5b914004",
  "f1c6a4e3-7051-4d8c-9e55-4a9b6c025005",
]);
