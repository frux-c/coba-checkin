// connect to websocket
const websocket_url = window.location.protocol=="https"?"wss://":"ws://" + window.location.host;
var socket = new WebSocket(websocket_url);

// useful elements
const event_log_list = document.getElementById("logs-list");
const students_list = document.getElementById("students-list");
// display message when connected
socket.onopen = () => {
    console.log("Connected to websocket");
    socket.send("Hello from client");
};

socket.onmessage = (message) => {
    payload = JSON.parse(message.data);
    if(payload.event === "websocket.checkin" || payload.event === "websocket.checkout"){
        // update logs for current session
        event_log = document.createElement("li");
        event_log.innerHTML = "<span>" + (new Date()).toLocaleString() + "</span><span>" + payload.message + "</span>";
        event_log_list.insertBefore(event_log, event_log_list.firstChild);
    }
    if(payload.event === "websocket.update_students"){
        students_list.innerHTML = ""; // clear list
        var wave = document.createElement("span");
        wave.classList.add("wave");
        wave.innerHTML = "&#128075;";
        for(let student_obj of payload.message){
            var student = document.createElement("li");
            student.appendChild(wave);
            student.innerHTML += student_obj.first_name + " " + student_obj.last_name;
            students_list.appendChild(student);
        }
    }
}