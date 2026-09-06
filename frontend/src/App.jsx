/**
 * App — Root component with client-side routing.
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ExplorePage from './pages/ExplorePage';
import CityDetailPage from './pages/CityDetailPage';
import LocalityDetailPage from './pages/LocalityDetailPage';
import ComparePage from './pages/ComparePage';
import RecommendPage from './pages/RecommendPage';
import DashboardPage from './pages/DashboardPage';

import './App.css';

import { AlertProvider } from './context/AlertContext';

export default function App() {
  return (
    <BrowserRouter>
      <AlertProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/explore" element={<ExplorePage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/recommend" element={<RecommendPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/city/:cityId" element={<CityDetailPage />} />
            <Route path="/city/:cityId/locality/:localityId" element={<LocalityDetailPage />} />
          </Routes>
        </Layout>
      </AlertProvider>
    </BrowserRouter>
  );
}
