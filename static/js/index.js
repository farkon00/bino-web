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
    if (event.inputType == "insertText" && event.value == "\n") sendCode();
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

function insert(text) {
    const selection_start = code_area.selectionStart;
    const selection_end = code_area.selectionEnd;
    const old_text = code_area.value;
  
    const prefix = old_text.substring(0, selection_start);
    const suffix = old_text.substring(selection_end);
    code_area.value = `${prefix}${text}${suffix}`;

    code_area.setSelectionRange(selection_start + 4, selection_start + 4);
  }

document.addEventListener("keydown", function(e) {
    console.log(e.target, e.key);
    if (e.key == "Tab") {
        e.preventDefault();
        insert("    ");
    }
})

const dropdown_options = document.getElementsByClassName("dropdown-option");
for (let i = 0; i < dropdown_options.length; i++) {
    dropdown_options[i].addEventListener("click", function() {
        code_area.value = examples[dropdown_options[i].getAttribute("data-example-id")];
        document.getElementById("dropdown-text").innerText = dropdown_options[i].innerText;
    });
}

const examples = {
    hello_world: 'print "Hello, world!"',
    fibonacci: 
`func list fib : n: int {
    if (== n 0) {
        return []
    }
    if (== n 1) {
        return [1]
    }

    var res = [1 1]
    while (< (len res) n) {
        append res (+ (index res -1) (index res -2))
    }
    return res
}

print (fib 8)
`,
    fizzbuzz:
`var i = 1
while (<= i 100) {
    if (== (% i 15) 0) {
        print "fizzbuzz" 
    }
    elif (== (% i 5) 0) {
        print "buzz"
    }
    elif (== (% i 3) 0) {
        print "fizz"
    }
    else {
        print i
    }
    var i = (+ i 1)
}`,
    rule110:
`// Input
var initial = [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
var iterations = 16

var size = (len initial)
var states = [initial]

var last-state = initial
var i = 0
while (< i (- iterations 1)) {
    var j = 0
    var new-state = []
    while (< j size) {
        var p = (index last-state (- j 1))
        var q = (index last-state j)
        var r = (index last-state (% (+ j 1) size))
        append new-state (or (and q (not p)) (xor q r))
        var j = (+ j 1)
    }
    var last-state = new-state
    append states last-state

    var i = (+ i 1)
}

var buffer = "" 
for i states {
    for j i {
        if j {
            var buffer = (+ buffer "*")
        }
        else {
            var buffer = (+ buffer " ")
        }
    }
    var buffer = (+ buffer "\\n")
}
print buffer`
};