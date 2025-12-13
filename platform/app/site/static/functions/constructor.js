(() => {
    // ------------------------------------
    // Настройки тайлов и карты
    // ------------------------------------
    const tileSize = 32;
    const tiles = [
        {id:0,color:'#ffffff'}, {id:1,color:'#00ff00'},
        {id:2,color:'#8B4513'}, {id:3,color:'#0000ff'},
        {id:4,color:'#808080'}
    ];
    let selectedTile = 1;
    const mapWidth = 20;
    const mapHeight = 15;
    let mapMatrix = [];
    let graphics;
    let phaserGame;

    // -------------------------------
    // Создание пустой карты
    // -------------------------------
    function createEmptyMap(width,height){
        return Array.from({length:height},()=>Array(width).fill(0));
    }

    // -------------------------------
    // Рисование карты
    // -------------------------------
    function drawMap(){
        graphics.clear();
        for(let y=0;y<mapHeight;y++){
            for(let x=0;x<mapWidth;x++){
                const tileId = mapMatrix[y][x];
                const color = Phaser.Display.Color.HexStringToColor(tiles[tileId].color).color;
                graphics.fillStyle(color,1);
                graphics.fillRect(x*tileSize,y*tileSize,tileSize,tileSize);
                graphics.lineStyle(1,0x000000,0.2);
                graphics.strokeRect(x*tileSize,y*tileSize,tileSize,tileSize);
            }
        }
    }

    function drawTile(pointer){
        const x = Math.floor(pointer.x/tileSize);
        const y = Math.floor(pointer.y/tileSize);
        if(x>=0 && x<mapWidth && y>=0 && y<mapHeight){
            mapMatrix[y][x] = selectedTile;
            drawMap();
        }
    }

    function getMap(){ return mapMatrix.map(row=>[...row]); }

    async function saveMap(){
        const matrix = getMap();
        const mapName = prompt("Введите название карты:");
        if(!mapName){ alert("Название обязательно!"); return; }
        console.log("Сохраняем карту:", mapName, matrix);
        alert("Карта сохранена! (пример, без backend)");
    }

    // -------------------------------
    // Палитра тайлов
    // -------------------------------
    function createPalette(container){
        container.innerHTML = '';
        const paletteDiv = document.createElement('div');
        paletteDiv.id = 'palette';
        tiles.forEach(tile=>{
            const div = document.createElement('div');
            div.classList.add('tile');
            div.style.background = tile.color;
            div.addEventListener('click',()=>{
                selectedTile = tile.id;
                document.querySelectorAll('.tile').forEach(t=>t.classList.remove('selected'));
                div.classList.add('selected');
            });
            if(tile.id===selectedTile) div.classList.add('selected');
            paletteDiv.appendChild(div);
        });
        container.appendChild(paletteDiv);

        const saveBtn = document.createElement('button');
        saveBtn.id = 'saveBtn';
        saveBtn.textContent = "Сохранить карту";
        saveBtn.addEventListener('click', saveMap);
        container.appendChild(saveBtn);
    }

    // -------------------------------
    // Инициализация Phaser
    // -------------------------------
    function initPhaser(container){
        if(phaserGame) phaserGame.destroy(true);
        mapMatrix = createEmptyMap(mapWidth,mapHeight);

        const config = {
            type: Phaser.AUTO,
            width: container.clientWidth,
            height: container.clientHeight - 70, // место под палитру
            parent: container,
            backgroundColor: '#ffffff',
            scene:{
                preload:()=>{},
                create:function(){
                    graphics = this.add.graphics();
                    drawMap();
                    this.input.on('pointerdown', pointer=>{
                        drawTile(pointer);
                        this.input.on('pointermove', drawTile);
                    });
                    this.input.on('pointerup', ()=>{
                        this.input.off('pointermove', drawTile);
                    });
                },
                update:()=>{}
            }
        };
        phaserGame = new Phaser.Game(config);
    }

    // -------------------------------
    // Переключение секций
    // -------------------------------
    function switchSection(section){
        const container = document.getElementById('gameContainer');
        container.innerHTML = '';

        document.querySelectorAll('header button').forEach(b=>b.classList.remove('active'));
        document.getElementById('btn'+section.charAt(0).toUpperCase()+section.slice(1)).classList.add('active');

        if(section==='map'){
            createPalette(container);
            initPhaser(container);
        } else if(section==='characters'){
            container.innerHTML = "<h2>Персонажи</h2><p>Здесь будут персонажи.</p>";
        } else if(section==='quests'){
            container.innerHTML = "<h2>Квесты</h2><p>Здесь будут квесты.</p>";
        } else if(section==='logic'){
            container.innerHTML = "<h2>Логика</h2><p>Редактор логики игры.</p>";
        }
    }

    document.getElementById('btnMap').addEventListener('click',()=>switchSection('map'));
    document.getElementById('btnCharacters').addEventListener('click',()=>switchSection('characters'));
    document.getElementById('btnQuests').addEventListener('click',()=>switchSection('quests'));
    document.getElementById('btnLogic').addEventListener('click',()=>switchSection('logic'));

    // -------------------------------
    // Инициализация первой секции
    // -------------------------------
    switchSection('map');

})();