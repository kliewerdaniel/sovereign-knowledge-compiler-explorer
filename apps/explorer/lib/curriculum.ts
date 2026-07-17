// Browser-only loaders: used by client components ("use client"). Fetch the
// static JSON at runtime. No server fs, no API, no inference. See docs/STATIC_ARTIFACTS.md.
import type { Concept, GraphView, LearningPath, Misconception, Edge } from "./types";

const BASE = "/curriculum";

async function loadJson<T>(file: string): Promise<T> {
  const res = await fetch(`${BASE}/${file}`);
  if (!res.ok) throw new Error(`missing ${file}`);
  return res.json();
}

export function getConceptStore(): Promise<Record<string, Concept>> {
  return loadJson<Record<string, Concept>>("concept-store.json");
}

export async function getConceptViews(): Promise<Record<string, GraphView>> {
  // Only the four views the Graph page actually renders. Each is normalized to a
  // {nodes, edges} shape so a malformed/missing artifact can never crash the page
  // (the previous ontology crash was an {kinds:{}} payload with no `nodes`).
  const keys = ["concept-graph", "prerequisite-graph", "decision-graph", "ontology-graph"];
  const out: Record<string, GraphView> = {};
  await Promise.all(
    keys.map(async (k) => {
      try {
        const v = await loadJson<any>(`graph-views/${k}.json`);
        out[k] = { nodes: v.nodes || [], edges: v.edges || [] } as GraphView;
      } catch {
        out[k] = { nodes: [], edges: [] } as GraphView;
      }
    })
  );
  return out;
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
