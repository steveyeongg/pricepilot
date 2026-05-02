/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "*.lazada.com.my" },
      { protocol: "https", hostname: "*.shopee.com.my" },
      { protocol: "https", hostname: "cf.shopee.com.my" },
      { protocol: "https", hostname: "aeonbig.com.my" },
      { protocol: "https", hostname: "*.jayagrocer.com" },
      { protocol: "https", hostname: "*.amazon.com" },
      { protocol: "https", hostname: "*.temu.com" },
      { protocol: "https", hostname: "*.alibaba.com" },
      { protocol: "https", hostname: "villagegrocer.com.my" },
      { protocol: "https", hostname: "*.lotuss.com.my" },
    ],
  },
};

module.exports = nextConfig;
