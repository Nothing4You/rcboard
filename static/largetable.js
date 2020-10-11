"use strict";

import { RCBOARD_CHECK_AND_HIDE_DISPLAY_DURATION } from "./modules/const.js";

let update_run_metadata = function (metadata) {
    document.getElementById("run-event-name").textContent = metadata["NAME"];
    document.getElementById("run-group-name").textContent = metadata["GROUP"];
};

let update_run_scores = function (data) {
    let old_pilots = [].slice.call(document.querySelectorAll("tbody > tr"));

    let new_pilots = {};

    for (let pilot of data) {
        let op_id = old_pilots.findIndex(p => parseInt(p.dataset["vehicle"]) === pilot["VEHICLE"]);
        let p;
        if (op_id !== -1) {
            p = old_pilots[op_id];
            old_pilots.splice(op_id, 1);
        } else {
            p = document.createElement("tr");
            for (let i = 0; i < 6; i++) p.appendChild(document.createElement("td"));

            p.children[2].appendChild(document.createElement("img"));

            p.dataset["vehicle"] = pilot["VEHICLE"];
        }

        new_pilots[pilot["INDEX"]] = p;

        if (parseInt(p.dataset["index"]) !== pilot["INDEX"]) {
            p.dataset["index"] = pilot["INDEX"];
            p.children[0].textContent = pilot["INDEX"];
        }
        if (p.children[1].textContent !== pilot["PILOT"]) {
            p.children[1].textContent = pilot["PILOT"];
        }
        if (p.children[2].children[0].alt !== pilot["COUNTRY"]) {
            let img = document.createElement("img");
            img.src = "flags-iso/flat/32/" + pilot["COUNTRY"] + ".png";
            img.alt = pilot["COUNTRY"];

            p.children[2].replaceChild(img, p.children[2].children[0]);
        }
        if (parseInt(p.children[3].textContent) !== pilot["LAPS"]) {
            p.children[3].textContent = pilot["LAPS"];
        }
        if (p.children[4].textContent !== pilot["BESTTIME"]) {
            p.children[4].textContent = pilot["BESTTIME"];
        }
        if (p.children[5].textContent !== pilot["ABSOLUTTIME"]) {
            p.children[5].textContent = pilot["ABSOLUTTIME"];
        }
    }

    for (let op of old_pilots) {
        op.remove();
    }

    let parent = document.querySelector("tbody");
    Object.keys(new_pilots).forEach(k => {
        let np = new_pilots[k];
        if (parent.children.length >= np.dataset["index"] && parent.children[np.dataset["index"]] !== np) {
            parent.insertBefore(np, parent.children[np.dataset["index"]]);
        } else if (parent.children.length < np.dataset["index"]) {
            parent.appendChild(np);
        }
    });
};

let check_and_hide = function (metadata) {
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
        if (!window.rcdata.check_hide_triggered) {
            window.rcdata.check_hide_triggered = true;

            document.querySelector("table").classList.remove("hidden");
            console.log("check_and_hide table unhidden");

            setTimeout(() => {
                console.log("check_and_hide " + RCBOARD_CHECK_AND_HIDE_DISPLAY_DURATION / 1000 + "s passed, hiding");
                document.querySelector("table").classList.add("hidden");
                delete window.rcdata.check_hide_time;
            }, RCBOARD_CHECK_AND_HIDE_DISPLAY_DURATION);
        }
    } else if (window.rcdata.check_hide_triggered) {
        window.rcdata.check_hide_triggered = false;
    }
};

let init = function () {
    if (typeof window.rcdata === "undefined") window.rcdata = {};

    window.rcdata.check_hide_triggered = false;

    let es = new EventSource("/sse");
    es.addEventListener("error", () => {
        setTimeout(init, 200);
    });

    es.addEventListener("StreamingData", function (data) {
        let event = JSON.parse(data.data)["EVENT"];

        try {
            check_and_hide(event["METADATA"]);
        } catch (e) {
            console.error(e);
        }
        if (!document.querySelector("table").classList.contains("hidden")) {
            return;
        }

        try {
            update_run_metadata(event["METADATA"]);
        } catch (e) {
            console.error(e);
        }
        try {
            update_run_scores(event["DATA"]);
        } catch (e) {
            console.error(e);
        }
    });
};

document.addEventListener("DOMContentLoaded", init);
