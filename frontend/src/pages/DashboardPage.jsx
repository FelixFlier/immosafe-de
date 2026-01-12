/**
 * DashboardPage Component
 * Risk analysis dashboard with search and map view
 */
import { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Shield, ArrowLeft, Home } from 'lucide-react';
import MapBackground from '../components/MapBackground';
import SearchInput from '../components/SearchInput';
import ComprehensiveRiskCard from '../components/ComprehensiveRiskCard';

// Default center: Germany
const DEFAULT_COORDINATES = { lat: 51.16, lng: 10.45 };

export default function DashboardPage() {
  const [riskData, setRiskData] = useState(null);
  const [coordinates, setCoordinates] = useState(DEFAULT_COORDINATES);
  const [loading, setLoading] = useState(false);
  const [currentAddress, setCurrentAddress] = useState('');

  const handleSearch = async (address) => {
    setLoading(true);
    setRiskData(null);
    setCurrentAddress(address);

    console.log("Sending request to /api/analyze with address:", address);

    try {
      const response = await axios.post('/api/analyze', {
        address,
      });

      console.log("Response received:", response.data);
      setRiskData(response.data);

      if (response.data.coordinates) {
        setCoordinates({
          lat: response.data.coordinates.lat,
          lng: response.data.coordinates.lng,
        });
      }
    } catch (error) {
      console.error("FULL ERROR DETAILS:", error);
      console.error("Error response:", error.response);
      console.error("Error message:", error.message);
      alert("Error: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-slate-50">
      {/* Left Panel - Dashboard Sidebar with Slide-in Animation */}
      <motion.aside 
        initial={{ x: '-100%' }}
        animate={{ x: 0 }}
        transition={{ 
          type: 'spring', 
          stiffness: 100, 
          damping: 20,
          duration: 0.8 
        }}
        className="w-[480px] bg-white h-full shadow-2xl z-20 flex flex-col border-r border-slate-200/80 overflow-hidden flex-shrink-0"
      >
        {/* Sticky Header */}
        <motion.header 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="p-6 border-b border-slate-100 bg-white/80 backdrop-blur-md sticky top-0 z-30 flex-shrink-0"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <motion.div 
                whileHover={{ scale: 1.05, rotate: 5 }}
                whileTap={{ scale: 0.95 }}
                className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/25"
              >
                <Shield className="w-5 h-5 text-white" />
              </motion.div>
              <div>
                <h1 className="text-xl font-bold text-slate-800 tracking-tight">ImmoSafe</h1>
                <p className="text-xs text-slate-500 font-medium">Risikoanalyse Dashboard</p>
              </div>
            </div>
            
            {/* Back to Home Link */}
            <Link 
              to="/"
              className="flex items-center space-x-2 px-3 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-all duration-200"
            >
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">Startseite</span>
            </Link>
          </div>
        </motion.header>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {/* Search Section */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="p-6 border-b border-slate-100"
          >
            <SearchInput onSearch={handleSearch} loading={loading} />
          </motion.div>

          {/* Risk Results Section */}
          {(loading || riskData) && (
            <div className="p-6">
              <ComprehensiveRiskCard data={riskData} loading={loading} address={currentAddress} />
            </div>
          )}

          {/* Empty State */}
          {!loading && !riskData && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7, duration: 0.5 }}
              className="p-6 flex flex-col items-center justify-center text-center min-h-[300px]"
            >
              <motion.div 
                animate={{ y: [0, -5, 0] }}
                transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
                className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mb-4"
              >
                <Shield className="w-8 h-8 text-slate-400" />
              </motion.div>
              <h3 className="text-lg font-semibold text-slate-700 mb-2">
                Immobilien-Risikoanalyse
              </h3>
              <p className="text-sm text-slate-500 max-w-xs">
                Geben Sie eine deutsche Adresse ein, um eine umfassende Naturkatastrophen-Risikoanalyse durchzuführen.
              </p>
            </motion.div>
          )}
        </div>

        {/* Footer */}
        <motion.footer 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.5 }}
          className="p-4 border-t border-slate-100 bg-slate-50/50 flex-shrink-0"
        >
          <p className="text-xs text-slate-400 text-center">
            © 2026 ImmoSafe · Daten vom Deutschen Wetterdienst
          </p>
        </motion.footer>
      </motion.aside>

      {/* Right Panel - Map View with Fade-in Animation */}
      <motion.main 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.2, delay: 0.2 }}
        className="flex-1 relative h-full"
      >
        <MapBackground 
          coordinates={coordinates}
          riskLevel={riskData?.total_risk_level || riskData?.risk_level}
          showRiskCircle={riskData?.total_risk_score > 0 || riskData?.risk_score > 0}
        />
      </motion.main>
    </div>
  );
}
