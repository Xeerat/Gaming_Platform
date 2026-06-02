// game.js - полная копия логики теста из конструктора

const tileSize = 16;
let phaserGame = null;
let fileDataStore = new Map();
let logicData = { functions: [] };
let playerSprite = null;
let sceneMode = 'game';

async function loadAndRunGame(sceneId) {
    try {
        // Загружаем сцену
        const sceneRes = await fetch(`/scenes/get_scene/${sceneId}/`, { credentials: 'include' });
        if (!sceneRes.ok) throw new Error('Игра не найдена');
        const sceneData = await sceneRes.json();
        
        // Загружаем карту
        const mapRes = await fetch(`/maps/get_map/${sceneData.map_id}/`, { credentials: 'include' });
        if (!mapRes.ok) throw new Error('Карта не найдена');
        const mapData = await mapRes.json();
        
        // Загружаем все спрайты
        const spriteIds = [...new Set(sceneData.objects.map(obj => obj.assetId))];
        for (const spriteId of spriteIds) {
            const spriteRes = await fetch(`/sprites/get_sprite/${spriteId}/`, { credentials: 'include' });
            if (spriteRes.ok) {
                const spriteData = await spriteRes.json();
                
                // Загружаем логику спрайта
                const logicRes = await fetch(`/sprites/get_sprite_logic/${spriteId}/`, { credentials: 'include' });
                if (logicRes.ok) {
                    const blocks = await logicRes.json();
                    const main = blocks.find(b => b.name === 'main') || blocks[0];
                    let functionsArray = [];
                    const triggerConfig = main?.trigger_config;
                    if (triggerConfig && typeof triggerConfig === 'object') {
                        functionsArray = Object.values(triggerConfig);
                    }
                    spriteData.functions = functionsArray;
                }
                fileDataStore.set(spriteId, spriteData);
            }
        }
        
        // Собираем всю логику
        let allFunctions = [];
        for (const sprite of fileDataStore.values()) {
            if (sprite.functions) allFunctions = allFunctions.concat(sprite.functions);
        }
        logicData.functions = allFunctions;
        
        document.getElementById('loading').style.display = 'none';
        
        // Запускаем игру (как режим теста)
        startGameAsTestMode(mapData.data, sceneData.objects);
        
    } catch (error) {
        console.error(error);
        document.getElementById('loading').innerHTML = 'Ошибка: ' + error.message;
    }
}

function startGameAsTestMode(map, objects) {
    if (phaserGame) phaserGame.destroy(true);
    
    const mapWidth = map[0].length * tileSize;
    const mapHeight = map.length * tileSize;
    
    const config = {
        type: Phaser.AUTO,
        width: window.innerWidth,
        height: window.innerHeight,
        parent: 'gameContainer',
        backgroundColor: '#000000',
        physics: {
            default: 'arcade',
            arcade: { debug: false, gravity: { y: 0 } }
        },
        scene: {
            preload: function() {},
            create: function() {                
                // Рисуем карту
                const g = this.add.graphics();
                for (let y = 0; y < map.length; y++) {
                    for (let x = 0; x < map[y].length; x++) {
                        const color = Phaser.Display.Color.HexStringToColor(map[y][x].color).color;
                        g.fillStyle(color, 1);
                        g.fillRect(x * tileSize, y * tileSize, tileSize, tileSize);
                    }
                }
                g.setDepth(-1);
                
                // Отрисовка объектов
                const moveConfig = logicData.functions.find(f => f.type === 'movement');
                const playerSpriteName = moveConfig?.params?.sprite;
                
                objects.forEach(obj => {
                    const file = fileDataStore.get(obj.assetId);
                    if (!file || !file.data) return;
                    
                    if (file.sprite_name === playerSpriteName) return;
                    
                    const textureKey = buildSpriteTextureFunc(this, file);
                    if (textureKey) {
                        const sprite = this.add.sprite(obj.x, obj.y, textureKey);
                        sprite.setOrigin(0.5);
                        sprite.setScale(obj.scaleX ?? 1, obj.scaleY ?? 1);
                    }
                });
                
                initGamePlayer(this, objects);
                
                // Центрируем камеру
                this.cameras.main.centerOn(mapWidth / 2, mapHeight / 2);
            },
            update: function() {
                if (playerSprite && this.playerUpdate) {
                    this.playerUpdate();
                }
            }
        }
    };
    
    phaserGame = new Phaser.Game(config);
}

