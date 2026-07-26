import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function OAuthSuccess() {
  const navigate = useNavigate();
  const { refreshProfile } = useAuth();

  useEffect(() => {
    const completeOAuthLogin = async () => {
      const params = new URLSearchParams(window.location.search);

      const accessToken = params.get("access_token");
      const refreshToken = params.get("refresh_token");

      if (!accessToken || !refreshToken) {
        navigate("/login", { replace: true });
        return;
      }

      localStorage.setItem("accessToken", accessToken);
      localStorage.setItem("refreshToken", refreshToken);

      const profileLoaded = await refreshProfile();
      navigate(profileLoaded ? "/dashboard" : "/login", { replace: true });
    };

    completeOAuthLogin();
  }, [navigate, refreshProfile]);

  return <h1>Signing you in...</h1>;
}
