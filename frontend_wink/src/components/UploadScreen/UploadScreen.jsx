import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { UploadCloud } from 'lucide-react';
import Button from '../Common/CommonButton';
import { uploadFile } from '../../api';
import './UploadScreen.css';

export default function UploadScreen() {
    const [file, setFile] = useState(null);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleUpload = async () => {
        if (!file) return setError('Пожалуйста, выберите файл.');
        const res = await uploadFile(file);
        if (res.id) navigate(`/uploads/${res.id}`);
    };

    return (
        <motion.div
            className="upload-screen"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
        >
            <motion.h1
                className="upload-title"
                initial={{ y: -30, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.8 }}
            >
                ИИ-ГЕНЕРАТОР РАСКАДРОВКИ
            </motion.h1>

            <motion.div
                className="upload-box glassy"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.8 }}
            >
                <UploadCloud size={64} className="upload-icon" />
                <label className="file-label">
                    <input type="file" onChange={(e) => setFile(e.target.files[0])} />
                    {file ? file.name : 'Выберите файл для загрузки'}
                </label>

                <Button onClick={handleUpload} className="upload-btn">
                    Далее →
                </Button>
                {error && <p className="error">{error}</p>}
            </motion.div>
        </motion.div>
    );
}
