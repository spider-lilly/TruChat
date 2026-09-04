import { useEffect } from "react";

function AdBanner() {
  useEffect(() => {
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (error) {
      console.error("AdSense error:", error);
    }
  }, []);

  return (
    <ins
      className="adsbygoogle"
      style={{ display: "block" }}
      data-ad-client="ca-pub-2974105923871330"
      data-ad-slot="8992707196"
      data-ad-format="auto"
      data-full-width-responsive="true"
    />
  );
}

export default AdBanner;
