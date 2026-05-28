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
    let mapWidth = 90;
    let mapHeight = 30;
    let mapMatrix = [];
    let graphics;
    let phaserGame;
    let nodes = [];
    let selectedNodeId = null;
    let currentLogicTarget = null;
    const fileDataStore = new Map();
    let selectedSpriteType = 'NPC';

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
            sprite_type: selectedSpriteType,
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

            const typeWrapper = document.createElement('div');
            typeWrapper.style.cssText = 'margin-top: 10px; display: flex; align-items: center; gap: 8px;';

            const typeLabel = document.createElement('label');
            typeLabel.textContent = 'Тип:';
            typeLabel.style.fontSize = '14px';

            const typeSelect = document.createElement('select');
            typeSelect.innerHTML = `
                <option value="NPC" ${selectedSpriteType === 'NPC' ? 'selected' : ''}>NPC</option>
                <option value="Player" ${selectedSpriteType === 'Player' ? 'selected' : ''}>Player</option>
                <option value="Object" ${selectedSpriteType === 'Object' ? 'selected' : ''}>Object</option>
            `;
            typeSelect.style.padding = '4px 8px';
            typeSelect.style.borderRadius = '4px';
            typeSelect.style.border = '1px solid #555';
            typeSelect.style.background = '#222';
            typeSelect.style.color = '#fff';

            typeSelect.addEventListener('change', (e) => {
                selectedSpriteType = e.target.value;
            });

            typeWrapper.appendChild(typeLabel);
            typeWrapper.appendChild(typeSelect);
            container.appendChild(typeWrapper);
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
                update: function() {
                    if (sceneMode === 'test' && this.playerUpdate) {
                        this.playerUpdate();
                    }
                }
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
            params: {},
            action: {}
        });

        renderFunctions();
    }

    // -------------------------------
    // Список триггеров
    // -------------------------------
    function renderFunctions() {
        const list = document.getElementById("functionList");
        if (!list) {
            console.warn("functionList not found in DOM - skipping render");
            return;  // Просто выходим если элемента нет
        }
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
        if (!editor) {
            console.warn("functionEditor not found - skipping");
            return;
        }
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
        return `<option value="">--</option>`;
    }

    async function saveFunctions() {
    if (!logicData.functions || logicData.functions.length === 0) {
        alert("Нет функций для сохранения!");
        return;
    }

    // Группируем функции по спрайтам
    const functionsBySprite = {};
    
        for (const fn of logicData.functions) {
            let targetSpriteName = null;
            
            if (fn.type === "movement") {
                targetSpriteName = fn.params.sprite;
            } else if (fn.type === "npc") {
                targetSpriteName = fn.params.npc;
                
                // ← ДОБАВЛЯЕМ: Сохраняем диалог по названию
                const dialogName = fn.params.dialog;
                if (dialogName) {
                    // Ищем диалог по названию в nodes
                    const dialog = nodes.find(n => n.dialogName === dialogName);
                    if (dialog) {
                        // Сохраняем полный диалог в params
                        fn.params.dialogData = dialog;
                        console.log(`Saved dialog "${dialogName}" to function`);
                    } else {
                        console.warn(`Dialog "${dialogName}" not found in nodes`);
                    }
                }
                
            } else if (fn.type === "object") {
                targetSpriteName = fn.params.object;
            }
            
            if (!targetSpriteName) {
                console.warn(`Нет target спрайта для функции ${fn.type}`, fn);
                continue;
            }
            
            if (!functionsBySprite[targetSpriteName]) {
                functionsBySprite[targetSpriteName] = [];
            }
            
            // Очищаем функцию от лишнего
            const cleanedFunction = {
                category: fn.category,
                type: fn.type,
                params: fn.params,
                action: fn.action || {}
            };
            
            functionsBySprite[targetSpriteName].push(cleanedFunction);
        }
        
        // Сохраняем для каждого спрайта
        for (const [spriteName, functions] of Object.entries(functionsBySprite)) {
            const triggerConfig = {};
            functions.forEach((fn, index) => {
                triggerConfig[`func_${index}`] = fn;
            });
            
            const payload = {
                sprite_name: spriteName,
                name: "main",
                trigger_config: triggerConfig,
                dialog_config: {},
                dialog_role: "system"
            };
            
            console.log(`Saving for ${spriteName}:`, payload);
            
            try {
                const response = await fetch("/sprites/update_sprite_logic/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    const data = await response.json();
                    console.error("Server error:", data);
                    throw new Error(data.detail || "ошибка");
                }
                
                console.log(`Saved for ${spriteName}`);
            } catch (e) {
                console.error(e);
                alert(`Ошибка: ${e.message}`);
                return;
            }
        }
        
        alert("Логика сохранена!");
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

    function createFunction() {
        const fn = {
            id: Date.now().toString(),
            category: "player",
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
                <button class="category-btn" onclick="createFunction()">🎮 Добавить функцию</button>
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

            // Загружаем логику для каждого спрайта
            const spritesWithLogic = await Promise.all(
                sprites.map(async (sprite) => {
                    try {
                        const res = await fetch(`/sprites/get_sprite_logic/${sprite.sprite_name}/`, {
                            credentials: 'include'
                        });
                        if (res.ok) {
                            const blocks = await res.json();
                            const main = blocks.find(b => b.name === 'main') || blocks[0];
                            
                            // Превращаем объект обратно в массив
                            let functionsArray = [];
                            const triggerConfig = main?.trigger_config;
                            
                            if (triggerConfig && typeof triggerConfig === 'object') {
                                // Объект с ключами func_0, func_1 и т.д.
                                functionsArray = Object.values(triggerConfig);
                            }
                            
                            console.log(`Functions for ${sprite.sprite_name}:`, functionsArray);
                            
                            return {
                                ...sprite,
                                functions: functionsArray
                            };
                        }
                    } catch (e) {
                        console.warn('Не загрузилась логика для', sprite.sprite_name, e);
                    }
                    return { ...sprite, functions: [] };
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
    window.deleteObject = deleteObject;

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
                selectedFunctionIndex = null;
                
                // Рисуем функции ТОЛЬКО если мы во вкладке логики
                if (document.getElementById("functionList")) {
                    renderFunctions();
                }
                
                addSpriteToScene(file);
                break;
        }
    }
    

    function addSpriteToScene(file) {
        console.log("=== addSpriteToScene CALLED ===");
        console.log("file.functions:", file.functions);
        
        // ОБЪЯВЛЯЕМ переменную functionsArray
        let functionsArray = [];
        
        if (file.functions) {
            if (Array.isArray(file.functions)) {
                functionsArray = file.functions;
            } else if (typeof file.functions === 'object') {
                functionsArray = Object.values(file.functions);
            }
        }
        
        console.log("functionsArray:", functionsArray);

        if (functionsArray.length > 0) {
            logicData.functions = functionsArray;
            console.log("logicData.functions updated:", logicData.functions);
        }
        
        // СОХРАНЯЕМ функции в глобальную переменную
        if (functionsArray.length > 0) {
            logicData.functions = functionsArray;
            if (document.getElementById("functionList")) {
                renderFunctions();
            }
        }
        
        if (sceneMode === 'test') {
            alert("Нельзя добавлять объекты в режиме теста!");
            return;
        }

        const obj = {
            id: Date.now().toString(),
            assetId: file.id,
            x: 100,
            y: 100,
            scaleX: 1,
            scaleY: 1
        };
        
        console.log("Created object:", obj);
        console.log("activeScene.objects before push:", activeScene.objects.length);
        
        activeScene.objects.push(obj);
        
        console.log("activeScene.objects after push:", activeScene.objects.length);
        console.log("Calling renderScene()...");
        
        renderScene();
    }

    let activeScene = {
        mapId: null,
        objects: [],
        music: null
    };

    let selectedObject = null;
    function renderScene() {
        console.log("=== renderScene CALLED ===");
        console.log("activeScene.mapId:", activeScene.mapId);
        console.log("activeScene.objects.length:", activeScene.objects.length);
        
        const container = document.getElementById('sceneContent');
        if (!container) {
            console.error("sceneContent not found!");
            return;
        }

        if (!activeScene.mapId) {
            console.log("No map selected");
            container.innerHTML = "<p>Выбери карту</p>";
            return;
        }

        container.innerHTML = `<div id="scenePhaser"></div>`;

        const mapFile = [...fileDataStore.values()]
            .find(f => f.fileType === 'map' && f.id === activeScene.mapId);

        console.log("mapFile:", mapFile);
        
        if (!mapFile) {
            console.error("Map not found!");
            container.innerHTML = "<p>Карта не найдена</p>";
            return;
        }

        console.log("Calling initScenePhaser...");
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

    let dragging = false;

    function initScenePhaser(container, map) {
        console.log("=== initScenePhaser CALLED ===");
        console.log("container exists:", !!container);
        console.log("map length:", map?.length);
        console.log("sceneMode:", sceneMode);
        if (phaserGame) phaserGame.destroy(true);
        if (!map || !map.length) return;

        const config = {
            type: Phaser.AUTO,
            width: map[0].length * tileSize,
            height: map.length * tileSize,
            parent: container,
            backgroundColor: '#000000',
            transparent: false,

            physics: {
                default: 'arcade',
                arcade: { 
                    debug: false,
                    gravity: { y: 0 }
                }
            },

            scene: {
                preload: function () {
                    if (activeScene.music) {
                        this.load.audio('bgMusic', activeScene.music);
                    }
                },

                create: function () {
                    console.log("=== SCENE CREATE ===");
                    
                    if (activeScene.music) {
                        const music = this.sound.add('bgMusic', {
                            loop: true,
                            volume: 0.5
                        });
                        music.play();
                        this._bgMusic = music;
                    }

                    this.input.once('pointerdown', () => {
                        if (this._bgMusic && !this._bgMusic.isPlaying) {
                            this._bgMusic.play();
                        }
                    });

                    // Рисуем карту
                    const g = this.add.graphics();
                    console.log("Drawing map...");
                    
                    for (let y = 0; y < map.length; y++) {
                        for (let x = 0; x < map[y].length; x++) {
                            const color = Phaser.Display.Color
                                .HexStringToColor(map[y][x].color).color;
                            g.fillStyle(color, 1);
                            g.fillRect(x * tileSize, y * tileSize, tileSize, tileSize);
                        }
                    }
                    g.setDepth(-1);
                    console.log("Map drawn");
                    
                    if (sceneMode === 'build') {
                        setupBuildMode(this);
                    } else if (sceneMode === 'test') {
                        loadFunctionsFromSceneObjects();
                        setupTestMode(this);
                    }
                },

                update: function() {
                    if (sceneMode === 'test' && this.playerUpdate) {
                        this.playerUpdate();
                    }
                }
            }
        };

        phaserGame = new Phaser.Game(config);
    }

    function updateObject(field, value){

        if (sceneMode === 'test') return;

        if(!selectedObject) return;

        const numericFields = ['scaleX', 'scaleY', 'x', 'y'];

        selectedObject[field] = numericFields.includes(field)
            ? parseFloat(value)
            : value;

        syncObject(selectedObject);
    }

    function setUniformScale(value){
        if (sceneMode === 'test') return;

        selectedObject.scaleX = value;
        selectedObject.scaleY = value;
        syncObject(selectedObject);
    }


    function deleteObject(){

        if (sceneMode === 'test') {
            alert(" Нельзя удалять объекты в режиме теста!");
            return;
        }

        if(!selectedObject) {
            console.warn("Нет выбранного объекта для удаления");
            return;
        }

        console.log(" Удаляем объект:", selectedObject.id);

        const scene = phaserGame?.scene?.scenes?.[0];
        
        if (scene && selectedObject._phaserRef) {
            selectedObject._phaserRef.destroy();
            console.log("🎮 Спрайт Phaser уничтожен");
        }

        activeScene.objects = activeScene.objects.filter(o => o.id !== selectedObject.id);
        
        selectedObject = null;
        
        renderObjectEditor();
        
        if (sceneMode === 'test') {
            renderScene();
        }
    }

    function renderObjectEditor(){
        const container = document.getElementById('objectFields');
        if(!container) return;

        if (sceneMode === 'test') {
            container.innerHTML = `
                <p style="color:#888; font-style:italic;">
                    Редактирование отключено в режиме теста
                </p>
            `;
            return;
        }

        if(!selectedObject){
            container.innerHTML = "<p>Ничего не выбрано</p>";
            return;
        }

        container.innerHTML = `
            <div style="margin-bottom:10px;">
                <strong>Параметры объекта</strong><br>
                X: <input type="number" id="objX" value="${Math.round(selectedObject.x)}" style="width:60px">
                Y: <input type="number" id="objY" value="${Math.round(selectedObject.y)}" style="width:60px">
            </div>
            <div style="margin-bottom:10px;">
                Масштаб: <input type="number" id="objScale" step="0.1" 
                    value="${selectedObject.scaleX ?? 1}" style="width:60px">
            </div>
            <button id="deleteBtn" class="button" style="background:#dc3545;">🗑️ Удалить объект</button>
        `;

        document.getElementById('deleteBtn').onclick = deleteObject;
        document.getElementById('objX').onchange = (e) => updateObject('x', e.target.value);
        document.getElementById('objY').onchange = (e) => updateObject('y', e.target.value);
        document.getElementById('objScale').onchange = (e) => {
            const val = parseFloat(e.target.value) || 1;
            updateObject('scaleX', val);
            updateObject('scaleY', val);
        };
    }

    function syncObject(obj){
        const sprite = obj._phaserRef;
        if(!sprite) return;

        sprite.setPosition(obj.x, obj.y);

        const sx = obj.scaleX ?? 1;
        const sy = obj.scaleY ?? 1;

        if (isFinite(sx) && isFinite(sy) && sx > 0 && sy > 0) {
            sprite.setScale(Number(sx), Number(sy));
        }
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

    let isDragDropSetup = false;

    function setupDragAndDrop() {
        if (isDragDropSetup) return;
        isDragDropSetup = true;

        const trash = document.getElementById('trashZone');
        const container = document.querySelector('#fileManager .files-container');
        
        if (!trash || !container) {
            isDragDropSetup = false;
            return;
        }

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

    let sceneMode = 'build';        // 'build' | 'test'
    let playerSprite = null;        // ссылка на игрока в тест-режиме
    let testSceneRef = null;        // ссылка на сцену Phaser для доступа извне

    function setSceneMode(mode) {
         sceneMode = mode;
    
        // Обновляем кнопки
        document.getElementById('modeBuildBtn')?.classList.toggle('active', mode==='build');
        document.getElementById('modeTestBtn')?.classList.toggle('active', mode==='test');
        
        // Скрываем/показываем панель редактора
        const objectEditor = document.getElementById('objectEditor');
        if (objectEditor) {
            objectEditor.style.display = mode === 'test' ? 'none' : 'block';
        }
        
        renderScene();
    }

    async function startTestMode() {
        
        setSceneMode('test');
    }

    function getPlayerMovementConfig() {
        return logicData.functions.find(f => 
            f.category === 'player' && f.type === 'movement'
        );
    }

    function getBlockerObjects() {
        return logicData.functions
            .filter(f => f.type === 'object')
            .map(f => f.params);
    }

    function getDialogNPCs() {
        return logicData.functions
            .filter(f => f.type === 'npc')  // ← убираем проверку на category и subtype
            .map(f => f.params);
    }

    function setupBuildMode(scene) {
        // 🔹 1. Очистка старой подсветки
        activeScene.objects.forEach(obj => {
            if (obj._highlight) {
                obj._highlight.destroy();
                delete obj._highlight;
            }
        });

        // 🔹 2. Генерация текстур
        activeScene.objects.forEach(obj => {
            const file = [...fileDataStore.values()].find(f => f.id === obj.assetId && f.fileType === 'sprite');
            if (file && !scene.textures.exists(`sprite_${file.id}`)) {
                buildSpriteTexture(scene, file);
            }  
        });

        // 🔹 3. Отрисовка объектов
        activeScene.objects.forEach(obj => {
            const file = [...fileDataStore.values()].find(f => f.id === obj.assetId && f.fileType === 'sprite');
            if (!file) return;
            const textureKey = `sprite_${file.id}`;
            if (!scene.textures.exists(textureKey)) return;

            const sprite = scene.add.sprite(obj.x, obj.y, textureKey);
            sprite.setOrigin(0.5);
            sprite.setScale(obj.scaleX ?? 1, obj.scaleY ?? 1);
            sprite.setInteractive();
            obj._phaserRef = sprite;

            // 🔹 4. Подсветка выбранного объекта
            if (obj === selectedObject) {
                const highlight = scene.add.graphics();
                highlight.lineStyle(2, 0xffffff, 1);
                highlight.strokeRect(obj.x - 18, obj.y - 18, 36, 36);
                obj._highlight = highlight;
            }

            // 🔹 5. Клик по объекту — БЕЗ renderScene()!
            sprite.on('pointerdown', () => {
                // Сначала убираем подсветку со всех объектов
                activeScene.objects.forEach(o => {
                    if (o._highlight) {
                        o._highlight.destroy();
                        delete o._highlight;
                    }
                });
                
                // Выделяем новый объект
                selectedObject = obj;
                dragging = true;
                
                // Рисуем новую рамку
                const highlight = scene.add.graphics();
                highlight.lineStyle(2, 0xffffff, 1);
                highlight.strokeRect(obj.x - 18, obj.y - 18, 36, 36);
                obj._highlight = highlight;
                
                // Обновляем панель редактора
                renderObjectEditor();
                // ❌ НЕ вызываем renderScene() здесь!
            });

            // 🔹 6. Перетаскивание — только обновление позиции
            scene.input.on('pointermove', (pointer) => {
                if (!dragging || !selectedObject) return;
                selectedObject.x = pointer.x;
                selectedObject.y = pointer.y;
                syncObject(selectedObject);
                
                // Обновляем позицию рамки, если есть
                if (selectedObject._highlight) {
                    selectedObject._highlight.clear();
                    selectedObject._highlight.lineStyle(2, 0xffffff, 1);
                    selectedObject._highlight.strokeRect(
                        selectedObject.x - 18, 
                        selectedObject.y - 18, 
                        36, 
                        36
                    );
                }
                // ❌ НЕ вызываем renderScene() здесь!
            });

            // 🔹 7. Отпускание мыши
            scene.input.on('pointerup', () => {
                dragging = false;
                // Не сбрасываем selectedObject и не вызываем renderScene()
                // Пусть объект остаётся выделенным, пока пользователь не кликнет в пустоту
            });
        });
        
        // 🔹 8. Клик по пустому месту — снимаем выделение
        scene.input.on('pointerdown', (pointer) => {
            // Если клик был не по спрайту и не по редактору
            if (!pointer.eventTarget?.closest?.('.Phaser-Canvas') && 
                !pointer.eventTarget?.closest?.('#objectEditor')) {
                return;
            }
            
            // Проверяем, был ли клик по существующему спрайту
            const hitSprite = scene.children.list.find(child => 
                child.input?.hitArea && child.input?.hitTest(pointer.x, pointer.y)
            );
            
            if (!hitSprite && !pointer.eventTarget?.closest?.('#objectEditor')) {
                // Клик по пустому месту — снимаем выделение
                if (selectedObject?._highlight) {
                    selectedObject._highlight.destroy();
                    delete selectedObject._highlight;
                }
                selectedObject = null;
                renderObjectEditor();

            }
        });
    }

    function setupTestMode(scene) {
        console.log("=== setupTestMode CALLED ===");
        console.log("logicData.functions BEFORE:", logicData.functions);
        
        loadFunctionsFromSceneObjects();
        
        console.log("logicData.functions AFTER load:", logicData.functions);
        
        // Получаем имя спрайта игрока из конфига
        const moveConfig = getPlayerMovementConfig();
        const playerSpriteName = moveConfig?.params?.sprite;
        
        // Отрисовка объектов статично (КРОМЕ спрайта игрока)
        activeScene.objects.forEach(obj => {
            const file = [...fileDataStore.values()].find(f => f.id === obj.assetId && f.fileType === 'sprite');
            if (!file) return;
            
            // ПРОПУСКАЕМ спрайт игрока - он будет создан отдельно
            if (file.sprite_name === playerSpriteName) {
                console.log("Skipping player sprite, will be created separately");
                return;
            }
            
            const textureKey = `sprite_${file.id}`;
            if (!scene.textures.exists(textureKey)) {
                buildSpriteTexture(scene, file);
            }
            
            const sprite = scene.add.sprite(obj.x, obj.y, textureKey);
            sprite.setOrigin(0.5);
            sprite.setScale(obj.scaleX ?? 1, obj.scaleY ?? 1);
            obj._phaserRef = sprite;
        });
        
        // Инициализация игрока и логики
        initTestModeLogic(scene);
    }

    function initTestModeLogic(scene) {
        console.log("=== initTestModeLogic CALLED ===");
        console.log("logicData.functions:", logicData.functions);
        
        logicData.functions.forEach((fn, i) => {
            console.log(`Function ${i}:`, fn);
            console.log(`  category: ${fn.category}, type: ${fn.type}`);
        });
        
        const moveConfig = getPlayerMovementConfig();
        console.log("moveConfig:", moveConfig);
        const speed = moveConfig?.params?.speed || 200;
        const controlType = moveConfig?.params?.control || 'wasd';
        const playerSpriteName = moveConfig?.params?.sprite;
        
        console.log("playerSpriteName:", playerSpriteName);
        console.log("All sprites in fileDataStore:", [...fileDataStore.values()].filter(f => f.fileType === 'sprite').map(f => ({ id: f.id, name: f.sprite_name })));
        
        // Создаём игрока
        const playerObj = activeScene.objects.find(o => {
            const file = [...fileDataStore.values()].find(f => f.id === o.assetId && f.fileType === 'sprite');
            console.log("Checking object:", o.assetId, "file:", file?.sprite_name, "vs needed:", playerSpriteName);
            return file?.sprite_name === playerSpriteName;
        });
        
        console.log("playerObj found:", playerObj);
    
        const playerFile = playerObj ? [...fileDataStore.values()].find(f => f.id === playerObj.assetId) : null;
        console.log("playerFile:", playerFile);
        
        if (playerFile) {
            buildSpriteTexture(scene, playerFile);
            playerSprite = scene.add.sprite(playerObj?.x || 100, playerObj?.y || 100, `sprite_${playerFile.id}`);
            console.log("playerSprite created:", playerSprite);
        } else {
            playerSprite = scene.add.rectangle(100, 100, 32, 32, 0x00ff00);
            console.log("playerSprite created (fallback rectangle):", playerSprite);
        }
        
        playerSprite.setOrigin(0.5);
        scene.physics.add.existing(playerSprite);
        playerSprite.body.setCollideWorldBounds(true);
        console.log("playerSprite physics added, body:", playerSprite.body);
        
        // Управление
        scene.input.keyboard.enabled = true;
        if (controlType === 'arrows') {
            scene.cursors = scene.input.keyboard.createCursorKeys();
            scene.controlKeys = { up: scene.cursors.up, down: scene.cursors.down, left: scene.cursors.left, right: scene.cursors.right };
        } else {
            scene.controlKeys = scene.input.keyboard.addKeys({
                up: Phaser.Input.Keyboard.KeyCodes.W,
                down: Phaser.Input.Keyboard.KeyCodes.S,
                left: Phaser.Input.Keyboard.KeyCodes.A,
                right: Phaser.Input.Keyboard.KeyCodes.D
            });
        }
        console.log("controlKeys set:", scene.controlKeys);

        // Коллизии с блокирующими объектами
        const blockers = getBlockerObjects();
        logicData.functions.forEach((fn, i) => {
            console.log(`Function ${i} params:`, fn.params);
        });
        console.log("Blockers found:", blockers);
        const colliderList = [];

        blockers.forEach(params => {
            console.log("Looking for blocker object:", params.object);
            
            const obj = activeScene.objects.find(o => {
                const file = [...fileDataStore.values()].find(f => f.id === o.assetId && f.fileType === 'sprite');
                return file?.sprite_name === params.object;
            });
            
            console.log("Found blocker obj:", obj);
            
            if (obj) {
                // Создаём невидимый коллайдер
                const col = scene.add.rectangle(obj.x, obj.y, 32, 32);
                scene.physics.add.existing(col);
                col.body.setImmovable(true);
                col.body.setAllowGravity(false);
                col.visible = false;
                colliderList.push(col);
                console.log("Blocker added at", obj.x, obj.y);
            }
        });

        if (colliderList.length) {
            scene.physics.add.collider(playerSprite, colliderList);
            console.log("Colliders added, count:", colliderList.length);
        } else {
            console.warn("No blockers found!");
        }
        // NPC для диалогов
        const dialogNPCs = getDialogNPCs();
        console.log("Dialog NPCs found:", dialogNPCs);
        console.log("Full dialog configs:", logicData.functions.filter(f => f.type === 'npc'));

        scene.npcList = [];
        dialogNPCs.forEach(params => {
            console.log("Processing dialog NPC:", params);
            
            const obj = activeScene.objects.find(o => {
                const file = [...fileDataStore.values()].find(f => f.id === o.assetId && f.fileType === 'sprite');
                console.log("  Looking for object with name:", params.npc, "found file:", file?.sprite_name);
                return file?.sprite_name === params.npc;
            });
            
            console.log("Found NPC object:", obj);
            
            if (obj) {
                const file = [...fileDataStore.values()].find(f => f.id === obj.assetId);
                if (file) {
                    buildSpriteTexture(scene, file);
                    const npc = scene.add.sprite(obj.x, obj.y, `sprite_${file.id}`);
                    npc.setOrigin(0.5);
                    npc.setData('dialogId', params.dialog);
                    npc.setData('interactKey', params.key || 'E');
                    scene.npcList.push(npc);
                    console.log("NPC added to scene.npcList, dialogId:", params.dialog);
                }
            }
        });

        console.log("Total NPCs in scene.npcList:", scene.npcList.length);

        // Функция обновления кадра
        scene.playerUpdate = function() {
            const keys = scene.controlKeys;
            playerSprite.body.setVelocity(0);
            
            if (keys.left.isDown) playerSprite.body.setVelocityX(-speed);
            else if (keys.right.isDown) playerSprite.body.setVelocityX(speed);
            if (keys.up.isDown) playerSprite.body.setVelocityY(-speed);
            else if (keys.down.isDown) playerSprite.body.setVelocityY(speed);
            
            checkNPCInteractions(scene);
            
        };
        console.log("playerUpdate function assigned, speed:", speed);
    }

    function checkNPCInteractions(scene) {
        if (!playerSprite || !scene.npcList) return;
        
        for (const npc of scene.npcList) {
            const distance = Phaser.Math.Distance.Between(playerSprite.x, playerSprite.y, npc.x, npc.y);
            const key = npc.getData('interactKey') || 'E';
            const interactKey = scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes[key.toUpperCase()]);
            
            if (distance < 80 && Phaser.Input.Keyboard.JustDown(interactKey)) {
                const dialogId = npc.getData('dialogId');
                if (dialogId) {
                    startDialog(dialogId); // ваша существующая функция
                    break;
                }
            }
        }
    }


    function loadFunctionsFromSceneObjects() {
        console.log("=== loadFunctionsFromSceneObjects CALLED ===");
        
        // Собираем функции со всех спрайтов на сцене
        let allFunctions = [];
        
        for (const obj of activeScene.objects) {
            const file = [...fileDataStore.values()].find(f => f.id === obj.assetId && f.fileType === 'sprite');
            if (file && file.functions && file.functions.length > 0) {
                console.log(`Found functions for ${file.sprite_name}:`, file.functions);
                allFunctions = allFunctions.concat(file.functions);
            }
        }
        
        if (allFunctions.length > 0) {
            logicData.functions = allFunctions;
            console.log("logicData.functions updated with", allFunctions.length, "functions");
        } else {
            console.warn("No functions found in scene objects");
        }
    }


    let currentDialog = null;
    let currentStep = 0;

    function startDialog(dialogId) {
        console.log("=== startDialog CALLED ===", dialogId);
        
        // Ищем диалог
        let dialog = nodes.find(n => n.id === dialogId || n.dialogName === dialogId);
        
        if (!dialog) {
            const npcFunction = logicData.functions.find(f => 
                f.type === 'npc' && f.params.dialog === dialogId
            );
            if (npcFunction?.params?.dialogData) {
                dialog = npcFunction.params.dialogData;
                console.log("Found dialog in function data:", dialog);
            }
        }
        
        if (!dialog) {
            console.error("Dialog not found:", dialogId);
            return;
        }
        
        console.log("Dialog object:", dialog);
        console.log("dialogFlow:", dialog.dialogFlow);
        console.log("dialogFlow length:", dialog.dialogFlow?.length);
        console.log("npcText:", dialog.npcText);
        console.log("playerText:", dialog.playerText);
        
        // Если нет dialogFlow, но есть npcText - создаём простой диалог
        if ((!dialog.dialogFlow || dialog.dialogFlow.length === 0) && dialog.npcText) {
            console.log("Creating simple dialog from npcText");
            dialog.dialogFlow = [
                { speaker: "npc", text: dialog.npcText }
            ];
            if (dialog.playerText) {
                dialog.dialogFlow.push({ speaker: "player", text: dialog.playerText });
            }
        }
        
        if (!dialog.dialogFlow || dialog.dialogFlow.length === 0) {
            console.error("Dialog has no content!");
            // Создаём тестовый диалог
            dialog.dialogFlow = [
                { speaker: "npc", text: dialog.npcText || "Привет!" },
                { speaker: "player", text: dialog.playerText || "Здравствуй!" }
            ];
        }
        
        currentDialog = dialog;
        currentStep = 0;
        
        showDialogStep();
    }

    function showDialogStep() {
        if (!currentDialog) return;
        
        const dialogFlow = currentDialog.dialogFlow || [];
        
        // Если диалог закончился - закрываем
        if (currentStep >= dialogFlow.length) {
            closeDialog();
            return;
        }
        
        const step = dialogFlow[currentStep];
        const isNPC = step.speaker === 'npc';
        const speakerName = isNPC ? (currentDialog.npcName || 'NPC') : (currentDialog.playerName || 'Игрок');
        const text = step.text || '...';
        
        // Создаём или обновляем окно диалога
        let dialogBox = document.getElementById('dialogBox');
        if (!dialogBox) {
            dialogBox = document.createElement('div');
            dialogBox.id = 'dialogBox';
            dialogBox.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 20px;
                right: 20px;
                background: rgba(0,0,0,0.9);
                color: white;
                padding: 20px;
                border-radius: 10px;
                font-family: monospace;
                z-index: 10000;
                cursor: pointer;
            `;
            document.body.appendChild(dialogBox);
        }
        
        dialogBox.innerHTML = `
            <div style="margin-bottom: 10px;"><strong>${speakerName}:</strong></div>
            <div>${text}</div>
            <div style="margin-top: 10px; font-size: 12px; color: #888;">Нажмите чтобы продолжить</div>
        `;
        dialogBox.style.display = 'block';
        
        // Убираем старый обработчик и добавляем новый
        const newHandler = () => {
            currentStep++;
            showDialogStep();
        };
        
        // Заменяем обработчик
        const oldHandler = dialogBox.onclick;
        dialogBox.onclick = newHandler;
    }

    function closeDialog() {
        const dialogBox = document.getElementById('dialogBox');
        if (dialogBox) {
            dialogBox.style.display = 'none';
        }
        currentDialog = null;
        currentStep = 0;
    }


    let currentPreviewUrl = null;

    async function uploadPreview() {
        // Создаём скрытый input для выбора файла
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/upload/file/', {
                    method: 'POST',
                    credentials: 'include',
                    body: formData
                });
                
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.detail || 'Ошибка загрузки');
                }
                
                const data = await response.json();
                currentPreviewUrl = data.url;
                alert('Превью загружено! Теперь можно сохранить сцену.');
                
            } catch (e) {
                console.error(e);
                alert('Ошибка загрузки превью: ' + e.message);
            }
        };
        
        input.click();
    }

    async function saveCurrentScene() {
        if (!activeScene.mapId) {
            alert("Сначала выбери карту!");
            return;
        }
        
        const sceneName = prompt("Введите название сцены:");
        if (!sceneName) return;
        
        const objectsToSave = activeScene.objects.map(obj => ({
            id: obj.id,
            assetId: obj.assetId,
            x: obj.x,
            y: obj.y,
            scaleX: obj.scaleX,
            scaleY: obj.scaleY
        }));
        
        const payload = {
            scene_name: sceneName,
            map_id: activeScene.mapId,
            objects: objectsToSave,
            preview_url: currentPreviewUrl || null
        };
        
        try {
            const response = await fetch("/scenes/save_scene/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || "Ошибка сохранения");
            }
            
            const data = await response.json();
            
            if (data.updated) {
                alert(`Сцена "${sceneName}" обновлена!`);
            } else {
                alert(`Сцена "${sceneName}" сохранена!`);
                currentPreviewUrl = null; // Очищаем для следующей новой сцены
            }
            
        } catch (e) {
            console.error(e);
            alert("Ошибка: " + e.message);
        }
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
                <div style="display:flex; gap:10px; margin-bottom:10px;">
                    <button id="modeBuildBtn" class="button ${sceneMode==='build'?'active':''}">Стройка</button>
                    <button id="modeTestBtn" class="button ${sceneMode==='test'?'active':''}">Тест</button>
                    <button id="uploadPreviewBtn" class="button" style="background:#17a2b8;">🖼️ Добавить превью</button>
                    <button id="saveSceneBtn" class="button" style="background:#28a745;">💾 Сохранить сцену</button>
                </div>
                <div style="display:flex">
                    <div id="sceneContent" style="flex:1"></div>
                    <div id="objectEditor" style="width:250px; padding:10px;">
                        <h3>Объект</h3>
                        <div id="objectFields"></div>
                    </div>
                </div>
            `;

            document.getElementById('modeBuildBtn').onclick = () => setSceneMode('build');
            document.getElementById('modeTestBtn').onclick = () => setSceneMode('test');
            document.getElementById('uploadPreviewBtn').onclick = () => uploadPreview();
            document.getElementById('saveSceneBtn').onclick = () => saveCurrentScene();

            renderScene();
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


