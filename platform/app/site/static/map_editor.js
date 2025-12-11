// ------------------------------------
// Настройки карты
// ------------------------------------
const tileSize = 8;   // размер тайла
const mapWidth = 150;
const mapHeight = 90;

// Палитра цветов
const tiles = [
    {id:0,color:'#000000'}, {id:1,color:'#1D2B53'}, {id:2,color:'#7E2553'}, {id:3,color:'#008751'},
    {id:4,color:'#AB5236'}, {id:5,color:'#5F574F'}, {id:6,color:'#C2C3C7'}, {id:7,color:'#FFF1E8'},
    {id:8,color:'#FF004D'}, {id:9,color:'#FFA300'}, {id:10,color:'#FFEC27'}, {id:11,color:'#00E436'},
    {id:12,color:'#29ADFF'}, {id:13,color:'#83769C'}, {id:14,color:'#FF77A8'}, {id:15,color:'#FFCCAA'},
    {id:16,color:'#ffffff'}, {id:17,color:'#808080'}, {id:18,color:'#404040'}, {id:19,color:'#A0A0A0'},
    {id:20,color:'#800000'}, {id:21,color:'#008080'}, {id:22,color:'#800080'}, {id:23,color:'#808000'},
    {id:24,color:'#004080'}, {id:25,color:'#400080'}, {id:26,color:'#804000'}, {id:27,color:'#008040'},
    {id:28,color:'#408000'}, {id:29,color:'#004000'}, {id:30,color:'#202080'}, {id:31,color:'#208020'}
];

let selectedTile = 1;
let mapMatrix = Array.from({length: mapHeight}, ()=>Array(mapWidth).fill(0));
let graphics;

// ------------------------------------
// Палитра
// ------------------------------------
const paletteDiv = document.getElementById('palette');
tiles.forEach(tile=>{
    const div=document.createElement('div');
    div.classList.add('tile');
    div.style.background=tile.color;
    div.addEventListener('click',()=>{
        selectedTile=tile.id;
        document.querySelectorAll('.tile').forEach(t=>t.classList.remove('selected'));
        div.classList.add('selected');
    });
    if(tile.id===selectedTile) div.classList.add('selected');
    paletteDiv.appendChild(div);
});

// ------------------------------------
// Phaser
// ------------------------------------
const canvasWrapper = document.getElementById('canvasWrapper');
const config = {
    type: Phaser.AUTO,
    width: mapWidth*tileSize,
    height: mapHeight*tileSize,
    backgroundColor:'#ffffff',
    parent: canvasWrapper,
    scene:{preload, create, update}
};
const game = new Phaser.Game(config);
function preload(){}
function create(){
    graphics=this.add.graphics();
    drawMap();
    this.input.on('pointerdown', pointer=>{
        drawTile(pointer);
        this.input.on('pointermove', drawTile);
    });
    this.input.on('pointerup', ()=>this.input.off('pointermove', drawTile));
}
function update(){}

// ------------------------------------
// Рисуем карту
// ------------------------------------
function drawMap(){
    graphics.clear();
    for(let y=0;y<mapHeight;y++){
        for(let x=0;x<mapWidth;x++){
            const id=mapMatrix[y][x];
            const color=Phaser.Display.Color.HexStringToColor(tiles[id].color).color;
            graphics.fillStyle(color,1);
            graphics.fillRect(x*tileSize,y*tileSize,tileSize,tileSize);
            graphics.lineStyle(1,0x000000,0.05);
            graphics.strokeRect(x*tileSize,y*tileSize,tileSize,tileSize);
        }
    }
}

// ------------------------------------
// Рисуем тайл по клику
// ------------------------------------
function drawTile(pointer){
    const x=Math.floor(pointer.x/tileSize);
    const y=Math.floor(pointer.y/tileSize);
    if(x>=0 && x<mapWidth && y>=0 && y<mapHeight){
        mapMatrix[y][x]=selectedTile;
        drawMap();
    }
}

// ------------------------------------
// Сохранение
// ------------------------------------
document.getElementById('saveBtn').addEventListener('click', async ()=>{
    const name=prompt("Введите название карты (1-10 символов):");
    if(!name||name.length<1||name.length>10){ alert("Имя 1–10 символов"); return; }
    const payload={ map_name:name, matrix:mapMatrix };
    try{
        const resp=await fetch("http://localhost:8000/map/add_map/",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            credentials:"include",
            body:JSON.stringify(payload)
        });
        if(!resp.ok){ const data=await resp.json(); alert("Ошибка: "+(data.detail||"неизвестная")); return;}
        alert("Карта сохранена!");
    }catch(e){console.error(e); alert("Ошибка сети");}
});
