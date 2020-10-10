"use strict";

import { RCBOARD_CHECK_AND_HIDE_CHECK_INTERVAL, RCBOARD_CHECK_AND_HIDE_DISPLAY_DURATION, RCBOARD_LAPTIME_DELTA_CHANGE_INTERVAL, RCBOARD_LAPTIME_DELTA_CHANGE } from "./modules/const.js";

let re_absolutetime = /^(\d{2}):(\d{2}).(\d{3})$/;

let update_run_metadata = function (metadata) {
    document.getElementById("run-time-remaining").textContent = metadata["REMAININGTIME"];
};

let get_distance_to_first = function (data, pilot) {
    // pilot is first place, no delta
    if (pilot["INDEX"] === 1) return "";

    //window.rc_latest = data;
    let first = data.find(p => p["INDEX"] === 1);

    let first_abstime = re_absolutetime.exec(first["ABSOLUTTIME"]);
    let pilot_abstime = re_absolutetime.exec(pilot["ABSOLUTTIME"]);
    if (first_abstime === null || pilot_abstime === null)
        // no match?
        return "?";

    first_abstime = parseInt(first_abstime[1], 10) * 60 + parseInt(first_abstime[2], 10) + parseInt(first_abstime[3], 10) / 1000;
    pilot_abstime = parseInt(pilot_abstime[1], 10) * 60 + parseInt(pilot_abstime[2], 10) + parseInt(pilot_abstime[3], 10) / 1000;

    let laps_delta = parseInt(first["LAPS"]) - parseInt(pilot["LAPS"]);
    let time_delta = pilot_abstime - first_abstime;

    if (laps_delta > 0) return "+" + laps_delta + "R";

    if (laps_delta < 0) return laps_delta + "R";

    if (time_delta > 0) return "+" + time_delta.toFixed(2);

    return time_delta.toFixed(2);
};

let update_run_scores = function (data) {
    let old_pilots = [].slice.call(document.querySelectorAll("tbody > tr"));

    let new_pilots = {};

    let flash_pilots = {};

    for (let pilot of data) {
        let op_id = old_pilots.findIndex(p => parseInt(p.dataset["vehicle"]) === pilot["VEHICLE"]);
        let p;
        if (op_id !== -1) {
            p = old_pilots[op_id];
            old_pilots.splice(op_id, 1);
        } else {
            p = document.createElement("tr");
            for (let i = 0; i < 4; i++) p.appendChild(document.createElement("td"));

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
        if (parseInt(p.children[2].textContent) !== pilot["LAPS"]) {
            p.children[2].textContent = pilot["LAPS"];
            flash_pilots[pilot["VEHICLE"]] = p;
        }

        if (RCBOARD_LAPTIME_DELTA_CHANGE && Math.floor(Date.now() - window.rcdata.display_delta_time) > RCBOARD_LAPTIME_DELTA_CHANGE_INTERVAL) {
            window.rcdata.display_delta_time = Date.now();
            window.rcdata.display_delta = !window.rcdata.display_delta;
        }

        if (!RCBOARD_LAPTIME_DELTA_CHANGE || window.rcdata.display_delta) {
            let pilot_distance;
            try {
                pilot_distance = get_distance_to_first(data, pilot);
                //console.log("[" + pilot["INDEX"] + "] R" + pilot["LAPS"] + " " + pilot["PILOT"] + " => " + pilot_distance + " @ " + pilot["ABSOLUTTIME"]);
            } catch (e) {
                console.error(e);
                pilot_distance = "E";
            }
            if (p.children[3].textContent !== pilot_distance) {
                p.children[3].textContent = pilot_distance;
            }
        } else {
            if (p.children[3].textContent !== pilot["LAPTIME"]) {
                p.children[3].textContent = pilot["LAPTIME"];
            }
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

    Object.keys(flash_pilots).forEach(k => {
        let fp = flash_pilots[k];
        fp.classList.add("highlight");
        setTimeout(
            p => {
                p.classList.remove("highlight");
            },
            50,
            fp
        );
    });
};

let check_and_hide_action = function () {
    let time_passed = Math.floor(Date.now() - window.rcdata.check_hide_time);
    if (time_passed > RCBOARD_CHECK_AND_HIDE_CHECK_INTERVAL) {
        console.log("check_and_hide_action " + RCBOARD_CHECK_AND_HIDE_CHECK_INTERVAL / 1000 + "s passed, clearing interval " + window.rcdata.check_hide_interval);
        clearInterval(window.rcdata.check_hide_interval);
        delete window.rcdata.check_hide_interval;

        document.querySelector("table").classList.add("hidden");
        console.log("check_and_hide_action table hidden");

        setTimeout(() => {
            console.log("check_and_hide_action " + RCBOARD_CHECK_AND_HIDE_DISPLAY_DURATION / 1000 + "s passed, unhiding");
            document.querySelector("table").classList.remove("hidden");
            delete window.rcdata.check_hide_time;
        }, RCBOARD_CHECK_AND_HIDE_DISPLAY_DURATION);
    }
};

let check_and_hide = function (metadata) {
    if (metadata["RACETIME"] === metadata["CURRENTTIME"] && window.rcdata.check_hide_cached_remaining === metadata["REMAININGTIME"]) {
        if (typeof window.rcdata.check_hide_time === "undefined") {
            window.rcdata.check_hide_time = Date.now();
            window.rcdata.check_hide_interval = setInterval(check_and_hide_action, 100);
            console.log("check_and_hide condition true, started interval " + window.rcdata.check_hide_interval);
        }
    } else if (typeof window.rcdata.check_hide_time !== "undefined" && typeof window.rcdata.check_hide_interval !== "undefined") {
        console.log("check_and_hide condition false, clearing interval " + window.rcdata.check_hide_interval);
        clearInterval(window.rcdata.check_hide_interval);
        delete window.rcdata.check_hide_interval;
        delete window.rcdata.check_hide_time;
    } else {
        window.rcdata.check_hide_cached_remaining = metadata["REMAININGTIME"];
        if (typeof window.rcdata.check_hide_time !== "undefined") {
            delete window.rcdata.check_hide_time;
        }
    }
};

let init = function () {
    if (typeof window.rcdata === "undefined") window.rcdata = {};

    window.rcdata.display_delta = false;
    window.rcdata.display_delta_time = Date.now();

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
            update_run_scores(event["DATA"]);
        } catch (e) {
            console.error(e);
        }
        try {
            check_and_hide(event["METADATA"]);
        } catch (e) {
            console.error(e);
        }
    });
};

document.addEventListener("DOMContentLoaded", init);
