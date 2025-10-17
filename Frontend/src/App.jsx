// App.jsx
import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Navbar from "./components/Navbar";
import WelcomePage from "./components/WelcomePage";
import ChatPage from "./components/Chatpage";
import AdminPanel from "./components/AdminPanel";
import "./components/styles/globals.css";

const App = () => {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
