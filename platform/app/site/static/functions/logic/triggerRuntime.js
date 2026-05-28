import { state } from "../core/state.js";
import { runAction } from "../scene/sceneEditor.js";

export function runTriggers(event) {
    state.logicData.triggers.forEach(trigger => {

        if (trigger.type === "click") {
            if (event.type === "npcClick" && event.id === trigger.target) {
                runAction(trigger.action);
            }
        }

        if (trigger.type === "near+key") {
            if (
                event.type === "near" &&
                event.id === trigger.target &&
                event.key === trigger.key
            ) {
                runAction(trigger.action);
            }
        }

    });
}