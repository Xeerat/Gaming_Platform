let currentPage = 0;
const limit = 6;

async function loadNovels() {
    const skip = currentPage * limit;
    const res = await fetch(`/novels/public/?skip=${skip}&limit=${limit}`);
    if (!res.ok) {
        console.error('Ошибка загрузки');
        return;
    }
    const data = await res.json();
    const grid = document.getElementById('novelsGrid');
    grid.innerHTML = '';
    if (data.items.length === 0 && currentPage === 0) {
        grid.innerHTML = '<div class="empty-message">Пока нет новелл.</div>';
    } else {
        for (let n of data.items) {
            const card = document.createElement('div');
            card.className = 'novel-card';
            const previewUrl = n.preview ? n.preview : '/static/default_preview.png';
            card.innerHTML = `
                <div class="preview" style="background-image: url('${previewUrl}');"></div>
                <div class="title">${escapeHtml(n.title)}</div>
                <button class="play-btn" onclick="startGame(${n.id})">▶ Играть</button>
            `;
            grid.appendChild(card);
        }
    }
    document.getElementById('prevPageBtn').disabled = currentPage === 0;
    document.getElementById('nextPageBtn').disabled = data.items.length < limit;
    document.getElementById('pageInfo').innerText = `Страница ${currentPage + 1}`;
}