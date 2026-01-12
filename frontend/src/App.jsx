/**
 * ImmoSafe DE - Main Application Component
 * Multi-page application with React Router
 */
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { APIProvider } from '@vis.gl/react-google-maps';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

function App() {
  if (!GOOGLE_MAPS_API_KEY) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <p className="text-slate-500 mb-2">Google Maps API key not configured</p>
          <p className="text-sm text-slate-400">Please set VITE_GOOGLE_MAPS_API_KEY in your environment</p>
        </div>
      </div>
    );
  }

  return (
    <APIProvider apiKey={GOOGLE_MAPS_API_KEY}>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </Router>
    </APIProvider>
  );
}

export default App;
