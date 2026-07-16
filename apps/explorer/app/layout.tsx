import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sovereign Knowledge Compiler Explorer",
  description:
    "An interactive explanation engine that recursively explains how the Sovereign Knowledge Compiler works — compiled by the compiler itself.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <a href="/" className="brand">SKC Explorer</a>
          <nav>
            <a href="/">Root</a>
            <a href="/graph/">Graph</a>
            <a href="/paths/">Paths</a>
            <a href="/search/">Search</a>
            <a href="/about/">About</a>
          </nav>
        </header>
        <main>{children}</main>
        <footer className="site-footer">
          <span>Compiled, not chat. Zero runtime inference.</span>
        </footer>
      </body>
    </html>
  );
}
