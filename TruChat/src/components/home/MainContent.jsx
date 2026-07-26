import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ExampleClaims from "./ExampleClaims";
import ClaimInput from "./ClaimInput";
import { checkClaim } from "../../services/claims";
import { useAuth } from "../../context/AuthContext";

const MainContent = ({ onClaimSubmitted }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [claimText, setClaimText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const getUserDisplayName = () => {
    if (user?.username) return user.username;
    if (user?.email) return user.email.split("@")[0];
    return "xyz";
  };

  const handleSelectExample = (example) => {
    setClaimText(example);
  };

  const handleSubmitClaim = async (text) => {
    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const response = await checkClaim(text);
      const resultData = {
        claim_text: text,
        verdict: response.data.verdict,
        credibility_score: response.data.credibility_score,
        confidence_score: response.data.confidence_score,
        explanation: response.data.explanation,
        created_at: new Date().toISOString(),
      };

      if (onClaimSubmitted) {
        onClaimSubmitted(resultData);
      }

      // Navigate to result page with result state
      navigate("/result", { state: { result: resultData } });
    } catch (error) {
      console.error("Claim verification error:", error);
      if (error.response?.data?.detail) {
        setErrorMessage(error.response.data.detail);
      } else {
        setErrorMessage("Unable to verify claim. Please check backend connection.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-1 px-6 space-y-8 font-serif">
      {/* Header Banner */}
      <div className="space-y-2 border-b border-neutral-400 pb-5">
        <div className="text-[11px] font-bold uppercase tracking-widest text-neutral-500">
          AI Verification Bureau
        </div>
        <h2 className="text-3xl font-extrabold text-neutral-900">
          Welcome, {getUserDisplayName()}
        </h2>
        <p className="text-xs text-neutral-700 leading-relaxed max-w-2xl">
          Paste/Type in any news claim, headline, or social media post below. Our AI will analyze it and deliver a verdict with credibility scores and supporting sources.
        </p>
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div className="border border-red-500 bg-red-100/70 p-3 text-xs text-red-900 font-medium">
          {errorMessage}
        </div>
      )}

      {/* Example Claims */}
      <ExampleClaims onSelectClaim={(text) => handleSubmitClaim(text)} />

      {/* Claim Input Card */}
      <ClaimInput
        onSubmitClaim={handleSubmitClaim}
        isSubmitting={isSubmitting}
      />
    </div>
  );
};

export default MainContent;