function initGamePlayer(scene, objects) {
    const moveConfig = logicData.functions.find(f => f.type === 'movement');
    if (!moveConfig) {
        console.warn('No movement config');
        return;
    }
    
    const speed = moveConfig.params?.speed || 200;
    const controlType = moveConfig.params?.control || 'wasd';
    const playerSpriteName = moveConfig.params?.sprite;
    
    // Находим объект игрока
    const playerObj = objects.find(o => {
        const file = fileDataStore.get(o.assetId);
        return file?.sprite_name === playerSpriteName;
    });
    
    const playerFile = playerObj ? fileDataStore.get(playerObj.assetId) : null;
    
    // Центр карты
    const mapWidth = scene.physics.world.bounds.width;
    const mapHeight = scene.physics.world.bounds.height;
    const centerX = mapWidth / 2;
    const centerY = mapHeight / 2;
    
    if (playerFile) {
        const textureKey = buildSpriteTextureFunc(scene, playerFile);
        playerSprite = scene.add.sprite(playerObj?.x || centerX, playerObj?.y || centerY, textureKey);
    } else {
        playerSprite = scene.add.rectangle(centerX, centerY, 32, 32, 0xff0000);
    }
    
    playerSprite.setOrigin(0.5);
    scene.physics.add.existing(playerSprite);
    playerSprite.body.setCollideWorldBounds(true);
    
    // Управление
    scene.input.keyboard.enabled = true;
    if (controlType === 'arrows') {
        const cursors = scene.input.keyboard.createCursorKeys();
        scene.controlKeys = { up: cursors.up, down: cursors.down, left: cursors.left, right: cursors.right };
    } else {
        scene.controlKeys = scene.input.keyboard.addKeys({
            up: Phaser.Input.Keyboard.KeyCodes.W,
            down: Phaser.Input.Keyboard.KeyCodes.S,
            left: Phaser.Input.Keyboard.KeyCodes.A,
            right: Phaser.Input.Keyboard.KeyCodes.D
        });
    }
    
    // Блокирующие объекты
    const blockers = logicData.functions.filter(f => f.type === 'object').map(f => f.params);
    const colliderList = [];
    
    blockers.forEach(params => {
        const obj = objects.find(o => {
            const file = fileDataStore.get(o.assetId);
            return file?.sprite_name === params.object;
        });
        
        if (obj) {
            const col = scene.add.rectangle(obj.x, obj.y, 32, 32);
            scene.physics.add.existing(col);
            col.body.setImmovable(true);
            col.body.setAllowGravity(false);
            col.visible = false;
            colliderList.push(col);
        }
    });
    
    if (colliderList.length) {
        scene.physics.add.collider(playerSprite, colliderList);
    }
    
    // Диалоговые NPC
    const dialogNPCs = logicData.functions.filter(f => f.type === 'npc').map(f => f.params);
    scene.npcList = [];
    
    dialogNPCs.forEach(params => {
        const obj = objects.find(o => {
            const file = fileDataStore.get(o.assetId);
            return file?.sprite_name === params.npc;
        });
        
        if (obj) {
            const file = fileDataStore.get(obj.assetId);
            if (file) {
                const textureKey = buildSpriteTextureFunc(scene, file);
                const npc = scene.add.sprite(obj.x, obj.y, textureKey);
                npc.setOrigin(0.5);
                npc.setData('dialogId', params.dialog);
                npc.setData('interactKey', params.key || 'E');
                scene.npcList.push(npc);
            }
        }
    });
    
    // Обновление кадра с диалогами
    scene.playerUpdate = function() {
        const keys = scene.controlKeys;
        playerSprite.body.setVelocity(0);
        if (keys.left.isDown) playerSprite.body.setVelocityX(-speed);
        else if (keys.right.isDown) playerSprite.body.setVelocityX(speed);
        if (keys.up.isDown) playerSprite.body.setVelocityY(-speed);
        else if (keys.down.isDown) playerSprite.body.setVelocityY(speed);
        
        // Проверка диалогов
        for (const npc of scene.npcList) {
            const distance = Phaser.Math.Distance.Between(playerSprite.x, playerSprite.y, npc.x, npc.y);
            const key = npc.getData('interactKey') || 'E';
            const interactKey = scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes[key.toUpperCase()]);
            
            if (distance < 80 && Phaser.Input.Keyboard.JustDown(interactKey)) {
                const dialogId = npc.getData('dialogId');
                if (dialogId) {
                    startDialog(dialogId);
                    break;
                }
            }
        }
    };
}

