import { useEffect, useState } from "react";

// Get API base URL from environment or default to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function WakeBackend() {
  const [warming, setWarming] = useState(true);
  const [tries, setTries] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const ping = async (attempt = 1) => {
      if (cancelled) return;

      try {
        // Create abort controller for timeout
        const ctrl = new AbortController();
        const timeoutId = setTimeout(() => ctrl.abort(), 8000);
        
        // Make health check request
        const res = await fetch(`${API_BASE_URL}/health`, { 
          signal: ctrl.signal, 
          cache: "no-store",
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        
        clearTimeout(timeoutId);
        
        if (cancelled) return;

        if (res.ok) {
          console.log("Backend is awake and ready!");
          setWarming(false);
          setError(null);
          return;
        } else {
          throw new Error(`Health check failed with status: ${res.status}`);
        }
      } catch (err) {
        if (cancelled) return;
        
        // Log the error for debugging
        console.log(`Wake attempt ${attempt} failed:`, err.message);
        
        // Set error message for user feedback
        if (attempt === 1) {
          setError("Connecting to backend...");
        } else if (attempt > 5) {
          setError("Backend is taking longer than usual to wake up. Please wait...");
        }
      }

      if (cancelled) return;

      // Exponential backoff: 1s, 2s, 4s, 8s, then cap at 8s
      const delay = Math.min(8000, 1000 * Math.pow(2, attempt - 1));
      setTries(attempt);
      
      setTimeout(() => {
        if (!cancelled) {
          ping(attempt + 1);
        }
      }, delay);
    };

    // Start the ping process
    ping();
    
    // Cleanup function
    return () => { 
      cancelled = true; 
    };
  }, []);

  // Don't render anything if backend is ready
  if (!warming) return null;

  return (
    <div style={{
      padding: "12px 16px",
      margin: "16px",
      border: "1px solid #e1e5e9",
      borderRadius: "8px",
      backgroundColor: "#f8f9fa",
      fontSize: "14px",
      color: "#495057",
      display: "flex",
      alignItems: "center",
      gap: "12px",
      boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
    }}>
      {/* Loading spinner */}
      <div style={{
        width: "16px",
        height: "16px",
        border: "2px solid #e9ecef",
        borderTop: "2px solid #007bff",
        borderRadius: "50%",
        animation: "spin 1s linear infinite"
      }}></div>
      
      <div>
        <div style={{ fontWeight: "500", marginBottom: "4px" }}>
          Waking the backend...
        </div>
        <div style={{ fontSize: "12px", color: "#6c757d" }}>
          {error ? error : `This can take 20-60 seconds. Attempt ${Math.max(1, tries)}`}
        </div>
      </div>
      
      {/* Add CSS animation for spinner */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
