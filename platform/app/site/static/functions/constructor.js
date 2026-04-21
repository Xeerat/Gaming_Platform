let currentAudio = null; // единственный объект аудио

function stopAudio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }
}

function playAudio(src) {
    if (!src) return;

    // если текущий объект не создан, создаём
    if (!currentAudio) {
        currentAudio = new Audio(src);
        currentAudio.loop = true;
        currentAudio.play().catch(e => console.log("Ошибка воспроизведения:", e));
    } else if (currentAudio.src !== src) {
        // если другой файл, меняем src
        currentAudio.pause();
        currentAudio.src = src;
        currentAudio.currentTime = 0;
        currentAudio.play().catch(e => console.log("Ошибка воспроизведения:", e));
    } else if (currentAudio.paused) {
        // если тот же файл, но на паузе
        currentAudio.play().catch(e => console.log("Ошибка воспроизведения:", e));
    }
}

let audioFile = null;

audioLoader.onchange = e => {
    if(e.target.files[0]) {
        audioFile = URL.createObjectURL(e.target.files[0]);
    }
};

const scene = document.getElementById("scene");
let selectedSprite = null;
let sprites = [];

// -------------------
// ПРОВЕРКА НА ВВОД
// -------------------
x.addEventListener("input", () => {
    x.value = x.value.replace(/[^0-9.-]/g,''); // оставляем только цифры, точку и минус
    updateSprite();
});
y.addEventListener("input", () => {
    y.value = y.value.replace(/[^0-9.-]/g,'');
    updateSprite();
});

// -------------------
// СПРАЙТЫ
// -------------------
function createSprite(src, x, y) {
    const img = document.createElement("img");
    img.src = src;
    img.className = "sprite";

    const sprite = { el: img, x, y, scale: 1 };
    img.style.left = x + "px";
    img.style.top = y + "px";

    img.onclick = () => selectSprite(sprite);
    scene.appendChild(img);
    sprites.push(sprite);
}

function selectSprite(sprite) {
    selectedSprite = sprite;
    x.value = sprite.x;
    y.value = sprite.y;
    scale.value = sprite.scale;
}

function updateSprite() {
    if (!selectedSprite) return;
    selectedSprite.x = +x.value;
    selectedSprite.y = +y.value;
    selectedSprite.scale = +scale.value;
    selectedSprite.el.style.left = selectedSprite.x + "px";
    selectedSprite.el.style.top = selectedSprite.y + "px";
    selectedSprite.el.style.transform = `scale(${selectedSprite.scale})`;
}

x.oninput = updateSprite;
y.oninput = updateSprite;
scale.oninput = updateSprite;
let selectedConnection = null;

scene.addEventListener("mousedown", e => {
    if (!e.target.classList.contains("sprite")) return;
    const sprite = sprites.find(s => s.el === e.target);

    const sceneRect = scene.getBoundingClientRect(); // координаты сцены
    const offsetX = (e.clientX - sprite.el.getBoundingClientRect().left) / sprite.scale;
    const offsetY = (e.clientY - sprite.el.getBoundingClientRect().top) / sprite.scale;

    function move(ev) {
        sprite.x = (ev.clientX - sceneRect.left) - offsetX;
        sprite.y = (ev.clientY - sceneRect.top) - offsetY;
        sprite.el.style.left = sprite.x + "px";
        sprite.el.style.top = sprite.y + "px";
    }

    function up() {
        window.removeEventListener("mousemove", move);
        window.removeEventListener("mouseup", up);
    }

    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
});

let spriteImage = null;
spriteLoader.onchange = e => { if(e.target.files[0]) spriteImage = URL.createObjectURL(e.target.files[0]); };
function addSprite() { if(!spriteImage) return; createSprite(spriteImage,100,100); }

let bgImage = null;
bgLoader.onchange = e => { if(e.target.files[0]) bgImage = URL.createObjectURL(e.target.files[0]); };
function setBackground() {
    if (!bgImage) return;
    scene.style.background = `url(${bgImage}) no-repeat center center`;
    scene.style.backgroundSize = "100% 100%"; // всегда растягиваем на весь экран
}

