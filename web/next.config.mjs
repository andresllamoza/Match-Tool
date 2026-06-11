/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_DEMO_MODE: process.env.API_URL?.trim() ? "false" : "true",
  },
};

export default nextConfig;
