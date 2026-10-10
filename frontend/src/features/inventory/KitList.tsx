import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/api/client";
import type { KitOut } from "@/api/schema";

export function KitList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["kits"],
    queryFn: () => apiGet<KitOut[]>("/kits"),
  });

  if (isLoading) return <p>Loading kits…</p>;
  if (error) return <p style={{ color: "crimson" }}>Failed to load kits.</p>;
  if (!data?.length) return <p>No kits yet.</p>;

  return (
    <table style={{ borderCollapse: "collapse", width: "100%" }}>
      <thead>
        <tr>
          <th style={cell}>Kit</th>
          <th style={cell}>Status</th>
          <th style={cell}>Complete</th>
        </tr>
      </thead>
      <tbody>
        {data.map((k) => (
          <tr key={k.kit_id}>
            <td style={cell}>{k.kit_id}</td>
            <td style={cell}>{k.status}</td>
            <td style={cell}>{k.complete ? "yes" : "no"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const cell: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};
