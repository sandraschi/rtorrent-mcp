import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";
import { AppLayout } from "@/components/layout/app-layout";
import { AnnasSearchPage } from "@/pages/annas";
import { Apps } from "@/pages/apps";
import { Chat } from "@/pages/chat";
import { Dashboard } from "@/pages/dashboard";
import { Depot } from "@/pages/depot";
import { GutenbergSearchPage } from "@/pages/gutenberg";
import { Help } from "@/pages/help";
import Logging from "@/pages/Logging";
import { NyaaSearchPage } from "@/pages/nyaa";
import { PirateBaySearchPage } from "@/pages/piratebay";
import { Settings } from "@/pages/settings";
import { Skills } from "@/pages/skills";
import { Status } from "@/pages/status";
import { Tools } from "@/pages/tools";

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/nyaa" element={<NyaaSearchPage />} />
          <Route path="/bay" element={<PirateBaySearchPage />} />
          <Route path="/gutenberg" element={<GutenbergSearchPage />} />
          <Route path="/annas" element={<AnnasSearchPage />} />
          <Route path="/depot" element={<Depot />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/status" element={<Status />} />
          <Route path="/apps" element={<Apps />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/logs" element={<Logging />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
