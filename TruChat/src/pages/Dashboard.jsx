import { useState, useEffect } from "react";
import Navbar from "../components/ui/Navbar";
import Sidebar from "../components/ui/Sidebar";
import MainContent from "../components/home/MainContent";
import RightPanel from "../components/home/RightPanel";
import Footer from "../components/ui/Footer";

const Dashboard = () => {
  const [verdictCounts, setVerdictCounts] = useState(() => {
    const saved = localStorage.getItem("verdictCounts");
    return saved ? JSON.parse(saved) : { verified: 0, unverified: 0, misleading: 0 };
  });

  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem("claimHistory");
    return saved ? JSON.parse(saved) : [];
  });

  const handleClaimSubmitted = (newResult) => {
    // Update history
    const updatedHistory = [newResult, ...history];
    setHistory(updatedHistory);
    localStorage.setItem("claimHistory", JSON.stringify(updatedHistory));

    // Update verdict count
    const updatedCounts = { ...verdictCounts };
    if (newResult.verdict === "SUPPORTS" || newResult.verdict === "VERIFIED") {
      updatedCounts.verified += 1;
    } else if (newResult.verdict === "REFUTES" || newResult.verdict === "MISLEADING") {
      updatedCounts.misleading += 1;
    } else {
      updatedCounts.unverified += 1;
    }
    setVerdictCounts(updatedCounts);
    localStorage.setItem("verdictCounts", JSON.stringify(updatedCounts));
  };

  return (
    <div className="min-h-screen bg-[#F7F4ED] text-neutral-900 selection:bg-red-200 selection:text-red-900">
      <div className="max-w-350 mx-auto min-h-screen flex flex-col border-x border-neutral-400 bg-[#FAF8F5] shadow-xl">
        {/* Navigation & Header */}
        <Navbar />

        {/* Dashboard Main Workspace */}
        <main className="flex-1 flex flex-col md:flex-row p-6 gap-6">
          <Sidebar verdictCounts={verdictCounts} history={history} />
          <MainContent onClaimSubmitted={handleClaimSubmitted} />
          <RightPanel />
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
};

export default Dashboard;