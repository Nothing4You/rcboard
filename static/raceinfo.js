"use strict";

let update_run_metadata = function(metadata) {
    document.getElementById("roundinfotext").textContent = metadata["NAME"];
    document.getElementById("raceinfotext").textContent = metadata["GROUP"];
};

let init = function() {
    let es = new EventSource("/sse");
    es.addEventListener("error", () => {setTimeout(init, 200);});

    es.addEventListener("StreamingData", function(data) {
        let event = JSON.parse(data.data)["EVENT"];

        try {
            update_run_metadata(event["METADATA"]);
        } catch(e) {
            console.error(e);
        }
    });
}

document.addEventListener("DOMContentLoaded", init);
