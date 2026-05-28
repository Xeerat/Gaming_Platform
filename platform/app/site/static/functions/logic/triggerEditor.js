import { state } from "../core/state.js";

// -------------------------------
// Добавление триггера
// -------------------------------
export function addTrigger() {
    state.logicData.triggers.push({
        type: "near+key",
        target: "",
        key: "E",
        range: 20,
        action: {
            type: "dialog",
            nodeId: ""
        }
    });

    renderTriggers();
}

// -------------------------------
// Список триггеров
// -------------------------------
export function renderTriggers() {
    const list = document.getElementById("triggerList");
    list.innerHTML = "";

    state.logicData.triggers.forEach((t, i) => {
        const div = document.createElement("div");
        div.className = "card";
        div.innerText = `${t.type} → ${t.action.type}`;

        div.onclick = () => {
            state.selectedTriggerIndex = i;
            renderTriggerEditor();
        };

        list.appendChild(div);
    });
}

// -------------------------------
// Редактор триггера
// -------------------------------
export function renderTriggerEditor() {
    const editor = document.getElementById("triggerEditor");
    editor.innerHTML = "";

    const t = state.logicData.triggers[state.selectedTriggerIndex];
    if (!t) return;

    editor.innerHTML = `
        <label>Тип триггера</label>
        <select id="tr_type">
            <option value="click">Клик</option>
            <option value="near+key">Рядом + кнопка</option>
        </select>

        <label>Имя спрайта</label>
        <input id="tr_target" value="${t.target}" />

        <label>Кнопка</label>
        <input id="tr_key" value="${t.key}" />

        <label>Дистанция</label>
        <input id="tr_range" type="number" value="${t.range}" />

        <hr>

        <label>Действие</label>
        <select id="tr_action_type">
            <option value="dialog">Диалог</option>
            <option value="music">Музыка</option>
        </select>

        <div id="actionParams"></div>
    `;

    // выставляем значения select
    document.getElementById("tr_type").value = t.type;
    document.getElementById("tr_action_type").value = t.action.type;

    bindTriggerEvents();
    renderActionParams(t);
}

// -------------------------------
// События редактора
// -------------------------------
function bindTriggerEvents() {
    const t = state.logicData.triggers[state.selectedTriggerIndex];

    document.getElementById("tr_type").onchange = e => {
        t.type = e.target.value;
        renderTriggers();
    };

    document.getElementById("tr_target").oninput = e => {
        t.target = e.target.value;
    };

    document.getElementById("tr_key").oninput = e => {
        t.key = e.target.value;
    };

    document.getElementById("tr_range").oninput = e => {
        t.range = parseInt(e.target.value) || 0;
    };

    document.getElementById("tr_action_type").onchange = e => {
        t.action.type = e.target.value;
        renderActionParams(t);
    };
}

// -------------------------------
// Параметры действия
// -------------------------------
export function renderActionParams(t) {
    const div = document.getElementById("actionParams");

    if (t.action.type === "dialog") {
        div.innerHTML = `
            <label>ID ноды</label>
            <input id="tr_nodeId" value="${t.action.nodeId || ''}" />
        `;

        document.getElementById("tr_nodeId").oninput = e => {
            t.action.nodeId = e.target.value;
        };
    }

    if (t.action.type === "music") {
        div.innerHTML = `
            <label>Файл</label>
            <input id="tr_music" value="${t.action.src || ''}" />
        `;

        document.getElementById("tr_music").oninput = e => {
            t.action.src = e.target.value;
        };
    }
}