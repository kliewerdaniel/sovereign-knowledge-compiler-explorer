// Server-only loaders: used by server components to prerender at build time.
// Reads the static JSON from public/curriculum via fs (no fetch at build, no API).
import type { Concept, GraphView, LearningPath, Misconception } from "./types";

const BASE = "public/curriculum";

async function loadJson<T>(file: string): Promise<T> {
  const fs = await import("fs");
  const path = await import("path");
  const p = path.join(process.cwd(), BASE, file);
  const text = fs.readFileSync(p, "utf-8");
  return JSON.parse(text) as T;
}

export function getConceptStore(): Promise<Record<string, Concept>> {
  return loadJson<Record<string, Concept>>("concept-store.json");
}

export function getConceptViews(): Promise<Record<string, GraphView>> {
  return Promise.resolve({} as Record<string, GraphView>);
}

export function getLearningPaths(): Promise<Record<string, LearningPath>> {
  return loadJson<Record<string, LearningPath>>("learning-paths.json").catch(() => ({} as Record<string, LearningPath>));
}

export function getSearchIndex(): Promise<{ inverted: Record<string, string[]>; titles: Record<string, string> }> {
  return loadJson<{ inverted: Record<string, string[]>; titles: Record<string, string> }>("search-index.json");
}

export function getMisconceptions(): Promise<Misconception[]> {
  return loadJson<{ misconceptions: Misconception[] }>("graph-views/misconception-map.json")
    .then((d) => d.misconceptions || [])
    .catch(() => []);
}

export function getStats(): Promise<any> {
  return loadJson<any>("stats.json").catch(() => null);
}

export { sourceHref, sourceLabel } from "./types";
