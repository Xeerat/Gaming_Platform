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
    let nodes = [];
    let selectedNodeId = null;
    const fileDataStore = new Map();

    function addNode() {
        const id = Date.now().toString();
        nodes.push({
            id,
            speaker: "NPC",
            name: "Персонаж",
            text: "",
            choices: []
        });
        selectNode(id);
        render();
    }

    function selectNode(id) {
        selectedNodeId = id;
        render();
    }

    function addChoice(node) {
        node.choices.push({
            text: "",
            next: null
        });
        render();
    }

    function render() {
        renderList();
        renderEditor();
    }

    function renderList() {
        const list = document.getElementById("nodeList");
        list.innerHTML = "";

        nodes.forEach(n => {
            const div = document.createElement("div");
            div.className = "card";
            div.innerText = (n.dialogName || "Новый диалог").slice(0, 30);
            div.onclick = () => selectNode(n.id);
            list.appendChild(div);
        });
    }

    function renderEditor() {
        const editor = document.getElementById("editor");
        editor.innerHTML = "";

        const node = nodes.find(n => n.id === selectedNodeId);
        if (!node) return;

        const card = document.createElement("div");
        card.className = "card";

        card.innerHTML = `
            <label>Название диалога:</label>
            <input value="${node.dialogName || ''}" 
                onchange="updateField('dialogName', this.value)" />

            <label>Имя главного персонажа:</label>
            <input value="${node.playerName || ''}" 
                onchange="updateField('playerName', this.value)" />

            <label>Имя NPC:</label>
            <input value="${node.npcName || ''}" 
                onchange="updateField('npcName', this.value)" />

            <label>Текст NPC:</label>
            <textarea onchange="updateField('npcText', this.value)">
    ${node.npcText || ''}
            </textarea>

            <label>Текст игрока:</label>
            <textarea onchange="updateField('playerText', this.value)">
    ${node.playerText || ''}
            </textarea>

            <button class="button" onclick="addChoiceToCurrent()">
                Добавить вариант
            </button>
        `;

        (node.dialogFlow || []).forEach((c, i) => {
            const div = document.createElement("div");
            div.className = "choice";

            div.innerHTML = `
                <label>Кто говорит:</label>
                <select onchange="updateFlow(${i}, 'speaker', this.value)">
                    <option value="npc" ${c.speaker==='npc'?'selected':''}>NPC</option>
                    <option value="player" ${c.speaker==='player'?'selected':''}>Игрок</option>
                </select>

                <label>Текст:</label>
                <input value="${c.text}" 
                    placeholder="Реплика"
                    onchange="updateFlow(${i}, 'text', this.value)" />
            `;

            card.appendChild(div);
        });

        editor.appendChild(card);
    }

    function updateFlow(index, field, value) {
        const node = nodes.find(n => n.id === selectedNodeId);
        if (!node) return;

        if (!node.dialogFlow) node.dialogFlow = [];

        node.dialogFlow[index][field] = value;

        renderEditor();
    }

    function updateField(field, value) {
        const node = nodes.find(n => n.id === selectedNodeId);
        if (!node) return;

        node[field] = value;
        renderEditor(); 
    }

    function addChoiceToCurrent() {
        const node = nodes.find(n => n.id === selectedNodeId);
        if (!node) return;

        if (!node.dialogFlow) node.dialogFlow = [];

        node.dialogFlow.push({
            speaker: "npc",
            text: ""
        });

        renderEditor();
    }

    function updateChoice(index, field, value) {
        const node = nodes.find(n => n.id === selectedNodeId);
        if (!node) return;

        node.choices[index][field] = value;
        renderEditor();
    }

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

        const payload = {
            map_name: mapName,
            data: matrix
        };

        try {
            const response = await fetch("/maps/add_map/", {
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

            alert("Карта сохранена!");
        } catch(e){
            console.error(e);
            alert("Ошибка сети");
        }
    }

    async function saveSprite(){
        const matrix = getMap();
        const spriteName = prompt("Введите название спрайта:");
        if(!spriteName){ alert("Название обязательно!"); return; }

        const payload = {
            sprite_name: spriteName,
            data: matrix
        };

        try {
            const response = await fetch("/sprites/add_sprite/", {
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

            alert("Спрайт сохранён!");
        } catch(e){
            console.error(e);
            alert("Ошибка сети");
        }
    }

    // -------------------------------
    // Палитра тайлов с слайдером
    // -------------------------------
    function createPalette(container, flag){
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
        if (flag === "map")
        {
            saveBtn.id = 'saveMapBtn';
            saveBtn.textContent = "Сохранить";
            saveBtn.addEventListener('click', saveMap);
            container.appendChild(saveBtn);
        }
        else if (flag === "sprite")
        {
            saveBtn.id = 'saveSpriteBtn';
            saveBtn.textContent = "Сохранить";
            saveBtn.addEventListener('click', saveSprite);
            container.appendChild(saveBtn);
        }
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
    // Хранилище логики
    // -------------------------------
    let logicData = {
        functions: []
    };

    // -------------------------------
    // Добавление триггера
    // -------------------------------
    function addFunction() {
        logicData.functions.push({
            id: Date.now().toString(),
            category: "player",
            type: "movement",
            params: {}
        });

        renderFunctions();
    }

    // -------------------------------
    // Список триггеров
    // -------------------------------
    function renderFunctions() {
        const list = document.getElementById("functionList");
        list.innerHTML = "";

        logicData.functions.forEach((f, i) => {
            const div = document.createElement("div");
            div.className = "card";
            div.innerText = `${f.category || "?"} → ${f.type || "?"}`;

            div.onclick = () => {
                selectedFunctionIndex = i;
                renderFunctionEditor();
            };

            list.appendChild(div);
        });
    }

    // -------------------------------
    // Редактор триггера
    // -------------------------------
    let selectedFunctionIndex = null;

    function renderFunctionEditor() {
        const editor = document.getElementById("functionEditor");
        const f = logicData.functions[selectedFunctionIndex];
        if (!f) return;

        editor.innerHTML = `
            <h3>${f.category}</h3>
            <label>Тип функции</label>
            <select onchange="updateFunction('type', this.value)">
                ${getFunctionOptions(f.category, f.type)}
            </select>

            <div id="functionParams"></div>
        `;

        renderFunctionParams(f);
    }

    
    function renderFunctionParams(f) {
        const div = document.getElementById("functionParams");
        if (!div) return;

        div.innerHTML = "";

        // 🚶 ХОДЬБА
        if (f.type === "movement") {
            div.innerHTML = `
                <label>Имя спрайта</label>
                <input value="${f.params.sprite || ''}" 
                    onchange="updateParam('sprite', this.value)" />

                <label>Управление</label>
                <select onchange="updateParam('control', this.value)">
                    <option value="wasd">WASD</option>
                    <option value="arrows">Стрелки</option>
                </select>

                <label>Скорость</label>
                <input type="number" value="${f.params.speed || 100}" 
                    onchange="updateParam('speed', this.value)" />
            `;
        }

        // 💬 NPC
        if (f.type === "npc") {
            div.innerHTML = `
                <label>Подтип</label>
                <select onchange="updateParam('subtype', this.value)">
                    <option value="dialog">Диалог</option>
                </select>

                <label>Условие</label>
                <input value="near+key" disabled />

                <label>Кнопка</label>
                <input value="${f.params.key || 'E'}"
                    onchange="updateParam('key', this.value)" />

                <label>Диалог</label>
                <input onchange="updateParam('dialog', this.value)" />

                <label>Игрок</label>
                <input onchange="updateParam('player', this.value)" />

                <label>NPC</label>
                <input onchange="updateParam('npc', this.value)" />
            `;
        }

        // 🚧 ОБЪЕКТ
        if (f.type === "object") {
            div.innerHTML = `
                <label>Подтип</label>
                <select onchange="updateParam('subtype', this.value)">
                    <option value="block">Блокирование</option>
                </select>

                <label>Условие</label>
                <input value="collision" disabled />

                <label>Игрок</label>
                <input onchange="updateParam('player', this.value)" />

                <label>Объект</label>
                <input onchange="updateParam('object', this.value)" />
            `;
        }
    }

    // -------------------------------
    // Варианты функций
    // -------------------------------
    function getFunctionOptions(category, selected) {
        if (category === "player") {
            return `
                <option value="movement" ${selected==='movement'?'selected':''}>Ходьба</option>
                <option value="npc" ${selected==='npc'?'selected':''}>Взаимодействие с NPC</option>
                <option value="object" ${selected==='object'?'selected':''}>Взаимодействие с объектом</option>
            `;
        }

        if (category === "npc") {
            return `
                <option value="dialog">Диалог</option>
                <label>NPC</label>
                <input onchange="updateParam('npc', this.value)" />
                <label>Объект</label>
                <input onchange="updateParam('object', this.value)" />
            `;
        }

        if (category === "object") {
            return `
                <option value="block">Блокировка</option>
                <label>NPC</label>
                <input onchange="updateParam('npc', this.value)" />
                <label>Объект</label>
                <input onchange="updateParam('object', this.value)" />
            `;
        }

        return `<option value="">--</option>`;
    }

    async function saveFunctions() {
        // защита
        if (!logicData.functions || logicData.functions.length === 0) {
            alert("Нет функций для сохранения!");
            return;
        }

        const payload = {
            functions: logicData.functions
        };

        try {
            const response = await fetch("/logic/save/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(payload)
            });

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                alert("Ошибка: " + (data.detail || "неизвестная ошибка"));
                return;
            }

            alert("Функции успешно сохранены!");
        } catch (e) {
            console.error(e);
            alert("Ошибка сети");
        }
    }

    // -------------------------------
    // Параметры действия
    // -------------------------------
    function renderActionParams(t) {
        const div = document.getElementById("actionParams");

        if (t.action.type === "dialog") {
            div.innerHTML = `
                <label>ID ноды:</label>
                <input value="${t.action.nodeId || ''}" 
                    onchange="updateAction('nodeId', this.value)" />
            `;
        }

        if (t.action.type === "music") {
            div.innerHTML = `
                <label>Файл:</label>
                <input value="${t.action.src || ''}" 
                    onchange="updateAction('src', this.value)" />
            `;
        }
    }

    // -------------------------------
    // Обновление данных
    // -------------------------------
    function updateFunction(field, value) {
        const f = logicData.functions[selectedFunctionIndex];

        f[field] = value;

        // если меняется тип — сбрасываем параметры
        if (field === "type") {
            f.params = {};
        }

        renderFunctions();
        renderFunctionEditor();
    }

    function updateParam(field, value) {
        logicData.functions[selectedFunctionIndex].params[field] = value;
    }

    function runFunctions(event) {
        logicData.functions.forEach(fn => {

            //  ХОДЬБА
            if (fn.type === "movement") {
                if (event.type === "movement") {
                    applyMovement(fn.params, event);
                }
            }

            // NPC взаимодействие
            if (fn.type === "npc") {
                if (
                    event.type === "npcInteraction" &&
                    event.npc === fn.params.npc &&
                    event.player === fn.params.player
                ) {
                    if (event.key === fn.params.key) {
                        startDialog(fn.params.dialog);
                    }
                }
            }

            //  ОБЪЕКТЫ
            if (fn.type === "object") {
                if (
                    event.type === "collision" &&
                    event.object === fn.params.object &&
                    event.player === fn.params.player
                ) {
                    blockMovement(event);
                }
            }
        });
    }

    function createFunction(category) {
        const fn = {
            id: Date.now().toString(),
            category,
            type: null,
            params: {},
            action: {}
        };

        logicData.functions.push(fn);

        selectedFunctionIndex = logicData.functions.length - 1;

        renderFunctions();
        renderFunctionEditor();
    }

    function showFunctionCategoryPicker() {
        const editor = document.getElementById("functionEditor");

        editor.innerHTML = `
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button class="category-btn" onclick="createFunction('player')">🎮 Игрок</button>
                <button class="category-btn" onclick="createFunction('npc')">💬 NPC</button>
                <button class="category-btn" onclick="createFunction('object')">📦 Объект</button>
            </div>
        `;
    }

    async function handleReload() {
        const fileManager = document.getElementById('fileManager');
        if (!fileManager) return;

        try {
            const mapsRes = await fetch('/maps/get_all_maps/', { credentials: 'include' });
            if (!mapsRes.ok) return window.location.href = '/auth/login/';
            const maps = await mapsRes.json();

            const spritesRes = await fetch('/sprites/get_all_sprites/', { credentials: 'include' });
            if (!spritesRes.ok) return window.location.href = '/auth/login/';
            const sprites = await spritesRes.json();

            //  Загружаем логику для каждого спрайта
            const spritesWithLogic = await Promise.all(
                sprites.map(async (sprite) => {
                    try {
                        const res = await fetch(`/sprites/get_sprite_logic/${sprite.sprite_name}/`, {
                            credentials: 'include'
                        });

                        if (res.ok) {
                            const blocks = await res.json();

                            const main = blocks.find(b => b.name === 'main') || blocks[0];

                            return {
                                ...sprite,
                                functions:
                                    main?.functions ??
                                    main?.trigger_config ??
                                    []
                            };
                        }
                    } catch (e) {
                        console.warn('Не загрузилась логика для', sprite.sprite_name, e);
                    }

                    return {
                        ...sprite,
                        functions: []
                    };
                })
            );

            const allFiles = [
                ...maps.map(m => ({ ...m, fileType: 'map' })),
                ...spritesWithLogic.map(s => ({ ...s, fileType: 'sprite' }))
            ];

            renderFileList(fileManager, allFiles);
            setTimeout(setupDragAndDrop, 50);
        } catch (error) {
            window.location.href = '/auth/login/';
        }
    }

    document.getElementById('reloadBtn').addEventListener('click', handleReload);

    // -------------------------------

    window.addNode = addNode;
    window.addChoiceToCurrent = addChoiceToCurrent;
    window.updateField = updateField;
    window.updateChoice = updateChoice;
    window.updateAction = updateAction; 
    window.addFunction = addFunction;
    window.updateFunction = updateFunction;
    window.updateParam = updateParam;
    window.saveFunctions = saveFunctions;
    window.showFunctionCategoryPicker = showFunctionCategoryPicker;
    window.createFunction = createFunction;

    function renderFileList(container, files) {
        let filesContainer = container.querySelector('.files-container');
        if (!filesContainer) {
            filesContainer = document.createElement('div');
            filesContainer.className = 'files-container';
            
            const reloadBtn = container.querySelector('.reload');
            if (reloadBtn) {
                container.insertBefore(filesContainer, reloadBtn);
            } else {
                container.appendChild(filesContainer);
            }
        }
        
        filesContainer.innerHTML = '';

        files.forEach(file => {

            const fileCard = document.createElement('div');
            fileCard.className = 'file-card';
            fileCard.setAttribute('draggable', 'true');
            
            const uniqueId = `file-${file.fileType}-${file.id}`;
            fileCard.id = uniqueId;
            fileCard.dataset.fileId = file.id;
            fileCard.dataset.fileType = file.fileType;
            
            const fileName = file.mapname || file.name || file.sprite_name || 'Без названия';
            fileCard.dataset.fileName = fileName;
            

            fileDataStore.set(uniqueId, file);

            const icon = file.fileType === 'map' ? '🗺️' : '🎨';
            
            fileCard.innerHTML = `
                <div class="file-icon">${icon}</div>
                <div class="file-name" title="${fileName}">${fileName}</div>
            `;

            fileCard.addEventListener('click', () => {
                const file = fileDataStore.get(uniqueId);
                handleFileSelect(file);
            });

            filesContainer.appendChild(fileCard);
        });
    }

    function updateAction(field, value) {
        const t = logicData.functions[selectedFunctionIndex];
        if (!t || !t.action) return;

        t.action[field] = value;

        renderActionParams(t);
    }
    
    function handleFileSelect(file) {
        switch (file.fileType) {

            case 'map':
                activeScene.mapId = file.id;
                break;

            case 'sprite':
                logicData.functions = file.functions || [];

                // сброс выделения (под новую систему)
                selectedFunctionIndex = null;

                addSpriteToScene(file);
                break;

            case 'music':
                activeScene.music = file.url;
                break;
        }
    }
    

    function addSpriteToScene(file) {
        const obj = {
            id: Date.now().toString(),
            assetId: file.id,
            x: 100,
            y: 100,
            scale: 1
        };

        activeScene.objects.push(obj);

        renderScene();
    }

    let activeScene = {
        mapId: null,
        objects: [],
        music: null
    };

    let selectedObject = null;
    function renderScene() {
        const container = document.getElementById('sceneContent');

        if (!activeScene.mapId) {
            container.innerHTML = "<p>Выбери карту</p>";
            return;
        }

        container.innerHTML = `<div id="scenePhaser"></div>`;

        const mapFile = [...fileDataStore.values()]
            .find(f => f.fileType === 'map' && f.id === activeScene.mapId);

        if (!mapFile) {
            container.innerHTML = "<p>Карта не найдена</p>";
            return;
        }

        initScenePhaser(document.getElementById('scenePhaser'), mapFile.data);
    }

    function buildSpriteTexture(scene, file) {
        const size = 4;

        const g = scene.make.graphics({ x: 0, y: 0, add: false });

        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;

        // 1. ищем границы (убираем пустоту)
        for (let y = 0; y < file.data.length; y++) {
            for (let x = 0; x < file.data[y].length; x++) {
                const c = file.data[y][x].color;

                if (c && c !== '#ffffff') {
                    minX = Math.min(minX, x);
                    minY = Math.min(minY, y);
                    maxX = Math.max(maxX, x);
                    maxY = Math.max(maxY, y);
                }
            }
        }

        if (maxX === -Infinity) return; // пустой спрайт

        // 2. рисуем только нужную часть
        for (let y = minY; y <= maxY; y++) {
            for (let x = minX; x <= maxX; x++) {
                const c = file.data[y][x].color;

                if (!c || c === '#ffffff') continue;

                const color = Phaser.Display.Color.HexStringToColor(c).color;

                g.fillStyle(color, 1);
                g.fillRect(
                    (x - minX) * size,
                    (y - minY) * size,
                    size,
                    size
                );
            }
        }

        const key = `sprite_${file.id}`;

        if (scene.textures.exists(key)) return;

        g.generateTexture(
            key,
            (maxX - minX + 1) * size,
            (maxY - minY + 1) * size
        );

        g.destroy();
    }

    function initScenePhaser(container, map) {
        if (phaserGame) phaserGame.destroy(true);
        if (!map || !map.length) return;

        const config = {
            type: Phaser.AUTO,
            width: map[0].length * tileSize,
            height: map.length * tileSize,
            parent: container,
            backgroundColor: '#000000',

            scene: {
                preload: function () {
                    if (activeScene.music) {
                        this.load.audio('bgMusic', activeScene.music);
                    }
                },

                create: function () {

                    if (activeScene.music) {
                        const music = this.sound.add('bgMusic', {
                            loop: true,
                            volume: 0.5
                        });
                        music.play();

                        this._bgMusic = music; // сохраним ссылку
                    }

                    this.input.once('pointerdown', () => {
                    if (this._bgMusic && !this._bgMusic.isPlaying) {
                        this._bgMusic.play();
                    }
                });

                    const g = this.add.graphics();

                    // ---- рисуем карту ----
                    for (let y = 0; y < map.length; y++) {
                        for (let x = 0; x < map[y].length; x++) {
                            const color = Phaser.Display.Color
                                .HexStringToColor(map[y][x].color).color;

                            g.fillStyle(color, 1);
                            g.fillRect(
                                x * tileSize,
                                y * tileSize,
                                tileSize,
                                tileSize
                            );
                        }
                    }

                    // генерируем текстуры спрайтов
                    activeScene.objects.forEach(obj => {
                        const file = [...fileDataStore.values()]
                            .find(f => f.id === obj.assetId);

                        if (file && !this.textures.exists(`sprite_${file.id}`)) {
                            buildSpriteTexture(this, file);
                        }
                    });

                    // ---- рисуем объекты ----
                    activeScene.objects.forEach(obj => {

                        const file = [...fileDataStore.values()]
                            .find(f => f.id === obj.assetId && f.fileType === 'sprite');

                        if (!file) return;

                        const sprite = this.add.image(obj.x, obj.y, `sprite_${file.id}`);
                        sprite.setScale(obj.scale || 1);

                        sprite.setInteractive();

                        obj._phaserRef = sprite;

                        
                        sprite.on('pointerdown', () => {
                            selectedObject = obj;
                            dragging = true;
                            renderObjectEditor();
                        });

                        this.input.on('pointermove', (pointer) => {
                            if (!dragging || !selectedObject) return;

                            selectedObject.x = pointer.x;
                            selectedObject.y = pointer.y;

                            syncObject(selectedObject);
                        });

                        this.input.on('pointerup', () => {
                            dragging = false;
                            selectedObject = null;
                        });
                    }); 

                } 
            } 
        };

        phaserGame = new Phaser.Game(config);
    }

    function updateObject(field, value){
        if(!selectedObject) return;

        selectedObject[field] = field === 'scale' || field === 'x' || field === 'y'
            ? parseFloat(value)
            : value;

        syncObject(selectedObject);
    }

    function deleteObject(){
        if(!selectedObject) return;

        // 1. удалить Phaser sprite
        if(selectedObject._phaserRef){
            selectedObject._phaserRef.destroy();
            selectedObject._phaserRef = null;
        }

        // 2. удалить из сцены-данных
        activeScene.objects = activeScene.objects.filter(
            o => o.id !== selectedObject.id
        );

        // 3. очистить выделение
        selectedObject = null;

        // 4. перерисовать UI
        renderObjectEditor();

        // 5. ОБЯЗАТЕЛЬНО перерендер сцены (важно!)
        renderScene();
    }

    function renderObjectEditor(){
        const container = document.getElementById('objectFields');
        if(!container) return;

        if(!selectedObject){
            container.innerHTML = "<p>Ничего не выбрано</p>";
            return;
        }

        container.innerHTML = `
            <label>Scale</label>
            <input type="number" step="0.1" value="${selectedObject.scale}"
                onchange="updateObject('scale', this.value)" />

            <button onclick="deleteObject()">Удалить</button>
        `;
    }

    function syncObject(obj){
        if(!obj._phaserRef) return;

        obj._phaserRef.setPosition(obj.x, obj.y);
        obj._phaserRef.setScale(Number(obj.scale) || 1);
    }

    function runAction(action) {
        if (!phaserGame) return;

        const scene = phaserGame.scene.scenes[0];

        if (action.type === "music") {
            if (scene._bgMusic) {
                scene._bgMusic.stop();
            }

            scene.load.audio('bgMusic', action.src);

            scene.load.once('complete', () => {
                const music = scene.sound.add('bgMusic', {
                    loop: true,
                    volume: 0.5
                });

                music.play();
                scene._bgMusic = music;
            });

            scene.load.start();
        }

        if (action.type === "dialog") {
            startDialog(action.nodeId);
        }
    }

    function setupDragAndDrop() {
        const trash = document.getElementById('trashZone');
        const container = document.querySelector('#fileManager .files-container');
        
        if (!trash || !container) return;

        container.onmousedown = (e) => {
            const card = e.target.closest('.file-card[draggable="true"]');
            if (card) card.draggable = true;
        };

        container.addEventListener('dragstart', (e) => {
            const card = e.target.closest('.file-card[draggable="true"]');
            if (!card) return;

            e.dataTransfer.setData('text/plain', JSON.stringify({
                id: card.dataset.fileId,
                type: card.dataset.fileType,
                uniqueId: card.id,
                name: card.dataset.fileName
            }));
            e.dataTransfer.effectAllowed = 'move';
            
            setTimeout(() => card.classList.add('dragging'), 0);
        });

        container.addEventListener('dragend', (e) => {
            const card = e.target.closest('.file-card');
            if (card) {
                card.classList.remove('dragging');
                card.style.opacity = '';
            }
            trash.classList.remove('drag-over');
        });

        trash.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            trash.classList.add('drag-over');
        });

        trash.addEventListener('dragenter', (e) => {
            e.preventDefault();
            trash.classList.add('drag-over');
        });

        trash.addEventListener('dragleave', (e) => {
            if (!trash.contains(e.relatedTarget)) {
                trash.classList.remove('drag-over');
            }
        });

        trash.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            trash.classList.remove('drag-over');

            try {
                const data = JSON.parse(e.dataTransfer.getData('text/plain'));
                if (!data.id) throw new Error('Нет данных');

                if (confirm(`Удалить "${data.name}"?`)) {
                    // Формируем URL
                    const endpoint = data.type === 'map' 
                        ? `/maps/delete_map/${data.id}/` 
                        : `/sprites/delete_sprite/${data.id}/`;

                    fetch(endpoint, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include'
                    })
                    .then(res => {
                        if (!res.ok) throw new Error('Ошибка сервера');
                        // Удаляем из DOM только если сервер ответил ОК
                        const el = document.getElementById(data.uniqueId);
                        if (el) el.remove();
                    })
                    .catch(err => {
                        alert('Не удалось удалить: ' + err.message);
                    });
                }
            } catch (err) {
            }
        });
        
    }

    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            if (document.querySelector('.file-card')) {
                setupDragAndDrop();
            }
        }, 800);
    });


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
            createPalette(document.getElementById('paletteContainer'), flag="map");
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
            createPalette(document.getElementById('paletteContainer'), flag="sprite");
            initPhaser(document.getElementById('phaserContainer'));
        } else if(section==='logic'){
            container.innerHTML = `
                <div style="display:flex; height:100%;">
                    
                    <div style="width:300px; padding:10px;">
                        <button class="button" onclick="saveFunctions()">Сохранение</button>
                        <button class="button" onclick="showFunctionCategoryPicker()">+ Добавить функцию</button>
                        <div id="functionList"></div>
                    </div>

                    <div style="flex:1; padding:10px;">
                        <h3>Конструктор функций</h3>
                        <div id="functionEditor"></div>
                    </div>

                </div>
            `;

            renderFunctions();
        } else if(section==='dialog'){
            container.innerHTML = `
                <div style="display:flex; height:100%;">
                    
                    <div style="width:250px; padding:10px; background:rgba(0,0,0,0.2);">
                        <button class="button new-replica" onclick="addNode()">Добавить диалог</button>
                        <div id="nodeList"></div>
                    </div>

                    <div style="flex:1; padding:10px;">
                        <h2>Редактор диалога</h2>
                        <div id="editor"></div>
                    </div>

                </div>
            `;
            render();
        } else if(section==='scene'){
            container.innerHTML = `
                <div style="display:flex">
                    <div id="sceneContent" style="flex:1"></div>
                    
                    <div id="objectEditor" style="width:250px; padding:10px;">
                        <h3>Объект</h3>
                        <div id="objectFields"></div>
                    </div>
                </div>

                <button id="runSceneBtn">▶ Запустить сцену</button>
            `;

            document.getElementById('runSceneBtn').onclick = renderScene;
        }
    }

    document.getElementById('btnMap').addEventListener('click',()=>switchSection('map'));
    document.getElementById('btnCharacters').addEventListener('click',()=>switchSection('characters'));
    document.getElementById('btnLogic').addEventListener('click',()=>switchSection('logic'));
    document.getElementById('btnScene').addEventListener('click', () => switchSection('scene'));
    document.getElementById('btnDialog').addEventListener('click', () => switchSection('dialog'));

    // -------------------------------
    // Инициализация первой секции
    // -------------------------------
    switchSection('map');
})();