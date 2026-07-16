// Shared types for the SKCE curriculum artifact.
export interface ConceptContract {
  what_is_it: string;
  why_exists: string;
  where_appears: string[];
  prerequisites: string[];
  dependencies: string[];
  related_concepts: string[];
  mathematical_foundations: string[];
  historical_evolution: string;
  implementation_details: string;
  source_references: { kind: string; ref: string; quote?: string }[];
}

export interface Concept {
  id: string;
  kind: string;
  title: string;
  aliases: string[];
  summary: string;
  abstraction_level: number;
  confidence: number;
  source: string;
  tags: string[];
  source_refs: { kind: string; ref: string; quote?: string }[];
  prerequisite_ids: string[];
  dependency_ids: string[];
  related_ids: string[];
  foundation_links: { foundationId: string; bridge: string }[];
  misconception_ids: string[];
  contract: ConceptContract;
}

export interface Edge {
  source: string;
  target: string;
  type: string;
  weight: number;
  confidence: number;
}

export interface GraphView {
  nodes: { id: string; title: string; kind: string; abstraction_level: number; confidence: number; source: string }[];
  edges: Edge[];
  misconceptions?: any[];
  kinds?: Record<string, string[]>;
}

export interface LearningPath {
  id: string;
  name: string;
  ordered_concept_ids: string[];
  estimated_depth: number;
  difficulty: string;
}

export interface Misconception {
  id: string;
  concept_id: string;
  misconception: string;
  correction: string;
  confidence: number;
  source: string;
}

// Source ref -> human link
export function sourceHref(ref: string): string | null {
  if (ref.startsWith("blog:")) {
    return `https://www.danielkliewer.com/blog/${ref.slice(5)}`;
  }
  if (ref.startsWith("source:") || ref.startsWith("spec:")) {
    return `https://github.com/kliewerdaniel/sovereign-knowledge-compiler-explorer/blob/main/corpus/${ref.replace(":", "/")}`;
  }
  return null;
}

export function sourceLabel(ref: string): string {
  if (ref.startsWith("blog:")) return "blog";
  if (ref.startsWith("source:")) return "source";
  if (ref.startsWith("spec:")) return "spec";
  return ref.split(":")[0];
}
