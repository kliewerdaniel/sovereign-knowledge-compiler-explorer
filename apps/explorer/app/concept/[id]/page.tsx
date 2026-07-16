import Link from "next/link";
import { notFound } from "next/navigation";
import { getConceptStore, getMisconceptions, sourceHref, sourceLabel } from "../../../lib/curriculum.server";

export async function generateStaticParams() {
  const store = await getConceptStore();
  return Object.keys(store).map((id) => ({ id }));
}

export default async function ConceptPage({ params }: { params: { id: string } }) {
  const store = await getConceptStore();
  const c = store[params.id];
  if (!c) notFound();
  const mcs = (await getMisconceptions()).filter((m) => m.concept_id === params.id);

  const pick = (ids: string[]) => ids.map((id) => store[id]).filter(Boolean);
  const prereqs = pick(c.prerequisite_ids || []);
  const deps = pick(c.dependency_ids || []);
  const related = pick(c.related_ids || []);
  const foundations = pick((c.foundation_links || []).map((f: any) => f.foundationId));

  return (
    <article>
      <div className="breadcrumb">
        <Link href="/">SKC</Link> / <span>{c.title}</span>
      </div>
      <h1>
        {c.title}
        <span className="kind-badge">{c.kind}</span>
        {c.source === "model:synth" && <span className="conf-badge">◇ synth</span>}
        {c.confidence < 1 && c.source !== "model:synth" && (
          <span className="conf-badge">conf {c.confidence.toFixed(2)}</span>
        )}
      </h1>

      <div className="summary">{c.contract.what_is_it}</div>
      <p className="why">{c.contract.why_exists}</p>

      {c.contract.where_appears?.length > 0 && (
        <>
          <h2>Where it appears</h2>
          <ul>
            {c.contract.where_appears.map((w: string, i: number) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </>
      )}

      <h2>Descend</h2>
      <div className="descend-grid">
        <DescendCol title="Prerequisites" items={prereqs} />
        <DescendCol title="Dependencies" items={deps} />
        <DescendCol title="Foundations" items={foundations} />
        <DescendCol title="Related" items={related} />
      </div>

      {c.contract.historical_evolution && (
        <>
          <h2>Historical evolution</h2>
          <p>{c.contract.historical_evolution}</p>
        </>
      )}
      {c.contract.implementation_details && (
        <>
          <h2>Implementation details</h2>
          <p className="mono">{c.contract.implementation_details}</p>
        </>
      )}

      {mcs.length > 0 && (
        <>
          <h2>Common confusion</h2>
          {mcs.map((m) => (
            <div className="callout" key={m.id}>
              <div className="mc-q">Misconception: {m.misconception}</div>
              <div className="mc-a">Clarification: {m.correction}</div>
            </div>
          ))}
        </>
      )}

      {(c.contract.source_references?.length > 0 || c.source_refs?.length > 0) && (
        <>
          <h2>Sources</h2>
          <ul className="src-list">
            {[...(c.contract.source_references || []), ...(c.source_refs || [])].map(
              (r: any, i: number) => {
                const href = sourceHref(r.ref || r);
                return (
                  <li key={i} className="source-ref">
                    [{sourceLabel(r.ref || r)}]&nbsp;
                    {href ? (
                      <a href={href} target="_blank" rel="noreferrer">{r.ref || r}</a>
                    ) : (
                      <span>{r.ref || r}</span>
                    )}
                    {r.quote && <span> — “{r.quote}”</span>}
                  </li>
                );
              }
            )}
          </ul>
        </>
      )}

      <p style={{ marginTop: 28 }}>
        <Link href="/graph/">View in graph →</Link>
      </p>
    </article>
  );
}

function DescendCol({ title, items }: { title: string; items: any[] }) {
  return (
    <div className="descend-col">
      <h3>{title}</h3>
      <ul>
        {items.map((p) => (
          <li key={p.id}>
            <Link href={`/concept/${p.id}/`}>{p.title}</Link>
          </li>
        ))}
        {items.length === 0 && <li className="why">—</li>}
      </ul>
    </div>
  );
}
