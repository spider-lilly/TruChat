import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const Sidebar = ({ verdictCounts = { verified: 0, unverified: 0, misleading: 0 }, history = [] }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const handleSignOut = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <aside className="w-64 flex-shrink-0 border-r border-neutral-400 pr-6 flex flex-col justify-between font-serif min-h-[500px]">
      <div className="space-y-8">
        {/* Nav Links */}
        <nav className="space-y-3 text-xs uppercase tracking-widest font-bold">
          <Link
            to="/dashboard"
            className={`flex items-center gap-2 py-1 transition-colors ${
              location.pathname === "/dashboard" || location.pathname === "/"
                ? "text-neutral-900 font-extrabold"
                : "text-neutral-500 hover:text-neutral-900"
            }`}
          >
            <span className="text-red-600 font-bold">•</span> VERIFY NEWS
          </Link>
          <Link
            to="/history"
            className={`block py-1 transition-colors ${
              location.pathname === "/history"
                ? "text-neutral-900 font-extrabold"
                : "text-neutral-500 hover:text-neutral-900"
            }`}
          >
            HISTORY
          </Link>
          <Link
            to="/profile"
            className={`block py-1 transition-colors ${
              location.pathname === "/profile"
                ? "text-neutral-900 font-extrabold"
                : "text-neutral-500 hover:text-neutral-900"
            }`}
          >
            PROFILE
          </Link>
        </nav>

        {/* Verdict Counters */}
        <div className="border-t border-b border-neutral-400 py-4 space-y-2">
          <h3 className="text-[11px] font-bold uppercase tracking-wider text-neutral-800">
            TODAY'S VERDICT:
          </h3>
          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between items-center text-neutral-700">
              <span className="uppercase tracking-wider">VERIFIED</span>
              <span className="font-mono font-bold text-neutral-900">{verdictCounts.verified || 0}</span>
            </div>
            <div className="flex justify-between items-center text-neutral-700">
              <span className="uppercase tracking-wider">UNVERIFIED</span>
              <span className="font-mono font-bold text-neutral-900">{verdictCounts.unverified || 0}</span>
            </div>
            <div className="flex justify-between items-center text-neutral-700">
              <span className="uppercase tracking-wider">MISLEADING</span>
              <span className="font-mono font-bold text-neutral-900">{verdictCounts.misleading || 0}</span>
            </div>
          </div>
        </div>

        {/* History List */}
        <div className="space-y-3">
          <h3 className="text-[11px] font-bold uppercase tracking-wider text-neutral-800">
            Chat History
          </h3>
          {history && history.length > 0 ? (
            <ul className="space-y-2 text-xs text-neutral-700">
              {history.slice(0, 5).map((item, idx) => (
                <li key={idx} className="truncate hover:text-black cursor-pointer border-b border-neutral-200 pb-1">
                  {item.claim_text || item}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-neutral-500 italic">No recent verification queries</p>
          )}
        </div>
      </div>

      {/* Logout Action */}
      <div className="pt-6 border-t border-neutral-400">
        <button
          onClick={handleSignOut}
          className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-neutral-900 hover:text-red-700 transition-colors"
        >
          <span>↳</span> Sign out
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;