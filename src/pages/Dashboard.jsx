import Navbar from "../components/ui/Navbar";
import Sidebar from "../components/ui/Sidebar";
import MainContent from "../components/home/MainContent";
import RightPanel from "../components/home/RightPanel";
import Footer from "../components/ui/Footer";

import Logo from "../assets/icons/logo.svg";

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-[#F7F4ED]">

      {/* Entire Page Container */}
      <div className="max-w-[1380px] mx-auto min-h-screen flex flex-col">

        {/* Top Editorial Strip */}
        <div className="h-7 border-b border-neutral-500 flex items-center justify-between px-5 text-[10px] uppercase tracking-[0.18em]">

          <p className="text-neutral-600">
            EST. 43 Editorial Division
          </p>

          <img
            src={Logo}
            alt="TruChat"
            className="h-6 object-contain"
          />

        </div>

        {/* Logo Section */}
        <section className="border-b border-neutral-500 py-7">

          <h1 className="text-center text-7xl font-black tracking-tight leading-none">
            TRUCHAT
          </h1>

          <p className="mt-2 text-center text-[11px] text-neutral-500">
            Powered by Trusted Sources &amp; Explainable AI
          </p>

        </section>

        {/* Navigation */}
        <Navbar />

        {/* Dashboard Body */}
        <main className="flex flex-1 px-5 pt-6">

          <Sidebar />

          <MainContent />

          <RightPanel />

        </main>

        {/* Footer */}
        <Footer />

      </div>

    </div>
  );
};

export default Dashboard;