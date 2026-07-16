import Link from "next/link";
import { getStats } from "@/lib/curriculum.server";

export default async function AboutPage() {
  const stats = await getStats();
  return (
    <div>
      <h1>About</h1>
      <div className="about-hero">
        <p>
          The <strong>Sovereign Knowledge Compiler Explorer</strong> is the first
          self-explaining artifact of the Sovereign Knowledge Compiler. The
          compiler&apos;s first compiled output is this application, which teaches
          you how the compiler works — recursively, from the highest-level
          architecture down to the underlying mathematics and computer science.
        </p>
      </div>

      <h2>The thesis: compile-time vs runtime</h2>
      <table className="cmp">
        <thead>
          <tr><th>Dimension</th><th>Runtime LLM conversation</th><th>Compiled curriculum (SKCE)</th></tr>
        </thead>
        <tbody>
          <tr><td>Cost per read</td><td>Full reasoning per query</td><td>Zero inference; static artifact</td></tr>
          <tr><td>Determinism</td><td>Non-deterministic every time</td><td>Deterministic artifact (model passes recorded)</td></tr>
          <tr><td>Sovereignty</td><td>Depends on cloud API</td><td>Local-first, inspectable, versionable</td></tr>
          <tr><td>Structure</td><td>Emergent in transcript</td><td>Baked-in prerequisite graph</td></tr>
          <tr><td>Drift</td><td>Conversation evaporates</td><td>Durable graph, re-compilable</td></tr>
        </tbody>
      </table>

      <h2>How it was built</h2>
      <p>
        A deterministic compiler (<code>compiler/</code>) parses a typed corpus —
        the research blog, the compiler source, and declared concept specs —
        into an intermediate representation, runs passes (ingest → normalize →
        extract → link → prerequisite-infer → optimize → emit), and writes an
        immutable, content-hashed bundle. This static Next.js app reads that
        bundle. No code runs at read time.
      </p>

      {stats && (
        <>
          <h2>This build</h2>
          <div className="stat-row">
            <div className="stat"><div className="n">{stats.concept_count}</div><div className="l">concepts</div></div>
            <div className="stat"><div className="n">{stats.edge_count}</div><div className="l">edges</div></div>
            <div className="stat"><div className="n">{stats.learning_path_count}</div><div className="l">learning paths</div></div>
            <div className="stat"><div className="n">{stats.max_descent_depth}</div><div className="l">max depth</div></div>
            <div className="stat"><div className="n">{stats.gap_count}</div><div className="l">gaps</div></div>
          </div>
          <p className="why">
            Coverage (declared): {Math.round((stats.coverage?.declared || 0) * 100)}%.
            Model vs deterministic nodes: {stats.model_vs_deterministic?.nodes?.join(" / ")}.
          </p>
        </>
      )}

      <h2>Source</h2>
      <ul>
        <li><Link href="/">Open the root concept →</Link></li>
        <li>
          <a href="https://github.com/kliewerdaniel/sovereign-knowledge-compiler-explorer" target="_blank" rel="noreferrer">
            GitHub repository
          </a>
        </li>
        <li>
          <a href="https://www.danielkliewer.com" target="_blank" rel="noreferrer">
            danielkliewer.com (canonical research record)
          </a>
        </li>
      </ul>
    </div>
  );
}
