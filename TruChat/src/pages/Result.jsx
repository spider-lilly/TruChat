import { useLocation } from "react-router-dom";
import Navbar from "../components/ui/Navbar";
import Sidebar from "../components/ui/Sidebar";
import RightPanel from "../components/home/RightPanel";
import Footer from "../components/ui/Footer";
import ResultCard from "../components/result/ResultCard";

const Result = () => {
  const location = useLocation();
  const result = location.state?.result || null;

  return (
    <div className="min-h-screen bg-[#F7F4ED] text-neutral-900 selection:bg-red-200 selection:text-red-900">
      <div className="max-w-[1400px] mx-auto min-h-screen flex flex-col border-x border-neutral-400 bg-[#FAF8F5] shadow-xl">
        <Navbar />

        <main className="flex-1 flex flex-col md:flex-row p-6 gap-6">
          <Sidebar />

          <div className="flex-1 px-6 space-y-6">
            <ResultCard result={result} />
          </div>

          <RightPanel />
        </main>

        <Footer />
      </div>
    </div>
  );
};

export default Result;