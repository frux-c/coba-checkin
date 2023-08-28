//GLOBALS
const student_header = document.getElementById("student_header");
const student_list = document.getElementById("student_list");
const title = document.getElementById("full_box");

title.classList.add('animate__animated', 'animate__fadeIn');

//WEBSOCKET

var websocket_endpoint = "ws://" + window.location.host + window.location.pathname;
const socket = new WebSocket(websocket_endpoint);

socket.onmessage = function(event){
    payload = JSON.parse(event.data).payload;
    if(payload.event == "websocket.update_students"){
        const students = payload.message.split(",");
        updateStudents(students);
    }
    if(payload.event == "websocket.student_checkin_status"){
        const message = payload.message;
        if(message == "404") return;
        updateCheckInLayout(!!message);
    }
}
socket.onerror = function(error){
    console.log('error recieved');
    console.log(error);
}
socket.onopen = function(){
    socket.send(
        JSON.stringify({
            event : "websocket.connect",
            message : "connected!"}));
    socket.send(
        JSON.stringify({
            event : "websocket.primary_student_update",
            message : null
        }));
}

function updateCheckInLayoutCaller(){
    const student_name = document.getElementById("student").value;
    const timein = document.getElementById("time_in_div");
    const timeout = document.getElementById("time_out_div");
    if(student_name == ""){
        timein.style.display = "none";
        timeout.style.display = "none";
        return;
    }
    socket.send(JSON.stringify({
        event : "websocket.student_checkin_status",
        message : student_name,
    }));
}
function updateCheckInLayout(status){
    const timein = document.getElementById("time_in_div");
    const timeout = document.getElementById("time_out_div");
    timein.style.setProperty('--animate-duration', '0.5s');
    timeout.style.setProperty('--animate-duration', '0.5s');
    if(status){
        // toggle time in field
        timeout.classList.toggle('animate__fadeIn');
        if(timein.classList.contains('animate__fadeIn')){
            timein.classList.toggle('animate__fadeIn');
            timein.classList.toggle('animate__fadeOut');
        }
        timein.style.display = "none";
        timeout.style.display = "block";
    }
    else{
        // toggle timeout field
        timein.classList.toggle('animate__fadeIn');
        if(timeout.classList.contains('animate__fadeIn')){
            timeout.classList.toggle('animate__fadeIn');
            timeout.classList.toggle('animate__fadeOut');
        }
        timeout.style.display = "none";
        timein.style.display = "block";
    }
}

student_header.classList.add('animate__animated','animate__fadeIn');
student_header.style.setProperty('--animate-duration', '0.5s');
student_list.classList.add('animate__animated','animate__fadeIn');
student_list.style.setProperty('--animate-duration', '0.5s');
function updateStudents(students){
    if(students.length < 1){
        student_header.style.display = "none";
        student_list.innerHTML = '';
    }
    else{
        student_header.style.display = "block";
        student_list.innerHTML = '';
        for(var i = 0; i < students.length; i++){
            var student_item = document.createElement("li");
            student_item.innerHTML = students[i];
            student_item.classList.add("text-white-50");
            student_list.appendChild(student_item);
        }
    }
}
// deprecated
// function grabAvailableStudents(){
//     const options = {
//       method: 'POST',
//       credentials: 'same-origin',
//       headers : {
//           "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
//       }
//     };
//     fetch(window.location.href + "webhooks/students/", options )
//             .then( response => response.json() )
//             .then( response => {
//               const students = response['students'];
//     if(students.length < 1){
//                 student_header.style.display = "none";
//             student_list.innerHTML = '';
//     }
//     else{
//         student_header.style.display = "block";
//         student_list.innerHTML = '';
//         for(var i = 0; i < students.length; i++){
//           var student_item = document.createElement("li");
//           student_item.innerHTML = students[i];
//           student_item.classList.add("text-white-50");
//           student_list.appendChild(student_item);
//           }
//         }
//     })
//             .catch(err => console.log(err));;
// }

