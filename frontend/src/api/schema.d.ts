/**
 * Placeholder for the GENERATED OpenAPI types.
 *
 * Run `npm run gen:api` with the backend running to overwrite this file with
 * types derived from http://localhost:8000/openapi.json. Hand-maintained types
 * below are a temporary stand-in so the app type-checks before generation.
 */
export interface KitOut {
  kit_id: string;
  status: string;
  complete: boolean;
}

export interface ReservationOut {
  reservation_id: string;
  status:
    | "PENDING"
    | "CONFIRMED"
    | "ACTIVE"
    | "COMPLETED"
    | "REROUTED"
    | "CANCELLED"
    | "NO_SHOW"
    | "EXPIRED";
  effective_start: string;
  effective_end: string;
}
