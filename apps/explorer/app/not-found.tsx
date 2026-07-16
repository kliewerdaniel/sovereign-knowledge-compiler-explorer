import Link from "next/link";

export default function NotFound() {
  return (
    <div>
      <h1>Not found</h1>
      <p className="why">
        That concept isn&apos;t in the compiled curriculum. Knowledge here is a
        static artifact — if a node is missing, it wasn&apos;t in the corpus when
        the compiler last ran.
      </p>
      <p>
        <Link href="/">Return to the root concept →</Link>
      </p>
    </div>
  );
}
