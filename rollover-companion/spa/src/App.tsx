import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { JourneyProvider } from "./context/JourneyProvider";
import { AgentPage } from "./pages/AgentPage";
import { CustomerPage } from "./pages/CustomerPage";

export default function App() {
  return (
    <JourneyProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CustomerPage />} />
        <Route path="/agent" element={<AgentPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
    </JourneyProvider>
  );
}