function buildSpriteTextureFunc(scene, file) {
    const size = 4;
    const g = scene.make.graphics({ x: 0, y: 0, add: false });
    
    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;
    
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
    
    if (maxX === -Infinity) return null;
    
    for (let y = minY; y <= maxY; y++) {
        for (let x = minX; x <= maxX; x++) {
            const c = file.data[y][x].color;
            if (!c || c === '#ffffff') continue;
            const color = Phaser.Display.Color.HexStringToColor(c).color;
            g.fillStyle(color, 1);
            g.fillRect((x - minX) * size, (y - minY) * size, size, size);
        }
    }
    
    const key = `sprite_${file.id}`;
    if (!scene.textures.exists(key)) {
        g.generateTexture(key, (maxX - minX + 1) * size, (maxY - minY + 1) * size);
    }
    g.destroy();
    return key;
}
let currentDialog = null;
let currentStep = 0;

function startDialog(dialogId) {
    console.log("=== startDialog CALLED ===", dialogId);
    
    // Ищем диалог в nodes (если есть) или в logicData
    let dialog = null;
    
    // Проверяем глобальные nodes (если есть из конструктора)
    if (typeof nodes !== 'undefined' && nodes) {
        dialog = nodes.find(n => n.id === dialogId || n.dialogName === dialogId);
    }
    
    if (!dialog) {
        const npcFunction = logicData.functions.find(f => 
            f.type === 'npc' && f.params.dialog === dialogId
        );
        if (npcFunction?.params?.dialogData) {
            dialog = npcFunction.params.dialogData;
        }
    }
    
    if (!dialog) {
        console.error("Dialog not found:", dialogId);
        return;
    }
    
    // Создаём dialogFlow из npcText/playerText если нет
    if ((!dialog.dialogFlow || dialog.dialogFlow.length === 0) && dialog.npcText) {
        dialog.dialogFlow = [
            { speaker: "npc", text: dialog.npcText }
        ];
        if (dialog.playerText) {
            dialog.dialogFlow.push({ speaker: "player", text: dialog.playerText });
        }
    }
    
    if (!dialog.dialogFlow || dialog.dialogFlow.length === 0) {
        console.error("Dialog has no content!");
        return;
    }
    
    currentDialog = dialog;
    currentStep = 0;
    
    showDialogStep();
}

function showDialogStep() {
    if (!currentDialog) return;
    
    const dialogFlow = currentDialog.dialogFlow || [];
    
    if (currentStep >= dialogFlow.length) {
        closeDialog();
        return;
    }
    
    const step = dialogFlow[currentStep];
    const isNPC = step.speaker === 'npc';
    const speakerName = isNPC ? (currentDialog.npcName || 'NPC') : (currentDialog.playerName || 'Игрок');
    const text = step.text || '...';
    
    let dialogBox = document.getElementById('dialogBox');
    if (!dialogBox) {
        dialogBox = document.createElement('div');
        dialogBox.id = 'dialogBox';
        dialogBox.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            max-width: 600px;
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 20px;
            border-radius: 10px;
            font-family: monospace;
            z-index: 10000;
            cursor: pointer;
            text-align: center;
        `;
        document.body.appendChild(dialogBox);
    }
    
    dialogBox.innerHTML = `
        <div style="margin-bottom: 10px;"><strong>${speakerName}:</strong></div>
        <div>${text}</div>
        <div style="margin-top: 10px; font-size: 12px; color: #888;">Нажмите чтобы продолжить</div>
    `;
    dialogBox.style.display = 'block';
    
    const newHandler = () => {
        currentStep++;
        showDialogStep();
    };
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