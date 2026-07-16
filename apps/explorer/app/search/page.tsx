"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { getSearchIndex, getConceptStore } from "../../lib/curriculum";

export default function SearchClient() {
  const [q, setQ] = useState("");
  const [index, setIndex] = useState<{ inverted: Record<string, string[]>; titles: Record<string, string> } | null>(null);
  const [store, setStore] = useState<Record<string, any>>({});

  useEffect(() => {
    getSearchIndex().then(setIndex);
    getConceptStore().then(setStore);
  }, []);

  const results = useMemo(() => {
    if (!index || !q.trim()) return [];
    const term = q.toLowerCase().trim();
    const scored = new Map<string, number>();
    for (const [tok, ids] of Object.entries(index.inverted)) {
      if (tok.includes(term) || term.includes(tok)) {
        for (const id of ids) scored.set(id, (scored.get(id) || 0) + 1);
      }
    }
    // also match by title prefix
    for (const [id, title] of Object.entries(index.titles)) {
      if (title.toLowerCase().includes(term)) scored.set(id, (scored.get(id) || 0) + 2);
    }
    return [...scored.entries()].sort((a, b) => b[1] - a[1]).slice(0, 30);
  }, [q, index]);

  return (
    <div>
      <h1>Search</h1>
      <p className="why">
        A pre-built inverted index (compiled, not a live embedding search). Type
        a term to find concepts.
      </p>
      <input
        className="search-box"
        placeholder="e.g. embeddings, crdt, prerequisite…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      <div className="results">
        {results.map(([id, score]) => {
          const c = store[id];
          if (!c) return null;
          return (
            <div className="result" key={id}>
              <Link href={`/concept/${id}/`}>{c.title}</Link>{" "}
              <span className="kind">{c.kind}</span>
              <div className="why">{c.contract.what_is_it?.slice(0, 140)}…</div>
            </div>
          );
        })}
        {q && results.length === 0 && <p className="why">No matches.</p>}
      </div>
    </div>
  );
}
