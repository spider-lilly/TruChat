import Navbar from "../components/ui/Navbar";
import Sidebar from "../components/ui/Sidebar";
import RightPanel from "../components/home/RightPanel";
import Footer from "../components/ui/Footer";
import HistorySection from "../components/home/HistorySection";

const History = () => {
  return (
    <div className="min-h-screen bg-[#F7F4ED] text-neutral-900 selection:bg-red-200 selection:text-red-900">
      <div className="mx-auto flex min-h-screen max-w-[1400px] flex-col border-x border-neutral-400 bg-[#FAF8F5] shadow-xl">
        <Navbar />

        <main className="flex-1 flex flex-col md:flex-row gap-6 p-6">
          <Sidebar />

          <div className="flex-1 px-6 py-2">
            <HistorySection />
          </div>

          <RightPanel />
        </main>

        <Footer />
      </div>
    </div>
  );
};

export default History;