// -------------------
// ЛОГИКА
// -------------------
const logic = document.getElementById("logic");
const canvas = document.getElementById("logicCanvas");
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

window.addEventListener("resize", resizeCanvas);

let blocks = [];
let connections = [];
let draggingLine = null;

function openLogic() { logic.style.display = "block"; }

// -------------------
// ДИАЛОГОВЫЕ БЛОКИ С ВИЗУАЛЬНОЙ ЛОГИКОЙ
// -------------------
function generateId() { return 'id'+Math.random().toString(36).substr(2,9); }

let userDialog = [];

function addReplicaBlock() {
    const name = document.getElementById("charName").value || "Описание";
    const text = document.getElementById("dialogText").value;
    if(!text) return;
    const id = generateId();
    const sceneState = captureSceneState();

    // создаём визуальный блок
    const div = document.createElement("div");
    div.className="block";
    div.innerText = name+"\n"+text;
    div.style.left="100px"; 
    div.style.top="100px";

    // кнопка удаления
    const deleteBtn = document.createElement("button");
    deleteBtn.innerText = "X";
    deleteBtn.style.position = "absolute";
    deleteBtn.style.top = "0";
    deleteBtn.style.right = "0";
    div.appendChild(deleteBtn);

    const block = {
        id,
        name,
        text,
        bg: sceneState.bg,
        sprites: sceneState.sprites,
        audio: audioFile || null,
        options: []
    };
    userDialog.push(block);

    document.getElementById("charName").value="";
    document.getElementById("dialogText").value="";

    const input = document.createElement("div"); input.className="port in"; div.appendChild(input);
    const output = document.createElement("div"); output.className="port out"; div.appendChild(output);
    logic.appendChild(div);

    const obj = { el: div, input, output, x:100, y:100, blockId:id };
    blocks.push(obj);

    // обработчик удаления
    deleteBtn.onclick = (e) => {
        e.stopPropagation();
        div.remove();
        blocks = blocks.filter(b => b !== obj);
        connections = connections.filter(c => c.from !== obj && c.to !== obj);
        userDialog = userDialog.filter(b => b.id !== id);
        userDialog.forEach(b => { b.options = b.options.filter(opt => opt.targetId !== id); });
        draw();
    };

    // перетаскивание
    div.onmousedown = e=>{
        let dx=e.offsetX, dy=e.offsetY;
        function move(ev){ obj.x=ev.clientX-dx; obj.y=ev.clientY-dy; div.style.left=obj.x+"px"; div.style.top=obj.y+"px"; draw(); }
        function up(){ window.removeEventListener("mousemove",move); window.removeEventListener("mouseup",up);}
        window.addEventListener("mousemove",move);
        window.addEventListener("mouseup",up);
    }

    output.onmousedown = e=>{ e.stopPropagation(); draggingLine={from:obj}; }
    input.onmouseup = e=>{
        if(draggingLine){
            const fromBlock = userDialog.find(b => b.id === draggingLine.from.blockId);
            const toBlock = userDialog.find(b => b.id === obj.blockId);
            if(fromBlock && toBlock){
                fromBlock.options.push({
                    targetId: toBlock.id,
                    text: toBlock.text
                });
            }
            connections.push({ from: draggingLine.from, to: obj });
            draggingLine = null;
        }
    }

    document.getElementById("charName").value="";
    document.getElementById("dialogText").value="";
}

// -------------------
// Показ диалога по ID
// -------------------
const dialogBox = document.getElementById("dialogBox");
const nameEl = document.getElementById("name");
const textEl = document.getElementById("text");

