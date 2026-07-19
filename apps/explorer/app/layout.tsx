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
      <head>
        <link rel="alternate" type="application/json" href="/concept-store.json" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@graph": [
                {
                  "@type": "WebSite",
                  "@id": "https://skce-explorer.vercel.app/#website",
                  "url": "https://skce-explorer.vercel.app/",
                  "name": "Sovereign Knowledge Compiler Explorer",
                  "description":
                    "An interactive explanation engine that recursively explains how the Sovereign Knowledge Compiler works — compiled by the compiler itself. Zero runtime inference; every concept is a static, crawlable page.",
                  "inLanguage": "en",
                },
                {
                  "@type": "DataCatalog",
                  "@id": "https://skce-explorer.vercel.app/#catalog",
                  "name": "Sovereign Knowledge Compiler Concept Corpus",
                  "url": "https://skce-explorer.vercel.app/",
                  "description":
                    "Compiled concept graph of the Sovereign AI methodology — concepts, decisions, patterns, and their typed prerequisite/related edges. Built at compile time from source documents.",
                  "keywords": [
                    "sovereign AI",
                    "knowledge compiler",
                    "concept graph",
                    "compile-time AI",
                    "methodology",
                  ],
                  "creator": {
                    "@type": "Person",
                    "name": "Daniel Kliewer",
                    "url": "https://danielkliewer.com",
                  },
                  "sameAs": "https://danielkliewer.com",
                  "distribution": [
                    {
                      "@type": "DataDownload",
                      "encodingFormat": "application/json",
                      "contentUrl":
                        "https://skce-explorer.vercel.app/concept-store.json",
                      "name": "concept-store.json (full concept graph)",
                    },
                    {
                      "@type": "DataDownload",
                      "encodingFormat": "text/plain",
                      "contentUrl": "https://skce-explorer.vercel.app/llms.txt",
                      "name": "llms.txt",
                    },
                    {
                      "@type": "DataDownload",
                      "encodingFormat": "application/xml",
                      "contentUrl": "https://skce-explorer.vercel.app/sitemap.xml",
                      "name": "sitemap.xml",
                    },
                  ],
                },
              ],
            }),
          }}
        />
      </head>
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
