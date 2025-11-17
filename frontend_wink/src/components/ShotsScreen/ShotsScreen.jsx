import React, { useEffect, useState } from 'react';
import { FaCog } from 'react-icons/fa'; // иконка шестерёнки

import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Button from '../Common/CommonButton';
import { getShots, addShot, deleteShot, regenerateAllShots } from '../../api';
import './ShotsScreen.css';

export default function ShotsScreen() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [shots, setShots] = useState([]);
    const [stage, setStage] = useState('sketch');
    const [style, setStyle] = useState('unknow');

    const [modalOpen, setModalOpen] = useState(false);
    const [pendingStage, setPendingStage] = useState(null);
    const [sidebarOpen, setSidebarOpen] = useState(false); // для сайдбара

    const refresh = async () => {
        const data = await getShots(id);
        setShots(data.shots);
    };
    const [exportModal, setExportModal] = useState(false);

    useEffect(() => { refresh(); }, [id]);

    const handleStageClick = (newStage) => {
        if (newStage === 'sketch') {
            setStage('sketch');
        } else {
            // открываем модалку выбора стиля
            setPendingStage(newStage);
            if(style === 'unknow'){
                setModalOpen(true);
            }
            setStage(newStage);
        }
    };

    const handleStyleSelect = async (style) => {
        setModalOpen(false);
        setStyle(style)
        // перегенерация всех шотов с выбранным стилем
        await regenerateAllShots(id, stage, style);
        refresh();
    };

    useEffect(() => { refresh(); }, [id]);
    return (
        <motion.div className="shots-screen" initial={{opacity: 0}} animate={{opacity: 1}} transition={{duration: 1}}>
            <header className="header-bar">
                <div className="project-title">
                    <motion.div
                        whileHover={{rotate: 90}}
                        transition={{type: 'spring', stiffness: 300}}
                        style={{display: 'inline-block', cursor: 'pointer', marginRight: 12}}
                        onClick={() => navigate(-1)} // ← кнопка назад
                    >
                        ←
                    </motion.div>

                    Storyboard — проект {id}
                    <motion.div
                        whileHover={{rotate: 90}}
                        transition={{type: 'spring', stiffness: 300}}
                        style={{display: 'inline-block', cursor: 'pointer', marginRight: 12}}
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                    >
                        <FaCog size={28}/>
                    </motion.div>
                </div>

                <div className="controls">
                    {style !== 'unknow' && stage !== 'sketch' && (
                        <Button variant={'danger'} onClick={() => setModalOpen(true)}>Изменить стиль</Button>
                    )}
                    <Button variant="secondary" onClick={() => setExportModal(true)}>Экспорт</Button>
                </div>
            </header>
            <motion.div
                className="sidebar"
                initial={{x: -300}}
                animate={{x: sidebarOpen ? 0 : -300}}
                transition={{type: 'tween', duration: 0.3}}
            >
                <h3>Настройки проекта</h3>
                <p>Здесь будут основные настройки</p>
                <Button onClick={() => setSidebarOpen(false)}>Закрыть</Button>
            </motion.div>
            <div className="content-commands">
                <Button onClick={async () => {
                    await addShot(id, {});
                    refresh();
                }}> Добавить шот</Button>

            </div>

            <div className="shots-grid">
                {shots.length === 0 ? (
                    <div className="empty-message">✨ Нет кадров — добавь первый и начни историю!</div>
                ) : (
                    shots.map(s => (
                        <div key={s.id} className="shot-card">
                            <div className="shot-image-box" onClick={() => navigate(`/uploads/${id}/shots/${s.id}`)}>
                                {s.imageUrl ? <img src={s.imageUrl} alt={`Shot ${s.id}`} className="shot-image"/> :
                                    <div className="shot-placeholder">Нет изображения</div>}
                                <div className="shot-time">{s.time} сек</div>
                                <div className="shot-overlay"><span className="shot-id">#{s.id}</span></div>
                                <button className="delete-cross" onClick={(e) => {
                                    e.stopPropagation();
                                    deleteShot(id, s.id).then(refresh);
                                }}>×
                                </button>
                            </div>
                            <div className="shot-info">
                                <div className="shot-text">{s.text || 'Без описания'}</div>
                                <div className="shot-actions">
                                    <Button variant="secondary"
                                            onClick={() => navigate(`/uploads/${id}/shots/${s.id}`)}>Открыть</Button>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Этапы — показываем только если есть хотя бы один шот */}
            {shots.length > 0 && (
                <div className="stage-bar glassy">
                    {['sketch', 'middle', 'final'].map((s, idx) => (
                        <div key={s}
                             className={`stage-cell ${idx <= ['sketch', 'middle', 'final'].indexOf(stage) ? 'active' : ''}`}
                             onClick={() => handleStageClick(s)}
                        >
                            {s.toUpperCase()}
                        </div>
                    ))}
                </div>
            )}
            {modalOpen && (
                <div className="style-modal-backdrop" onClick={() => setModalOpen(false)}>
                    <motion.div
                        className="style-modal"
                        initial={{scale: 0.8, opacity: 0}}
                        animate={{scale: 1, opacity: 1}}
                        transition={{duration: 0.25}}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <button className="style-modal-close" onClick={() => setModalOpen(false)}>×</button>

                        <h2>Выберите стиль для {pendingStage?.toUpperCase()}</h2>

                        <div className="style-cards">
                            {[
                                {name: 'Реализм', img: 'https://picsum.photos/seed/r1/320/180'},
                                {name: 'Мультяшный', img: 'https://picsum.photos/seed/r2/320/180'},
                                {name: 'Пастель', img: 'https://picsum.photos/seed/r3/320/180'},
                                {name: 'Футуризм', img: 'https://picsum.photos/seed/r4/320/180'},
                            ].map(s => (
                                <div
                                    key={s.name}
                                    className="style-card-new"
                                    onClick={() => handleStyleSelect(s.name)}
                                >
                                    <img src={s.img} alt={s.name}/>
                                    <div className="style-card-name">{s.name}</div>
                                </div>
                            ))}
                        </div>

                        <button className="style-cancel-btn" onClick={() => setModalOpen(false)}>
                            Отмена
                        </button>
                    </motion.div>
                </div>
            )}

            {/* Модальное окно экспорта */}
            {exportModal && (
                <div className="modal-backdrop">
                    <motion.div
                        className="export-modal"
                        initial={{scale: 0.8, opacity: 0}}
                        animate={{scale: 1, opacity: 1}}
                        transition={{duration: 0.25}}
                    >
                        <button className="modal-close" onClick={() => setExportModal(false)}>×</button>

                        <h2 className="export-title">Экспорт проекта</h2>

                        <div className="export-buttons">
                            <button className="export-btn" onClick={() => alert('ZIP загружается…')}>
                                ZIP архив
                            </button>
                            <button className="export-btn" onClick={() => alert('PDF генерируется…')}>
                                PDF документ
                            </button>
                            <button className="export-btn" onClick={() => alert('DOCX создаётся…')}>
                                DOCX файл
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}

        </motion.div>
    );
}
