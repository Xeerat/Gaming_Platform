import { state } from "../core/state.js";

export async function saveTrigger() {
    const i = state.selectedTriggerIndex;
    if (i === null) {
        alert("Выбери триггер");
        return;
    }

    const trigger = state.logicData.triggers[i];

    if (!trigger.target) {
        alert("Укажи target");
        return;
    }

    const payload = {
        sprite_name: trigger.target,
        trigger_config: trigger
    };

    const res = await fetch("/sprites/update_sprite_logic/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    if (!res.ok) {
        alert("Ошибка");
        return;
    }

    alert("Сохранено");
}