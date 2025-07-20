import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'i.ibb.co',
      },
      {
        protocol: 'https',
        hostname: 'ui-avatars.com',
      },
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'https',
        hostname: 'example.com',
      },
      // Cloudflare R2 public URLs
      {
        protocol: 'https',
        hostname: '*.r2.dev',
      },
      // Custom domain cho R2
      {
        protocol: 'https',
        hostname: 's3.cloudfly.vn',
      },
    ],
  },
};

export default nextConfig;
