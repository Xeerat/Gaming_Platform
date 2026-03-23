// Обработка зоны удаления файлов
const trashZone = document.getElementById('trashZone');
trashZone.addEventListener('dragover', e => {
    e.preventDefault();
    trashZone.style.backgroundColor = 'rgba(255,0,0,0.3)';
});

trashZone.addEventListener('dragleave', () => {
    trashZone.style.backgroundColor = 'rgba(255,0,0,0.1)';
});

trashZone.addEventListener('drop', () => {
    alert('Файл удалён!');
    trashZone.style.backgroundColor = 'rgba(255,0,0,0.1)';
});

// Кнопка перезагрузки
const reloadBtn = document.getElementById('reloadBtn');
reloadBtn.addEventListener('click', () => {
    location.reload();
});

// Кнопка сохранения
const saveBtn = document.getElementById('saveBtn');
saveBtn.addEventListener('click', () => {
    alert('Сцена сохранена!');
});