function showReplicaById(blockId){
    const block = userDialog.find(b => b.id === blockId);
    if(!block) return dialogBox.style.display="none";

    // показать диалог
    dialogBox.style.display = "block";

    if(block.audio){
        playAudio(block.audio);
    } else {
        stopAudio();
    }

    // меняем фон
    applySceneState(block);

    // показываем реплику
    nameEl.innerText = block.name;
    textEl.innerText = block.text;

    // удаляем старые кнопки
    const oldBtns = dialogBox.querySelectorAll("button.dialogOption");
    oldBtns.forEach(b => b.remove());

    if(block.options.length > 0){
        block.options.forEach(opt => {
            const targetBlock = userDialog.find(b => b.id === opt.targetId);
            const btn = document.createElement("button");
            btn.className = "dialogOption";
            btn.innerText = opt.text || (targetBlock ? targetBlock.text : "Выбор");
            btn.onclick = () => showReplicaById(opt.targetId);
            dialogBox.appendChild(btn);
        });
    } else {
        const btn = document.createElement("button");
        btn.className = "dialogOption";
        btn.innerText = "Конец";
        btn.onclick = () => {
            dialogBox.style.display = "none";

            // Останавливаем музыку
            if (currentAudio) {
                currentAudio.pause();
                currentAudio.currentTime = 0;
                currentAudio = null;
            }
        };
        dialogBox.appendChild(btn);
    }
}

function playDialog(){ 
    if(userDialog.length===0) return;

    // ищем блок, у которого НЕТ входящих связей
    const targets = connections.map(c => c.to.blockId);
    const startBlock = userDialog.find(b => !targets.includes(b.id));

    showReplicaById(startBlock ? startBlock.id : userDialog[0].id);
}

document.getElementById("closeLogicBtn").onclick = () => {
    logic.style.display = "none"; // просто скрываем панель
};

// -------------------
// УДАЛЕНИЕ СОЕДИНЕНИЙ
// -------------------
let hoveredConnection = null;

canvas.addEventListener("mousemove", e => {
    hoveredConnection = null;
    connections.forEach(c => {
        const fromRect = c.from.el.getBoundingClientRect();
        const toRect = c.to.el.getBoundingClientRect();

        const x1 = fromRect.right;
        const y1 = fromRect.top + fromRect.height / 2;

        const x2 = toRect.left;
        const y2 = toRect.top + toRect.height / 2;

        // вычисляем расстояние от курсора до линии
        const dist = pointLineDistance(e.clientX, e.clientY, x1, y1, x2, y2);
        if (dist < 5) hoveredConnection = c;
    });
});

document.addEventListener("keydown", e => {
    if (e.key === "Delete" && hoveredConnection) {
        // удалить соединение из connections
        const fromBlock = userDialog.find(b => b.id === hoveredConnection.from.blockId);
        if (fromBlock) {
            fromBlock.options = fromBlock.options.filter(opt => opt.targetId !== hoveredConnection.to.blockId);
        }
        connections = connections.filter(c => c !== hoveredConnection);
        hoveredConnection = null;
    }
});

// функция для расстояния от точки до линии
function pointLineDistance(px, py, x1, y1, x2, y2) {
    const A = px - x1;
    const B = py - y1;
    const C = x2 - x1;
    const D = y2 - y1;

    const dot = A * C + B * D;
    const len_sq = C * C + D * D;
    let param = -1;
    if (len_sq !== 0) param = dot / len_sq;

    let xx, yy;

    if (param < 0) {
        xx = x1;
        yy = y1;
    } else if (param > 1) {
        xx = x2;
        yy = y2;
    } else {
        xx = x1 + param * C;
        yy = y1 + param * D;
    }

    const dx = px - xx;
    const dy = py - yy;
    return Math.sqrt(dx * dx + dy * dy);
}

// Подсветка соединения при наведении
function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);

    connections.forEach(c => {
        const fromRect = c.from.el.getBoundingClientRect();
        const toRect = c.to.el.getBoundingClientRect();

        const x1 = fromRect.right;
        const y1 = fromRect.top + fromRect.height / 2;

        const x2 = toRect.left;
        const y2 = toRect.top + toRect.height / 2;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = (c === hoveredConnection) ? "red" : "white";
        ctx.lineWidth = (c === hoveredConnection) ? 3 : 1;
        ctx.stroke();
    });
}

function captureSceneState() {
    return {
        bg: bgImage ? `url(${bgImage}) center/cover` : null,
        sprites: sprites.map(s => ({
            src: s.el.src,
            x: s.x,
            y: s.y,
            scale: s.scale
        }))
    };
}

