import Link from "next/link";
import { getConceptStore } from "../../lib/curriculum.server";
import SearchClient from "./SearchClient";

export const metadata = {
  title: "Search — SKC Explorer",
  description:
    "Search the compiled concept corpus. A static index of every concept is rendered server-side; the live box is a progressive enhancement.",
};

export default async function SearchPage() {
  const store = await getConceptStore();
  const concepts = Object.values(store).sort((a: any, b: any) =>
    (a.title || "").localeCompare(b.title || "")
  );

  return (
    <div>
      <h1>Search</h1>
      <p className="why">
        A pre-built inverted index (compiled, not a live embedding search). The live
        search box below requires JavaScript; the full concept index is rendered
        server-side and is fully crawlable without JS.
      </p>

      <SearchClient />

      <h2>All concepts ({concepts.length})</h2>
      <ul className="idx">
        {concepts.map((c: any) => (
          <li key={c.id}>
            <Link href={`/concept/${c.id}/`}>{c.title}</Link>{" "}
            <span className="kind">{c.kind}</span>
            {c.contract?.what_is_it ? (
              <span className="why"> — {c.contract.what_is_it.slice(0, 120)}…</span>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
