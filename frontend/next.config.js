/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ["localhost", "attendance-system-production-bb54.up.railway.app"],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};
module.exports = nextConfig;
