import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function OAuthSuccess() {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);

    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");

    console.log("URL:", window.location.href);
    console.log("Access:", accessToken);
    console.log("Refresh:", refreshToken);

    if (!accessToken || !refreshToken) {
      return;
    }

    localStorage.setItem("accessToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);

    navigate("/", { replace: true });
  }, [navigate]);

  return <h1>Signing you in...</h1>;
}