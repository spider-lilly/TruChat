import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import Logo from "../../assets/icons/logo.svg";

const Navbar = () => {
  const location = useLocation();
  const { user, isAuthenticated } = useAuth();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="border-b border-neutral-700 bg-[#F7F4ED]">
      {/* Top Editorial Strip */}
      <div className="h-8 border-b border-neutral-400 flex items-center justify-between px-6 text-[11px] uppercase tracking-[0.2em] font-serif text-neutral-700">
        <div>EST. AI EDITORIAL DIVISION</div>
        <div className="flex items-center gap-2">
          <span className="font-bold text-neutral-900">Tru</span>
          <span className="inline-flex items-center justify-center w-5 h-5 bg-red-600 text-white rounded-full text-xs">
            🔍
          </span>
          <span className="font-bold text-red-600">Chat</span>
        </div>
        <div className="flex items-center gap-6 font-medium">
          <Link
            to="/dashboard"
            className={`hover:text-black transition-colors ${
              isActive("/dashboard") || isActive("/") ? "underline font-bold text-black" : ""
            }`}
          >
            VERIFY
          </Link>
          <Link
            to="/result"
            className={`hover:text-black transition-colors ${
              isActive("/result") ? "underline font-bold text-black" : ""
            }`}
          >
            RECENT VERDICTS
          </Link>
          {isAuthenticated ? (
            <Link
              to="/profile"
              className={`hover:text-black transition-colors flex items-center gap-1 ${
                isActive("/profile") ? "underline font-bold text-black" : ""
              }`}
            >
              <span>Me</span>
            </Link>
          ) : (
            <Link
              to="/login"
              className="hover:text-black transition-colors font-bold"
            >
              SIGN IN
            </Link>
          )}
        </div>
      </div>

      {/* Main Title Section */}
      <div className="py-6 text-center border-b border-neutral-400">
        <h1 className="text-6xl md:text-7xl font-black tracking-tight font-serif text-neutral-900 uppercase">
          TRUCHAT
        </h1>
        <p className="mt-1 text-xs uppercase tracking-[0.25em] text-neutral-600 font-serif">
          ‘Powered by Trusted Sources &amp; Explainable AI’
        </p>
      </div>
    </header>
  );
};

export default Navbar;