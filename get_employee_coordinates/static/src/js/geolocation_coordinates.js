/** @odoo-module **/

import {registry} from "@web/core/registry";

async function actionGetCoordinates(env, action) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const {latitude, longitude} = position.coords;
                await saveCoordinates(latitude, longitude, env, action.context.active_id);
            },
            () => {
                console.log("Unable to retrieve your location.");
            }
        );
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

async function saveCoordinates(latitude, longitude, env, activeId) {
    try {
        await env.services.orm.call(
            "hr.employee.coordinate",
            "save_coordinates",
            [activeId, latitude, longitude],
        );
        window.location.reload();

    } catch (err) {
        console.log("Error saving coordinates");
    }
}

registry.category("actions").add("get_employee_coordinates", (env, action) =>
    actionGetCoordinates(env, action));
