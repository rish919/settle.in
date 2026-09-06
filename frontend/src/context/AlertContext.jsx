import React, { createContext, useContext, useEffect, useState } from 'react';
import { checkSmartAlerts } from '../api/cityApi';
import { useLocalStorage } from '../hooks/useLocalStorage';
import NotificationToast from '../components/NotificationToast';

const AlertContext = createContext();

export function AlertProvider({ children }) {
  const [savedLocalities] = useLocalStorage('settle_saved_localities', []);
  const [prefs] = useLocalStorage('settle_preferences', null);
  const [activeAlert, setActiveAlert] = useState(null);
  const [alertHistory, setAlertHistory] = useLocalStorage('settle_alert_history', []);
  
  useEffect(() => {
    // Polling function
    const fetchAlerts = async () => {
      if (!savedLocalities || savedLocalities.length === 0) return;
      
      const localityIds = savedLocalities.map(loc => loc.id || loc.locality_id);
      
      try {
        const payload = {
          locality_ids: localityIds,
          max_rent: prefs?.max_rent || null,
          max_commute_mins: prefs?.max_commute_minutes || null
        };
        
        const response = await checkSmartAlerts(payload);
        if (response && response.alerts && response.alerts.length > 0) {
          
          // Check if we already saw these alerts
          const newAlerts = response.alerts.filter(
            alert => !alertHistory.some(hist => hist.id === alert.id)
          );
          
          if (newAlerts.length > 0) {
            // Show the most critical/recent one in the toast
            const alertToShow = newAlerts.find(a => a.severity === 'critical') || newAlerts[0];
            setActiveAlert(alertToShow);
            
            // Save to history
            setAlertHistory(prev => [...newAlerts, ...prev].slice(0, 50)); // keep last 50
          }
        }
      } catch (err) {
        console.error("Failed to check smart alerts:", err);
      }
    };

    // Run immediately, then every 60 seconds
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 60000);
    
    return () => clearInterval(interval);
  }, [savedLocalities, prefs]); // Re-run if saved localities change

  return (
    <AlertContext.Provider value={{ alertHistory, clearAlertHistory: () => setAlertHistory([]) }}>
      {children}
      <NotificationToast alert={activeAlert} onClose={() => setActiveAlert(null)} />
    </AlertContext.Provider>
  );
}

export function useAlerts() {
  return useContext(AlertContext);
}