function applySceneState(block) {
    // фон
    if (block.bg) {
        scene.style.background = block.bg;
        scene.style.backgroundSize = "100% 100%"; // растягиваем
    }

    // удалить старые спрайты
    sprites.forEach(s => s.el.remove());
    sprites = [];

    // восстановить спрайты
    block.sprites.forEach(s => {
        createSprite(s.src, s.x, s.y);
        const newSprite = sprites[sprites.length - 1];
        newSprite.scale = s.scale;
        newSprite.el.style.transform = `scale(${s.scale})`;
    });
}

function deleteSprite() {
    if (!selectedSprite) return;

    // удалить из DOM
    selectedSprite.el.remove();

    // удалить из массива
    sprites = sprites.filter(s => s !== selectedSprite);

    selectedSprite = null;
}

function resizePanels() {
    const w = window.innerWidth;

    // левая панель
    if (w > 1000) {
        assets.style.width = "200px";
    } else if (w > 700) {
        assets.style.width = (w * 0.15) + "px"; // 15% ширины
    } else {
        assets.style.width = "50px"; // минимальная ширина
    }

    // правая панель
    if (w > 1000) {
        panel.style.width = "300px";
    } else if (w > 700) {
        panel.style.width = (w * 0.2) + "px"; // 20% ширины
    } else {
        panel.style.width = "50px";
    }
}

document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("spriteLoader").addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = async function () {
            const base64 = reader.result.split(",")[1];

            robotSay("Удаляю фон ✂️");

            const res = await fetch("/robot/remove-bg", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ image: base64 })
            });

            const data = await res.json();

            if (!data.image) return;

            const imgSrc = "data:image/png;base64," + data.image;

            createSprite(imgSrc, 100, 100);
        };

        reader.readAsDataURL(file);
    });

});

function robotAction(mode) {

    if (mode === "remove_bg") {
        robotSay("Загрузи изображение ✂️");
        document.getElementById("spriteLoader").click();
        return; 
    }

    let promptText = prompt("Опиши что нужно сгенерировать:");

    if (!promptText) return;

    if (mode === "character") {
        robotSay("Генерирую персонажа 🎭");
        generateAI(promptText, "character");
    }

    if (mode === "background") {
        robotSay("Генерирую фон 🌄");
        generateAI(promptText, "background");
    }
}

// простой prompt UI
function promptUser(text) {
    return prompt(text);
}

// вызов FastAPI
async function generateAI(prompt, mode) {
    const res = await fetch("/robot/generate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ prompt, mode })
    });

    const data = await res.json();

    if (!data.image) return;

    const imgSrc = "data:image/png;base64," + data.image;

    if (mode === "background") {
        scene.style.background = `url(${imgSrc}) center/cover`;
    } else {
        createSprite(imgSrc, 100, 100);
    }
}

document.addEventListener("mousemove", e => {
    document.querySelectorAll(".pupil").forEach(pupil => {
        const rect = pupil.parentElement.getBoundingClientRect();

        const dx = e.clientX - (rect.left + rect.width / 2);
        const dy = e.clientY - (rect.top + rect.height / 2);

        const angle = Math.atan2(dy, dx);
        const radius = 3;

        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;

        pupil.style.transform = `translate(${x}px, ${y}px)`;
    });
});

setInterval(() => {
    document.querySelectorAll(".eye").forEach(eye => {
        eye.classList.add("blink");
        setTimeout(() => eye.classList.remove("blink"), 200);
    });
}, 3000 + Math.random() * 2000);

document.getElementById("robotAssistant").onclick = () => {
    const mouth = document.querySelector(".mouth");
    mouth.style.height = "12px";

    setTimeout(() => {
        mouth.style.height = "6px";
    }, 300);
};

const robot = document.getElementById("robotAssistant");
const bubble = document.getElementById("robotBubble");

function robotSay(text, duration = 2000) {
    bubble.innerText = text;
    robot.classList.add("showBubble");

    setTimeout(() => {
        robot.classList.remove("showBubble");
    }, duration);
}

function robotThinking(text = "Думаю") {
    bubble.innerText = text;
    bubble.classList.add("loadingDots");
    robot.classList.add("showBubble");
    robot.classList.add("thinking");
}

function robotDone(text = "Готово!") {
    bubble.classList.remove("loadingDots");
    robot.classList.remove("thinking");
    robotSay(text, 1500);
}

window.addEventListener("resize", resizePanels);
resizePanels();

setInterval(draw,30);