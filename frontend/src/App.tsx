import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Home from './pages/Home';
import Importar from './pages/Importar';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/importar" element={<Importar />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App; 