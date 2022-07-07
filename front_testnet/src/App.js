import logo from './logo.svg';
import './App.css';
import Navbar from './components/Navbar';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import Warp from './pages/warp';
import Claim from './pages/claim';
import Status from './pages/status';
import Popup from './components/popup';
import Home from './pages/home';
import { useState } from 'react';
function App() {
  const [metamask_trigger, set_metamask_trigger] = useState(false);
  const [address, set_address] = useState("");
  return (
    <Router >
     <Navbar trigger={metamask_trigger} set_trigger={set_metamask_trigger} address={address} />
     <Popup trigger={metamask_trigger} set_trigger={set_metamask_trigger} set_address={set_address}/>
     <Routes>
       <Route path="/" exact element={<Home/>} />
       <Route path="/claim" element={<Claim/>} />
       <Route path="/status" element={<Status/>} />
       <Route path="/warp" element={<Warp/>} />
     </Routes>
    </Router>
    
  );
}

export default App;
