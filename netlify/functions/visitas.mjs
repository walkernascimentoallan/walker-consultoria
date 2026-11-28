import { getStore } from "@netlify/blobs";

export default async (req) => {
  const store = getStore("contador");
  const url = new URL(req.url);
  let n = Number(await store.get("visitas")) || 0;
  if (url.searchParams.get("inc") === "1" && req.method === "POST") {
    n += 1;
    await store.set("visitas", String(n));
  }
  return new Response(JSON.stringify({ visitas: n }), {
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
};

export const config = { path: "/api/visitas" };
