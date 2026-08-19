import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Emits a minimal, self-contained server bundle (.next/standalone) instead of
  // requiring the full node_modules tree in the deployed image -- what the Docker
  // build below actually copies into the runtime container.
  output: "standalone",
};

export default nextConfig;
