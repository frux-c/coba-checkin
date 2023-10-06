// connect to websocket
const websocket_url = (window.location.protocol==="https:"?"wss://":"ws://") + window.location.host + "/ws/";

var socket = new WebSocket(websocket_url);

// useful elements
const event_log_list = document.getElementById("logs-list");
const employees_list = document.getElementById("employees-list");

// display message when connected
socket.onopen = () => {
    console.log("Connected to websocket");
    socket.send({
        "type": "websocket.connect",
        "message": "Connected to websocket"
    });
};

socket.onmessage = (message) => {
    payload = JSON.parse(message.data);
    if(payload.event === "websocket.checkin" || payload.event === "websocket.checkout"){
        // update logs for current session
        event_log = document.createElement("li");
        event_log.innerHTML = "<span class=\"timestamp\">" + (new Date()).toLocaleTimeString() + "</span><span>" + payload.message + "</span>";
        // check if there are already 7 logs
        if(event_log_list.childNodes.length >= 7){
            event_log_list.removeChild(event_log_list.lastChild);
        }
        event_log_list.insertBefore(event_log, event_log_list.firstChild);
    }
    if(payload.event === "websocket.update_employees"){
        employees_list.innerHTML = ""; // clear list
        var wave = document.createElement("span");
        wave.classList.add("wave");
        wave.innerHTML = "&#128075;";
        for(let employee of payload.message){
            var li_elem = document.createElement("li");
            li_elem.appendChild(wave);
            li_elem.innerHTML += employee.first_name + " " + employee.last_name;
            employees_list.appendChild(li_elem);
        }
    }
}