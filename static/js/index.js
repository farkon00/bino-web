const code_area = document.getElementById('code-area');
const send_timer_time = 5000;
let send_timer = setTimeout(send_code, send_timer_time); 

code_area.addEventListener("input", on_input);

function on_input(event) {
    if (event.inputType == "insertLineBreak") send_code();
}

function send_code() {
    console.log("hey, where is websocket?\n" + code_area.value);
    send_timer = setTimeout(send_code, send_timer_time);
}