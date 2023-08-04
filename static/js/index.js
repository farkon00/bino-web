const code_area  = document.getElementById("code-area");
const out_frame  = document.getElementById("result-frame-text");
const run_button = document.getElementById("run-button");
const send_timer_time = 7000;

let prev_text = code_area.value;
let send_timer = setTimeout(sendCode, send_timer_time); 

code_area.addEventListener("input", onInput);
run_button.addEventListener("click", sendCode)

function onInput(event) {
    if (event.inputType == "insertLineBreak") sendCode();
}

function sendCode() {
    if (prev_text != code_area.value)
        fetch("/execute", {
            method: "POST",
            body: code_area.value
        })
        .then(resp => resp.text())
        .then(function(text) {
            out_frame.innerText = text;
        });
    prev_text = code_area.value;
    clearTimeout(send_timer);
    send_timer = setTimeout(sendCode, send_timer_time);
}