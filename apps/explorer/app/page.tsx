import Link from "next/link";
import { getConceptStore } from "@/lib/curriculum.server";

const ROOT = "sovereign-knowledge-compiler";

export default async function HomePage() {
  const store = await getConceptStore();
  const root = store[ROOT];
  if (!root) return <div>Root concept not found.</div>;
  return (
    <RootView concept={root} store={store} />
  );
}

function RootView({ concept, store }: { concept: any; store: Record<string, any> }) {
  const c = concept;
  const prereqs = (c.prerequisite_ids || []).map((id: string) => store[id]).filter(Boolean);
  const deps = (c.dependency_ids || []).map((id: string) => store[id]).filter(Boolean);
  const related = (c.related_ids || []).map((id: string) => store[id]).filter(Boolean);
  return (
    <article>
      <h1>{c.title}<span className="kind-badge">{c.kind}</span></h1>
      <div className="summary">{c.contract.what_is_it}</div>
      <p className="why">{c.contract.why_exists}</p>

      <h2>Descend</h2>
      <div className="descend-grid">
        <div className="descend-col">
          <h3>Prerequisites</h3>
          <ul>
            {prereqs.map((p: any) => (
              <li key={p.id}><Link href={`/concept/${p.id}/`}>{p.title}</Link></li>
            ))}
            {prereqs.length === 0 && <li className="why">—</li>}
          </ul>
        </div>
        <div className="descend-col">
          <h3>What it&apos;s made of</h3>
          <ul>
            {deps.map((p: any) => (
              <li key={p.id}><Link href={`/concept/${p.id}/`}>{p.title}</Link></li>
            ))}
            {deps.length === 0 && <li className="why">—</li>}
          </ul>
        </div>
        <div className="descend-col">
          <h3>Related</h3>
          <ul>
            {related.map((p: any) => (
              <li key={p.id}><Link href={`/concept/${p.id}/`}>{p.title}</Link></li>
            ))}
            {related.length === 0 && <li className="why">—</li>}
          </ul>
        </div>
      </div>

      <h2>Start a guided tour</h2>
      <p>
        <Link href="/paths/">Browse learning paths →</Link> or{" "}
        <Link href="/graph/">explore the graph →</Link>.
      </p>

      <h2>What this is</h2>
      <p>
        This is the first self-explaining artifact of the Sovereign Knowledge
        Compiler. The compiler compiled its own explanation: every concept you
        can open knows what it is, why it exists, what it depends on, and where
        to go next. There is no chatbot here — the application is a static
        artifact, served with zero runtime inference.
      </p>
    </article>
  );
}
