// ==================== Глобальные переменные ====================
let scene = document.getElementById("scene");
let dialogBox = document.getElementById("dialogBox");
let nameEl = document.getElementById("name");
let textEl = document.getElementById("text");
let optionsDiv = document.getElementById("options");

let sprites = [];
let userDialog = [];
let connections = [];
let currentAudio = null;

// ==================== Аудио ====================
function stopAudio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }
}

function playAudio(src) {
    if (!src) return;
    if (!currentAudio) {
        currentAudio = new Audio(src);
        currentAudio.loop = true;
        currentAudio.play().catch(e => console.log("Audio error:", e));
    } else if (currentAudio.src !== src) {
        currentAudio.pause();
        currentAudio.src = src;
        currentAudio.currentTime = 0;
        currentAudio.play().catch(e => console.log("Audio error:", e));
    } else if (currentAudio.paused) {
        currentAudio.play().catch(e => console.log("Audio error:", e));
    }
}

// ==================== Спрайты ====================
function createSprite(src, x, y, scale = 1) {
    const img = document.createElement("img");
    img.src = src;
    img.className = "sprite";
    img.style.left = x + "px";
    img.style.top = y + "px";
    // Базовая ширина задаётся в CSS, здесь не трогаем
    img.style.transform = `scale(${scale})`;
    const sprite = { el: img, x, y, scale: scale };
    scene.appendChild(img);
    sprites.push(sprite);
    return sprite;
}

function applySceneState(state) {
    // фон
    if (state.currentBg) {
        scene.style.background = `url(${state.currentBg}) no-repeat center center`;
        scene.style.backgroundSize = "100% 100%";
    } else if (state.bg) {
        scene.style.background = state.bg;
        scene.style.backgroundSize = "100% 100%";
    }
    // удаляем старые спрайты
    sprites.forEach(s => s.el.remove());
    sprites = [];
    // создаём новые
    (state.sceneSpritesData || []).forEach(s => {
        createSprite(s.src, s.x, s.y, s.scale);
    });
}

// ==================== Диалог ====================
function showReplicaById(blockId) {
    const block = userDialog.find(b => b.id === blockId);
    if (!block) {
        dialogBox.style.display = "none";
        return;
    }
    dialogBox.style.display = "block";

    if (block.audio) playAudio(block.audio);
    else stopAudio();

    if (block.bg) {
        scene.style.background = block.bg;
        scene.style.backgroundSize = "100% 100%";
    }

    if (block.sprites && block.sprites.length) {
        sprites.forEach(s => s.el.remove());
        sprites = [];
        block.sprites.forEach(s => {
            createSprite(s.src, s.x, s.y, s.scale);
        });
    }

    nameEl.innerText = block.name;
    textEl.innerText = block.text;

    optionsDiv.innerHTML = "";
    if (block.options && block.options.length > 0) {
        block.options.forEach(opt => {
            const targetBlock = userDialog.find(b => b.id === opt.targetId);
            const btn = document.createElement("button");
            btn.className = "dialogOption";
            btn.innerText = opt.text || (targetBlock ? targetBlock.text : "Выбор");
            btn.onclick = () => showReplicaById(opt.targetId);
            optionsDiv.appendChild(btn);
        });
    } else {
        const endBtn = document.createElement("button");
        endBtn.className = "dialogOption";
        endBtn.innerText = "Конец";
        endBtn.onclick = () => {
            dialogBox.style.display = "none";
            stopAudio();
        };
        optionsDiv.appendChild(endBtn);
    }
}

function playDialog() {
    if (!userDialog.length) return;
    let startBlockId = null;
    if (connections && connections.length) {
        const targets = new Set(connections.map(c => c.toId || c.to?.blockId));
        const start = userDialog.find(b => !targets.has(b.id));
        startBlockId = start ? start.id : userDialog[0].id;
    } else {
        startBlockId = userDialog[0].id;
    }
    showReplicaById(startBlockId);
}

// ==================== Масштабирование сцены ====================
function resizeSceneToWindow() {
    const w = parseFloat(scene.style.width);
    const h = parseFloat(scene.style.height);
    if (isNaN(w) || isNaN(h)) return;
    const scaleX = window.innerWidth / w;
    const scaleY = window.innerHeight / h;
    const scale = Math.min(scaleX, scaleY, 1);
    scene.style.transformOrigin = "center center";
    scene.style.transform = `scale(${scale})`;
}

// ==================== Загрузка игры ====================
async function loadGame(novelId) {
    try {
        // URL согласно вашему роуту – /novels/game/{id}/data
        const res = await fetch(`/novels/game/${novelId}/data`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        userDialog = data.dialogData || [];
        connections = data.connectionsData || [];

        // Устанавливаем размеры сцены из сохранённых
        if (data.sceneWidth && data.sceneHeight) {
            scene.style.width = data.sceneWidth + "px";
            scene.style.height = data.sceneHeight + "px";
        } else {
            // fallback для старых проектов
            scene.style.width = "1280px";
            scene.style.height = "720px";
        }

        applySceneState(data);
        resizeSceneToWindow();
        window.addEventListener('resize', resizeSceneToWindow);
        playDialog();
    } catch (err) {
        console.error(err);
        alert("Ошибка загрузки игры");
    }
}

// Запуск
loadGame(novelId);