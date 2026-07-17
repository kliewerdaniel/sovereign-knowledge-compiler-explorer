/** @type {import('next').NextConfig} */
const nextConfig = {
  // No output:export — Vercel serves this as a normal Next.js app. All pages are
  // prerendered at build time (generateStaticParams), so read-time is still
  // zero-inference; Vercel just handles routing correctly (no static-export
  // trailing-slash mismatch).
  images: { unoptimized: true },
  typescript: { ignoreBuildErrors: true },
};

export default nextConfig;
