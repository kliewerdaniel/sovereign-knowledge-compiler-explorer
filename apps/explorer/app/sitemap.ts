import type { MetadataRoute } from "next";
import { promises as fs } from "fs";
import path from "path";

const BASE = "https://skce-explorer.vercel.app";

// Enumerate every statically prerendered page so crawlers/agents can discover
// the full corpus without JS or guessing URLs.
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const urls: MetadataRoute.Sitemap = [
    { url: `${BASE}/` },
    { url: `${BASE}/graph/` },
    { url: `${BASE}/paths/` },
    { url: `${BASE}/search/` },
    { url: `${BASE}/about/` },
    { url: `${BASE}/sitemap.xml` },
    { url: `${BASE}/llms.txt` },
    { url: `${BASE}/concept-store.json` },
  ];

  try {
    const p = path.join(process.cwd(), "public", "curriculum", "concept-store.json");
    const raw = await fs.readFile(p, "utf-8");
    const store = JSON.parse(raw) as Record<string, unknown>;
    for (const id of Object.keys(store)) {
      urls.push({ url: `${BASE}/concept/${id}/` });
    }
  } catch {
    // concept-store not present at build time; section pages still enumerated.
  }

  return urls;
}
