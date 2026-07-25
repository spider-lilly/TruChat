import { BrowserRouter, Routes, Route } from "react-router-dom";

// Main Pages
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Result from "./pages/Result";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";
import OAuthSuccess from "./pages/OAuthSuccess";

// Authentication Pages
import { LoginPage } from "./components/login/LoginPage";
import { SignUpPage } from "./components/signup/SignUpPage";
import { ForgotPasswordPage } from "./components/forgot-password/ForgotPasswordPage";
import { ResetPasswordPage } from "./components/reset-password/ResetPasswordPage";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>

        {/* Landing */}
        <Route path="/" element={<Landing />} />

        {/* Main Application */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/result" element={<Result />} />
        <Route path="/profile" element={<Profile />} />

        {/* Authentication */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route
          path="/forgot-password"
          element={<ForgotPasswordPage />}
        />
        <Route
          path="/reset-password"
          element={<ResetPasswordPage />}
        />
        <Route
          path="/oauth-success"
          element={<OAuthSuccess />}
        />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />

      </Routes>
    </BrowserRouter>
  );
};

export default App;