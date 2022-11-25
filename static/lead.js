"use strict";

import { RCBOARD_LEAD_DISPLAY_DURATION } from "./modules/const.js";

let show_update = function () {
    if (window.rcdata.hidden) {
        document.querySelector("div.wrapper > div").classList.remove("hidden");
        window.rcdata.hidden = false;
    } else {
        clearTimeout(window.rcdata.timeout_hide);
    }

    window.rcdata.timeout_hide = setTimeout(() => {
        document.querySelector("div.wrapper > div").classList.add("hidden");
        window.rcdata.hidden = true;
    }, RCBOARD_LEAD_DISPLAY_DURATION);
};

let update_lead = function (data) {
    if (window.rcdata.race_finished) return;

    let valid_vehicles = data.filter(v => v["BESTTIME"] !== "0.000");

    if (valid_vehicles.length === 0) {
        if (window.rcdata.best_vehicle_id !== null) {
            window.rcdata.best_vehicle_id = null;
            window.rcdata.best_vehicle_time = null;
        }

        return;
    }

    let [lead] = valid_vehicles.sort((a, b) => (parseFloat(a["BESTTIME"]) < parseFloat(b["BESTTIME"]) ? -1 : 1));

    if (window.rcdata.best_vehicle_id !== lead["VEHICLE"]) {
        window.rcdata.best_vehicle_id = lead["VEHICLE"];
        window.rcdata.best_vehicle_time = lead["BESTTIME"];
        document.querySelector("#driver").textContent = lead["PILOT"];
        document.querySelector("#laptime").textContent = lead["BESTTIME"];
        show_update();
    } else if (window.rcdata.best_vehicle_time !== lead["BESTTIME"]) {
        window.rcdata.best_vehicle_time = lead["BESTTIME"];
        document.querySelector("#laptime").textContent = lead["BESTTIME"];
        show_update();
    }
};

let update_run_metadata = function (metadata) {
    // The "RACESTATE" is indicating you the state of the race. Following you will find the different states
    // Idle : 0
    // Started : 1
    // Prepared : 2
    // Interrupted : 3
    // RaceOver : 4
    // Finalized : 5
    let racestate = metadata["RACESTATE"];
    if (typeof racestate === "string") racestate = parseInt(racestate, 10);

    if (racestate === 4 || racestate === 5) {
        if (!window.rcdata.hidden) {
            window.rcdata.hidden = true;
            window.rcdata.race_finished = true;

            document.querySelector("div.wrapper > div").classList.add("hidden");
            if (window.rcdata.timeout_hide !== null) {
                clearTimeout(window.rcdata.timeout_hide);
            }
        }
    } else {
        if (window.rcdata.race_finished) {
            window.rcdata.race_finished = false;
            window.rcdata.best_vehicle_id = null;
            window.rcdata.best_vehicle_time = null;
        }
    }
};

let init = function () {
    if (typeof window.rcdata === "undefined") window.rcdata = {};

    window.rcdata.hidden = true;
    window.rcdata.race_finished = false;
    window.rcdata.best_vehicle_id = null;
    window.rcdata.best_vehicle_time = null;

    window.rcdata.timeout_hide = null;

    let es = new EventSource("/sse");
    es.addEventListener("error", () => {
        setTimeout(init, 200);
    });

    es.addEventListener("StreamingData", function (data) {
        let event = JSON.parse(data.data)["EVENT"];

        try {
            update_run_metadata(event["METADATA"]);
        } catch (e) {
            console.error(e);
        }

        try {
            update_lead(event["DATA"]);
        } catch (e) {
            console.error(e);
        }
    });
};

document.addEventListener("DOMContentLoaded", init);
