export type Club = {
  name: string;
  monogram: string;
  shape: "circle" | "square" | "hex";
};

/** Invented but believable campus clubs that share a kit on the relay. */
export const CLUBS: Club[] = [
  { name: "Meridian Film Society", monogram: "M", shape: "hex" },
  { name: "Vanguard Robotics", monogram: "V", shape: "square" },
  { name: "Thornwood Drama Guild", monogram: "T", shape: "circle" },
  { name: "Halcyon A/V Collective", monogram: "H", shape: "square" },
  { name: "Northgate Debate Union", monogram: "N", shape: "hex" },
  { name: "Kestrel Photography Club", monogram: "K", shape: "circle" },
];
