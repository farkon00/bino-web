const code_area = document.getElementById('code-area');
const out_frame = document.getElementById('result-frame');
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

socket.on("add_out", function (text) {
    console.log("Recieved output:\n" + text);
    out_frame.innerText += text;
})

socket.on("reset_out", function () {
    console.log("Output cleared");
    out_frame.innerText = "";
})