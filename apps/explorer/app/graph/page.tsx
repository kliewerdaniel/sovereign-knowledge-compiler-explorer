import Link from "next/link";
import { getConceptViews, getConceptStore } from "../../lib/curriculum.server";
import GraphClient from "./GraphClient";

export const metadata = {
  title: "Knowledge Graph — SKC Explorer",
  description:
    "The compiled concept graph, with a server-rendered node/edge table for crawlers and no-JS readers.",
};

export default async function GraphPage() {
  const [views, store] = await Promise.all([getConceptViews(), getConceptStore()]);
  const view = views["prerequisite-graph"] || Object.values(views)[0] || { nodes: [], edges: [] };
  const nodes = view.nodes || [];
  const edges = view.edges || [];

  return (
    <div>
      <h1>Knowledge Graph</h1>
      <p className="why">
        The compiled concept graph ({nodes.length} nodes, {edges.length} edges in the
        prerequisite view). The interactive SVG below requires JavaScript; the tables
        beneath it are server-rendered and fully readable with JS disabled. Every node
        links to its static concept page.
      </p>

      <GraphClient />

      <noscript>
        <p className="why">(Interactive graph needs JavaScript. The node/edge list is rendered below.)</p>
      </noscript>

      <h2 id="node-table">Nodes ({nodes.length})</h2>
      <ul className="idx">
        {nodes.map((n: any) => (
          <li key={n.id}>
            <Link href={`/concept/${n.id}/`}>{n.title}</Link>{" "}
            <span className="kind">{n.kind}</span>
          </li>
        ))}
      </ul>

      <h2 id="edge-table">Edges ({edges.length})</h2>
      <table className="graphtable">
        <thead>
          <tr><th>type</th><th>source</th><th>target</th></tr>
        </thead>
        <tbody>
          {edges.map((e: any, i: number) => (
            <tr key={i}>
              <td className="kind">{e.type}</td>
              <td>
                {store[e.source] ? (
                  <Link href={`/concept/${e.source}/`}>{store[e.source].title}</Link>
                ) : (
                  e.source
                )}
              </td>
              <td>
                {store[e.target] ? (
                  <Link href={`/concept/${e.target}/`}>{store[e.target].title}</Link>
                ) : (
                  e.target
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
