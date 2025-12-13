// ------------------------------------
// Настройки персонажа
// ------------------------------------
const pixelSize = 8;   // размер одного пикселя
const charWidth = 32;   // ширина персонажа в пикселях
const charHeight = 32;  // высота персонажа в пикселях

// Палитра из 32 цветов
const colors = [
    {id: 0, color:'#000000'}, {id: 1, color:'#1D2B53'}, {id: 2, color:'#7E2553'}, {id: 3, color:'#008751'},
    {id: 4, color:'#AB5236'}, {id: 5, color:'#5F574F'}, {id: 6, color:'#C2C3C7'}, {id: 7, color:'#FFF1E8'},
    {id: 8, color:'#FF004D'}, {id: 9, color:'#FFA300'}, {id:10, color:'#FFEC27'}, {id:11, color:'#00E436'},
    {id:12, color:'#29ADFF'}, {id:13, color:'#83769C'}, {id:14, color:'#FF77A8'}, {id:15, color:'#FFCCAA'},
    {id:16, color:'#ffffff'}, {id:17, color:'#808080'}, {id:18, color:'#404040'}, {id:19, color:'#A0A0A0'},
    {id:20, color:'#800000'}, {id:21, color:'#008080'}, {id:22, color:'#800080'}, {id:23, color:'#808000'},
    {id:24, color:'#004080'}, {id:25, color:'#400080'}, {id:26, color:'#804000'}, {id:27, color:'#008040'},
    {id:28, color:'#408000'}, {id:29, color:'#004000'}, {id:30, color:'#202080'}, {id:31, color:'#208020'}
];

let selectedColor = 1; // по умолчанию цвет 1 (темно-синий)
let charMatrix = [];
let graphics;

// ------------------------------------
// Создаём пустого персонажа
// ------------------------------------
function createEmptyCharacter(w, h){
    return Array.from({length: h}, ()=>Array(w).fill(0));
}

// ------------------------------------
// Палитра в HTML
// ------------------------------------
const paletteDiv = document.getElementById('palette');

colors.forEach(col => {
    const div = document.createElement('div');
    div.classList.add('tile');
    div.style.background = col.color;
    div.addEventListener('click', () => {
        selectedColor = col.id;
        document.querySelectorAll('.tile').forEach(t => t.classList.remove('selected'));
        div.classList.add('selected');
    });
    if(col.id === selectedColor) div.classList.add('selected');
    paletteDiv.appendChild(div);
});

// ------------------------------------
// Phaser 3 конфигурация
// ------------------------------------
const config = {
    type: Phaser.AUTO,
    width: charWidth * pixelSize,
    height: charHeight * pixelSize,
    backgroundColor: '#ffffff',
    scene: { preload, create, update }
};

const game = new Phaser.Game(config);

function preload(){}

function create(){
    graphics = this.add.graphics();
    charMatrix = createEmptyCharacter(charWidth, charHeight);
    drawCharacter();

    this.input.on('pointerdown', pointer => {
        drawPixel(pointer);
        this.input.on('pointermove', drawPixel);
    });

    this.input.on('pointerup', () => {
        this.input.off('pointermove', drawPixel);
    });
}

function update(){}

// ------------------------------------
// Рисуем персонажа
// ------------------------------------
function drawCharacter(){
    graphics.clear();
    for(let y=0; y<charHeight; y++){
        for(let x=0; x<charWidth; x++){
            const id = charMatrix[y][x];
            const color = Phaser.Display.Color.HexStringToColor(colors[id].color).color;
            graphics.fillStyle(color, 1);
            graphics.fillRect(x*pixelSize, y*pixelSize, pixelSize, pixelSize);
            graphics.lineStyle(1, 0x000000, 0.1);
            graphics.strokeRect(x*pixelSize, y*pixelSize, pixelSize, pixelSize);
        }
    }
}

// ------------------------------------
// Рисуем пиксель по клику
// ------------------------------------
function drawPixel(pointer){
    const x = Math.floor(pointer.x / pixelSize);
    const y = Math.floor(pointer.y / pixelSize);
    if(x>=0 && x<charWidth && y>=0 && y<charHeight){
        charMatrix[y][x] = selectedColor;
        drawCharacter();
    }
}

// ------------------------------------
// Получить копию матрицы
// ------------------------------------
function getCharacter(){
    return charMatrix.map(row => [...row]);
}

// ------------------------------------
// Сохранение персонажа через API
// ------------------------------------
document.getElementById('saveBtn').addEventListener('click', async () => {
    const matrix = getCharacter();
    const name = prompt("Введите имя персонажа (1-10 символов):");

    if(!name || name.length<1 || name.length>10){
        alert("Имя должно быть 1–10 символов");
        return;
    }

    const payload = { character_name: name, matrix };

    try {
        const response = await fetch("http://localhost:8000/characters/add_character/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(payload)
        });

        if(!response.ok){
            const data = await response.json();
            alert("Ошибка: " + (data.detail || "неизвестная"));
            return;
        }

        alert("Персонаж сохранён!");
    } catch(e){
        console.error(e);
        alert("Ошибка сети");
    }
});
