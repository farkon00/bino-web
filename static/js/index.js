const code_area = document.getElementById('code-area');
const send_timer_time = 5000;

const socket = io();

let prev_text = code_area.value;
let send_timer = setTimeout(sendCode, send_timer_time); 

code_area.addEventListener("input", onInput);

function onInput(event) {
    if (event.inputType == "insertLineBreak") sendCode();
}

function sendCode() {
    if (prev_text != code_area.value)
        socket.emit("change", code_area.value);
    prev_text = code_area.value;
    clearTimeout(send_timer);
    send_timer = setTimeout(sendCode, send_timer_time);
}