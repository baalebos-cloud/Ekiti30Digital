import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      // The citizen stories page moved from /my-story; keep old links working.
      { source: "/my-story", destination: "/my-ekiti-story", permanent: true },
      // Ask Ekiti is a floating panel now, not a page; this opens it.
      { source: "/ask-ekiti", destination: "/?ask=1", permanent: false },
    ];
  },
};

export default nextConfig;
