import Link from "next/link";
import { getLearningPaths, getConceptStore } from "../../lib/curriculum.server";

export default async function PathsPage() {
  const paths = await getLearningPaths();
  const store = await getConceptStore();
  const list = Object.values(paths).sort((a: any, b: any) => a.estimated_depth - b.estimated_depth);
  return (
    <div>
      <h1>Learning Paths</h1>
      <p className="why">
        Pre-computed traversals of the prerequisite DAG. Each path is a guided
        descent from the root concept to a foundation — compiled, not generated
        at read time.
      </p>
      {list.map((p: any) => (
        <div className="path-card" key={p.id}>
          <strong>{p.name}</strong>{" "}
          <span className="depth">
            depth {p.estimated_depth} · {p.difficulty}
          </span>
          <p style={{ marginTop: 8 }}>
            {p.ordered_concept_ids.map((id: string, i: number) => (
              <span key={id}>
                {i > 0 && <span className="why"> → </span>}
                {store[id] ? (
                  <Link href={`/concept/${id}/`}>{store[id].title}</Link>
                ) : (
                  <span>{id}</span>
                )}
              </span>
            ))}
          </p>
        </div>
      ))}
    </div>
  );
}
