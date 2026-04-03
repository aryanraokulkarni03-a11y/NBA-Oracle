import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DashboardPage } from "./pages/Dashboard";
import { LearningPage } from "./pages/Learning";
import { LoginPage } from "./pages/Login";
import { OperationsPage } from "./pages/Operations";
import { PerformancePage } from "./pages/Performance";
import { ProvidersPage } from "./pages/Providers";
import { StabilityPage } from "./pages/Stability";
import { TodayPage } from "./pages/Today";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="today" element={<TodayPage />} />
        <Route path="performance" element={<PerformancePage />} />
        <Route path="stability" element={<StabilityPage />} />
        <Route path="learning" element={<LearningPage />} />
        <Route path="providers" element={<ProvidersPage />} />
        <Route path="operations" element={<OperationsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
