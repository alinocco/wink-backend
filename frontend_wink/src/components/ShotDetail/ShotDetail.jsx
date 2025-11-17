import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Button from '../Common/CommonButton';
import './ShotDetail.css';

export default function ShotDetail() {
    const { id, shotId } = useParams();
    const navigate = useNavigate();

    // моковые данные
    const [image, setImage] = useState('/mock_shot.jpg');
    const [loading, setLoading] = useState(false);

    const [showHistory, setShowHistory] = useState(false);
    const [showFinalize, setShowFinalize] = useState(false);

    const [params, setParams] = useState({
        яркость: 1,
        контраст: 1,
        детализация: 1
    });

    const handleParamChange = (key, value) => {
        setParams(prev => ({
            ...prev,
            [key]: value
        }));
    };
    // мок истории версий
    const versions = [
        { id: 'v1', date: '2025-02-08 12:31', name: 'Версия 1', image: '/mock_shot.jpg' },
        { id: 'v2', date: '2025-02-08 12:40', name: 'Версия 2', image: '/mock_shot_alt.jpg' }
    ];

    const regenerate = async () => {
        setLoading(true);
        await new Promise(res => setTimeout(res, 1200));
        setImage('/mock_new.jpg');
        setLoading(false);
    };

    const finalize = async () => {
        setShowFinalize(false);
        await new Promise(res => setTimeout(res, 800));
        alert('Шот финализирован (мок)');
    };

    const rollBack = (version) => {
        setImage(version.image);
        setShowHistory(false);
    };

    return (
        <motion.div
            className="shot-detail-screen"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
        >
            <div className={'detail-header'}>
                <button className="back-btn" onClick={() => navigate(-1)}>
                    ← Назад
                </button>
                <h1 className="shot-title">Шот #{shotId}</h1>

            </div>

            <div className="shot-detail-wrapper glassy">

                {/* LEFT */}
                <div className="shot-left">
                    <div className="shot-image-box">
                        {loading ? (
                            <div className="loader">⏳ Генерация...</div>
                        ) : (
                            <img src={image} alt="shot" className="shot-detail-image" />
                        )}
                    </div>

                    <div className="shot-left-buttons">
                        <div className={'detail-buttons-row'}>
                            <Button variant="primary" onClick={regenerate}>Перегенерировать</Button>
                            <Button variant="primary" onClick={() => setShowFinalize(true)}>Финал</Button>
                        </div>
                        <div className={'detail-buttons-row'}>
                            <Button variant="secondary" onClick={() => setShowHistory(true)}>История</Button>
                        </div>

                        </div>
                    </div>

                    {/* RIGHT */}
                    <div className="shot-right">
                    <h3>Название шота</h3>
                    <input className="title-input" defaultValue="Новый шот"/>

                    <h3>Промт</h3>
                    <textarea defaultValue="Описание кадра..."/>

                    <h3>Негативный промт</h3>
                    <textarea defaultValue="Без дефектов..."/>

                    <h3>Параметры генерации</h3>
                    <div className="params-grid">
                        {Object.entries(params).map(([key, value]) => (
                            <div className="param-row" key={key}>
                                <label>{key}</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={value}
                                    onChange={e => handleParamChange(key, e.target.value)}
                                />
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* === МОДАЛКА ИСТОРИИ === */}
            {showHistory && (
                <div className="modal-backdrop">
                    <div className="modal-content history-modal">
                        <h2>История версий</h2>

                        <div className="versions-list">
                            {versions.map(v => (
                                <div key={v.id} className="version-card">
                                    <img src={v.image} alt=""/>
                                    <div className="v-info">
                                        <div className="v-name">{v.name}</div>
                                        <div className="v-date">{v.date}</div>
                                    </div>
                                    <Button variant="primary" onClick={() => rollBack(v)}>Перейти</Button>
                                </div>
                            ))}
                        </div>

                        <Button variant="danger" onClick={() => setShowHistory(false)}>Закрыть</Button>
                    </div>
                </div>
            )}

            {/* === МОДАЛКА ФИНАЛИЗАЦИИ === */}
            {showFinalize && (
                <div className="modal-backdrop">
                    <div className="modal-content confirm-modal">
                        <h3>Финализировать шот?</h3>
                        <p>После финализации изменения будут ограничены.</p>

                        <div className="modal-buttons">
                            <Button variant="primary" onClick={finalize}>Да</Button>
                            <Button variant="secondary" onClick={() => setShowFinalize(false)}>Нет</Button>
                        </div>
                    </div>
                </div>
            )}
        </motion.div>
    );
}
