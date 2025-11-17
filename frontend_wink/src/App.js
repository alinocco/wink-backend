import React from 'react';
import { Routes, Route } from 'react-router-dom';
import UploadScreen from './components/UploadScreen/UploadScreen';
import ShotsScreen from './components/ShotsScreen/ShotsScreen';
import ShotDetail from './components/ShotDetail/ShotDetail';

function App() {
    return (
        <Routes>
            <Route path="/" element={<UploadScreen />} />
            <Route path="/uploads/:id" element={<ShotsScreen />} />
            <Route path="/uploads/:id/shots/:shotId" element={<ShotDetail />} />
        </Routes>
    );
}

export default App;
