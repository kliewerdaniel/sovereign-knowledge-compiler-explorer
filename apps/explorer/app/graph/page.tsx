"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { getConceptViews, getConceptStore } from "@/lib/curriculum";

const KIND_COLORS: Record<string, string> = {
  architecture: "#818cf8",
  pass: "#f472b6",
  ir: "#5eead4",
  artifact: "#34d399",
  math: "#fbbf24",
  cs: "#60a5fa",
  concept: "#e6edf3",
  decision: "#a78bfa",
  pattern: "#fb7185",
  limitation: "#94a3b8",
};

type ViewKey = "concept-graph" | "prerequisite-graph" | "decision-graph" | "ontology-graph";

// Deterministic spherical/radial layout (no random seed drift).
function layout(nodes: any[], w: number, h: number) {
  const n = nodes.length;
  const cx = w / 2;
  const cy = h / 2;
  const R = Math.min(w, h) * 0.42;
  const pos: Record<string, [number, number]> = {};
  nodes.forEach((node, i) => {
    if (n === 1) {
      pos[node.id] = [cx, cy];
      return;
    }
    const phi = Math.acos(1 - (2 * (i + 0.5)) / n);
    const theta = Math.PI * (1 + Math.sqrt(5)) * i;
    const r = R * (0.5 + 0.5 * (node.abstraction_level || 0) / 4);
    pos[node.id] = [
      cx + r * Math.sin(phi) * Math.cos(theta),
      cy + r * Math.sin(phi) * Math.sin(theta),
    ];
  });
  return pos;
}

export default function GraphClient() {
  const [view, setView] = useState<ViewKey>("prerequisite-graph");
  const [focus, setFocus] = useState<string | null>(null);
  const [data, setData] = useState<{ nodes: any[]; edges: any[] } | null>(null);
  const [store, setStore] = useState<Record<string, any>>({});

  useEffect(() => {
    getConceptViews().then((views) => setData(views[view] || { nodes: [], edges: [] }));
    getConceptStore().then(setStore);
  }, [view]);

  const W = 900;
  const H = 640;
  const pos = useMemo(() => (data ? layout(data.nodes, W, H) : {}), [data]);

  const focusNeighbors = useMemo(() => {
    if (!focus || !data) return null;
    const set = new Set<string>([focus]);
    for (const e of data.edges) {
      if (e.source === focus) set.add(e.target);
      if (e.target === focus) set.add(e.source);
    }
    return set;
  }, [focus, data]);

  if (!data) return <div>Loading graph…</div>;

  return (
    <div>
      <h1>Knowledge Graph</h1>
      <div className="viewbar">
        {([
          ["prerequisite-graph", "Prerequisite"],
          ["concept-graph", "Concept"],
          ["decision-graph", "Decision"],
          ["ontology-graph", "Ontology"],
        ] as [ViewKey, string][]).map(([k, label]) => (
          <button
            key={k}
            className={view === k ? "active" : ""}
            onClick={() => {
              setView(k);
              setFocus(null);
            }}
          >
            {label}
          </button>
        ))}
      </div>
      <p className="why">
        {view === "prerequisite-graph"
          ? "Directed by prerequisite/dependency/foundation edges. Click a node to focus its neighborhood."
          : view === "concept-graph"
          ? "Concept co-occurrence (related) edges, weighted."
          : view === "decision-graph"
          ? "Design decisions and their rationale/conflicts."
          : "Concepts grouped by ontology kind."}
      </p>

      <div className="graph-wrap">
        <svg className="graph" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="knowledge graph">
          {data.edges.map((e, i) => {
            const a = pos[e.source];
            const b = pos[e.target];
            if (!a || !b) return null;
            const dim = focusNeighbors && !(focusNeighbors.has(e.source) && focusNeighbors.has(e.target));
            const isOrdering = e.type === "prerequisite_of" || e.type === "depends_on" || e.type === "foundation_of";
            return (
              <line
                key={i}
                x1={a[0]}
                y1={a[1]}
                x2={b[0]}
                y2={b[1]}
                stroke={isOrdering ? "#5eead4" : "#3a4a66"}
                strokeWidth={isOrdering ? 1.4 : 0.7}
                opacity={dim ? 0.12 : isOrdering ? 0.7 : 0.4}
                markerEnd={isOrdering ? "url(#arrow)" : undefined}
              />
            );
          })}
          <defs>
            <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 Z" fill="#5eead4" />
            </marker>
          </defs>
          {data.nodes.map((node) => {
            const p = pos[node.id];
            if (!p) return null;
            const dim = focusNeighbors && !focusNeighbors.has(node.id);
            const color = KIND_COLORS[node.kind] || "#e6edf3";
            const r = 4 + Math.min(node.abstraction_level || 0, 4);
            return (
              <g key={node.id} opacity={dim ? 0.18 : 1} style={{ cursor: "pointer" }}
                 onClick={() => setFocus(focus === node.id ? null : node.id)}>
                <circle cx={p[0]} cy={p[1]} r={r} fill={color} stroke="#05060a" strokeWidth={1} />
                {(focus === node.id || !focus) && (
                  <text x={p[0] + r + 3} y={p[1] + 3} fontSize={9} fill="#8b9bb4">
                    {node.title.length > 22 ? node.title.slice(0, 22) + "…" : node.title}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {focus && store[focus] && (
        <div className="card">
          <strong>{store[focus].title}</strong>{" "}
          <span className="kind-badge">{store[focus].kind}</span>
          <p>{store[focus].contract.what_is_it}</p>
          <Link href={`/concept/${focus}/`}>Open full concept →</Link>
        </div>
      )}

      <div style={{ marginTop: 16 }}>
        <h3>Legend (by kind)</h3>
        <div>
          {Object.entries(KIND_COLORS).map(([k, c]) => (
            <span key={k} className="linkpill" style={{ borderColor: c, color: c }}>
              {k}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
