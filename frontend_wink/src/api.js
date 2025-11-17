const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const getData = () => JSON.parse(localStorage.getItem('mockUploads') || '{}');
const saveData = (data) => localStorage.setItem('mockUploads', JSON.stringify(data));

export const uploadFile = async (file) => {
    await delay(400);
    const uploads = getData();
    const id = Date.now().toString();
    uploads[id] = { id, name: file?.name || 'mock.txt', shots: [], style: null };
    saveData(uploads);
    return { id };
};

export const getShots = async (uploadId) => {
    await delay(300);
    const uploads = getData();
    return uploads[uploadId] || { id: uploadId, shots: [] };
};

export const addShot = async (uploadId, shotData) => {
    await delay(200);
    const uploads = getData();
    const upload = uploads[uploadId];
    if (!upload) return { error: 'Upload not found' };

    const newShot = {
        id: Date.now().toString(),
        order: upload.shots.length + 1,
        text: shotData.text || 'Новый шот',
        prompt: 'Описание кадра...',
        negative_prompt: 'Без дефектов...',
        time: shotData.time || '13',
        params: { яркость: 1, контраст: 1, детализация: 1 },
        imageUrl: `https://picsum.photos/seed/${Date.now()}/400/200`, // тестовое изображение
        versions: [],
    };
    upload.shots.push(newShot);
    saveData(uploads);
    return newShot;
};

export const deleteShot = async (uploadId, shotId) => {
    await delay(200);
    const uploads = getData();
    const upload = uploads[uploadId];
    upload.shots = upload.shots.filter((s) => s.id !== shotId);
    saveData(uploads);
    return { success: true };
};

export const regenerateShot = async (uploadId, shotId) => {
    await delay(400);
    return { success: true, message: `Шот ${shotId} перегенерирован` };
};

export const finalizeShot = async (uploadId, shotId) => {
    await delay(400);
    return { success: true, message: `Шот ${shotId} зафинален` };
};

export const setStyle = async (uploadId, style) => {
    await delay(300);
    const uploads = getData();
    uploads[uploadId].style = style;
    saveData(uploads);
    return { success: true, style };
};
// Mock для регенерации всех шотов по этапу
export async function regenerateAllShots(projectId, stage) {
    console.log(`Замокано: перегенерация всех шотов проекта ${projectId} на этапе ${stage}`);
    // имитация задержки как будто идёт запрос на сервер
    return new Promise((resolve) => setTimeout(() => {
        resolve({ success: true, message: `Все шоты обновлены до этапа ${stage}` });
    }, 800));
}


export const exportStoryboard = async (uploadId, fileType) => {
    await delay(600);
    return { success: true, file: `storyboard_${uploadId}.${fileType}` };
};
