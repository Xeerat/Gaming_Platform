(() => {
    // ------------------------------------
    // Настройки тайлов и карты
    // ------------------------------------
    const tileSize = 16;
    const tiles = [
        {id:0, color:'#ffffff'}, // фон
        {id:1, color:'#4caf50'}, // зелёный
        {id:2, color:'#8bc34a'}, // светлый зелёный
        {id:3, color:'#03a9f4'}, // голубой
        {id:4, color:'#ffeb3b'},  // жёлтый
        {id:5, color:'#0a0a0a'}, // почти черный (фон)
        {id:6, color:'#1a2b2b'}, // холодный зеленовато-синий
        {id:7, color:'#2f3e46'}, // тёмный серо-синий
        {id:8, color:'#5c0000'}, // кровь (акцент)
        {id:9, color:'#3a3a3a'},  // грязный серый
        {id:10, color:'#fff0f5'}, // светло-розовый
        {id:11, color:'#ffb6c1'}, // розовый
        {id:12, color:'#ffdAB9'}, // персиковый
        {id:13, color:'#e6ccff'}, // нежный фиолетовый
        {id:14, color:'#fffacd'},  // мягкий жёлтый
        {id:15, color:'#000000'}, // фон
        {id:16, color:'#ff0000'}, // опасность
        {id:17, color:'#ff8c00'}, // энергия
        {id:18, color:'#ffff00'}, // вспышки
        {id:19, color:'#1e90ff'},  // контрастный синий
        {id:20, color:'#1b0033'}, // тёмный фиолетовый
        {id:21, color:'#4b0082'}, // индиго
        {id:22, color:'#00ffff'}, // магия (циан)
        {id:23, color:'#7fff00'}, // кислотный зелёный
        {id:24, color:'#ff00ff'},  // магический розовый
        {id:25, color:'#850e3d', custom:true} // цвет по выбору пользователя
    ];

    let selectedTile = 1;
    let currentCustomColor = '#850e3d';
    let mapWidth = 20;
    let mapHeight = 15;
    let mapMatrix = [];
    let graphics;
    let phaserGame;

    // -------------------------------
    // Функция изменения яркости
    // -------------------------------
    function adjustBrightness(hex, percent) {
        let num = parseInt(hex.slice(1), 16);
        let r = (num >> 16) + percent;
        let g = ((num >> 8) & 0x00FF) + percent;
        let b = (num & 0x0000FF) + percent;

        r = Math.max(0, Math.min(255, r));
        g = Math.max(0, Math.min(255, g));
        b = Math.max(0, Math.min(255, b));

        return "#" + (r << 16 | g << 8 | b).toString(16).padStart(6, '0');
    }

    // -------------------------------
    // Создание пустой карты
    // -------------------------------
    function createEmptyMap(width,height){
        return Array.from({length:height},()=> 
            Array.from({length:width},()=> ({
                type:'fixed',
                color: '#ffffff'
            }))
        );
    }

    // -------------------------------
    // Добавляем кнопки выбора размера карты
    // -------------------------------
    function createMapSizeButtons(container) {
        const sizes = [
            {name:'Маленькая', width:60, height:30},
            {name:'Средняя', width:90, height:30},
            {name:'Большая', width:115, height:30},
        ];

        const btnContainer = document.createElement('div');
        btnContainer.id = 'mapSizeButtons';
        container.appendChild(btnContainer);

        sizes.forEach(size=>{
            const btn = document.createElement('button');
            btn.textContent = size.name;

            btn.addEventListener('click', ()=>{
                btnContainer.querySelectorAll('button').forEach(b=>b.classList.remove('active'));
                btn.classList.add('active');

                mapWidth = size.width;
                mapHeight = size.height;

                initPhaser(document.getElementById('phaserContainer'));
            });

            btnContainer.appendChild(btn);
        });

        // По умолчанию активна средняя карта
        btnContainer.querySelector('button:nth-child(2)').classList.add('active');
    }

    // -------------------------------
    // Рисование карты
    // -------------------------------
    function drawMap(){
        graphics.clear();
        for(let y=0;y<mapHeight;y++){
            for(let x=0;x<mapWidth;x++){
                const cell = mapMatrix[y][x];
                let hexColor;

                if(cell.type === 'fixed') hexColor = cell.color;
                else if(cell.type === 'custom') hexColor = cell.color;

                const color = Phaser.Display.Color.HexStringToColor(hexColor).color;
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
            if(selectedTile === 25){
                mapMatrix[y][x] = { type: 'custom', color: currentCustomColor };
            } else {
                mapMatrix[y][x] = { type: 'fixed', color: tiles[selectedTile].color };
            }
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
    // Палитра тайлов с слайдером
    // -------------------------------
    function createPalette(container){
        const paletteDiv = document.createElement('div');
        paletteDiv.id = 'palette';
        container.appendChild(paletteDiv);

        // слайдер яркости
        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = -100;
        slider.max = 100;
        slider.value = 0;
        slider.style.width = '200px';
        slider.style.marginTop = '8px';
        slider.style.display = 'none';
        container.appendChild(slider);

        tiles.forEach(tile=>{
            const div = document.createElement('div');
            div.classList.add('tile');
            div.style.background = tile.color;

            div.addEventListener('click', ()=>{
                selectedTile = tile.id;
                document.querySelectorAll('.tile').forEach(t=>t.classList.remove('selected'));
                div.classList.add('selected');

                if(!tile.custom){
                    slider.style.display = 'block';
                    const originalColor = tile.color;
                    slider.value = 0;

                    slider.oninput = (e)=>{
                        const value = parseInt(e.target.value);
                        const newColor = adjustBrightness(originalColor, value);
                        div.style.background = newColor;
                        tile.color = newColor;
                        drawMap();
                    };
                } else {
                    slider.style.display = 'none';

                    let colorInput = document.createElement('input');
                    colorInput.type = 'color';
                    colorInput.value = currentCustomColor;
                    colorInput.style.position = 'absolute';
                    colorInput.style.left = '-9999px';
                    document.body.appendChild(colorInput);

                    colorInput.click();

                    colorInput.addEventListener('change', (e)=>{
                        currentCustomColor = e.target.value;
                        div.style.background = currentCustomColor;
                        document.body.removeChild(colorInput);
                    }, {once:true});
                }
            });

            if(tile.id===selectedTile) div.classList.add('selected');
            paletteDiv.appendChild(div);
        });

        const saveBtn = document.createElement('button');
        saveBtn.id = 'saveMapBtn';
        saveBtn.textContent = "Сохранить";
        saveBtn.addEventListener('click', saveMap);
        container.appendChild(saveBtn);
    }

    // -------------------------------
    // Инициализация Phaser
    // -------------------------------
    function initPhaser(container){
        if(phaserGame) phaserGame.destroy(true);
        mapMatrix = createEmptyMap(mapWidth,mapHeight);

        const width = mapWidth * tileSize;   
        const height = mapHeight * tileSize; 

        const config = {
            type: Phaser.AUTO,
            width: width,
            height: height,
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
                    this.input.on('pointerup', ()=>{ this.input.off('pointermove', drawTile); });
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
            container.innerHTML = `
                <div id="paletteContainer"></div>
                <div id="phaserContainer" style="height: 500px;"></div>
            `;
            createPalette(document.getElementById('paletteContainer'));
            createMapSizeButtons(document.getElementById('paletteContainer'));
            // const toolContainer = document.createElement('div');
            // toolContainer.id = 'toolContainer';
            // toolContainer.style.margin = '10px 0';

            // const drawBtn = document.createElement('button');
            // drawBtn.textContent = '✏️';
            // drawBtn.addEventListener('click', ()=> { currentTool = 'draw'; });

            // const fillBtn = document.createElement('button');
            // fillBtn.textContent = '🪣';
            // fillBtn.addEventListener('click', ()=> { currentTool = 'fill'; });

            // toolContainer.appendChild(drawBtn);
            // toolContainer.appendChild(fillBtn);

            // document.getElementById('paletteContainer').appendChild(toolContainer);
            initPhaser(document.getElementById('phaserContainer'));
        } else if(section==='characters'){
            container.innerHTML = `
                <div id="paletteContainer"></div>
                <div id="phaserContainer" style="height: 500px;"></div>
            `;
            createPalette(document.getElementById('paletteContainer'));
            initPhaser(document.getElementById('phaserContainer'));
        } else if(section==='quests'){
            container.innerHTML = "<h2>Квесты</h2><p>Здесь будут квесты.</p>";
        } else if(section==='logic'){
            container.innerHTML = "<h2>Логика</h2><p>Редактор логики игры.</p>";
        } else if(section==='dialog'){
            container.innerHTML = "<h2>Диалог</h2><p>Редактор диалогов игры.</p>";
        } else if(section==='scene'){
            container.innerHTML = `
                <div id="gameContainer"></div>
                <div id="fileManager">
                    <div id="trashZone" class="trash">🗑️</div>
                    <button id="reloadBtn" class="reload">🔄</button>
                </div>
            `;
        }
    }

    document.getElementById('btnMap').addEventListener('click',()=>switchSection('map'));
    document.getElementById('btnCharacters').addEventListener('click',()=>switchSection('characters'));
    document.getElementById('btnQuests').addEventListener('click',()=>switchSection('quests'));
    document.getElementById('btnLogic').addEventListener('click',()=>switchSection('logic'));
    document.getElementById('btnScene').addEventListener('click', () => switchSection('scene'));
    document.getElementById('btnDialog').addEventListener('click', () => switchSection('dialog'));

    // -------------------------------
    // Инициализация первой секции
    // -------------------------------
    switchSection('map');
})();