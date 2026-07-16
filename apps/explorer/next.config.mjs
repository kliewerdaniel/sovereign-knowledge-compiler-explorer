/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
  typescript: { ignoreBuildErrors: true },
  // No server runtime, no API routes. Pure static export.
};

export default nextConfig;
