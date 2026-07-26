import { useNavigate } from "react-router-dom";
import Navbar from "../components/ui/Navbar";
import Sidebar from "../components/ui/Sidebar";
import Footer from "../components/ui/Footer";
import { useAuth } from "../context/AuthContext";

const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await logout();
    navigate("/login");
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "26/07/2026";
    try {
      const d = new Date(dateStr);
      return `${String(d.getDate()).padStart(2, "0")}/${String(d.getMonth() + 1).padStart(2, "0")}/${d.getFullYear()}`;
    } catch {
      return "26/07/2026";
    }
  };

  return (
    <div className="min-h-screen bg-[#F7F4ED] text-neutral-900 selection:bg-red-200 selection:text-red-900">
      <div className="max-w-[1400px] mx-auto min-h-screen flex flex-col border-x border-neutral-400 bg-[#FAF8F5] shadow-xl font-serif">
        <Navbar />

        <main className="flex-1 flex flex-col md:flex-row p-6 gap-6">
          <Sidebar />

          {/* Center Profile Workspace */}
          <div className="flex-1 px-6 space-y-8 flex flex-col items-center pt-6">
            <div className="w-full max-w-xl text-center border-b border-neutral-400 pb-4">
              <h2 className="text-3xl font-extrabold tracking-tight uppercase text-neutral-900">
                YOUR PROFILE
              </h2>
              <p className="text-xs uppercase tracking-widest text-neutral-500 mt-1">
                Account details &amp; preferences
              </p>
            </div>

            {/* Profile Card Box */}
            <div className="w-full max-w-xl border-2 border-neutral-800 bg-white p-8 space-y-6 shadow-md relative">
              {/* User Avatar Circle */}
              <div className="flex flex-col items-center space-y-3">
                <div className="w-20 h-20 rounded-full bg-neutral-200 border-2 border-neutral-800 flex items-center justify-center text-3xl font-bold text-neutral-700">
                  👤
                </div>
                <div className="text-xl font-bold text-neutral-900">
                  {user?.username || user?.email?.split("@")[0] || "Name"}
                </div>
              </div>

              {/* Account Details Table */}
              <div className="space-y-4 border-t border-neutral-300 pt-6 text-sm">
                <div className="flex justify-between items-center border-b border-neutral-200 pb-2">
                  <span className="uppercase tracking-wider text-xs font-bold text-neutral-500">EMAIL</span>
                  <span className="font-mono text-neutral-900">{user?.email || "user@example.com"}</span>
                </div>

                <div className="flex justify-between items-center border-b border-neutral-200 pb-2">
                  <span className="uppercase tracking-wider text-xs font-bold text-neutral-500">MEMBER SINCE</span>
                  <span className="font-mono text-neutral-900">{formatDate(user?.date_joined)}</span>
                </div>

                <div className="flex justify-between items-center border-b border-neutral-200 pb-2">
                  <span className="uppercase tracking-wider text-xs font-bold text-neutral-500">PLAN</span>
                  <span className="font-bold text-emerald-700 uppercase tracking-wider text-xs bg-emerald-50 px-2 py-0.5 border border-emerald-300">Free</span>
                </div>

                <div className="flex justify-between items-center pb-2">
                  <span className="uppercase tracking-wider text-xs font-bold text-neutral-500">VERIFICATION STATUS</span>
                  <span className={`font-bold text-xs uppercase tracking-wider ${user?.is_verified ? "text-emerald-700" : "text-amber-700"}`}>
                    {user?.is_verified ? "VERIFIED EMAIL" : "PENDING VERIFICATION"}
                  </span>
                </div>
              </div>

              {/* Sign Out Button inside card */}
              <div className="pt-4 border-t border-neutral-300 flex justify-center">
                <button
                  onClick={handleSignOut}
                  className="px-6 py-2.5 bg-neutral-900 text-white font-bold text-xs uppercase tracking-widest hover:bg-red-700 transition-colors flex items-center gap-2"
                >
                  <span>[→</span> Sign out <span>]</span>
                </button>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </div>
  );
};

export default Profile;