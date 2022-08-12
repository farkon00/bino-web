const code_area = document.getElementById('code-area');
const send_timer_time = 5000;
let send_timer = setTimeout(sendCode, send_timer_time); 

let prev_text = code_area.value;

code_area.addEventListener("input", onInput);

function onInput(event) {
    if (event.inputType == "insertLineBreak") sendCode();
}

function getDifference(a, b) {
    var start_index = 0;
    var end_index = 0;

    if (a == b) return [0, 0, ""];

    while (start_index < a.length - 1 && a[start_index] == b[start_index]) start_index++;
    while (end_index < b.length && a[a.length-end_index] == b[b.length-end_index]) end_index++;

    return [start_index, end_index, b.substring(start_index, b.length-end_index+1)];
}

function sendCode() {
    console.log(getDifference(prev_text, code_area.value));
    prev_text = code_area.value;
    clearTimeout(send_timer);
    send_timer = setTimeout(sendCode, send_timer_time);
}