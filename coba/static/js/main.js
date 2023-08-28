function StartCamera(){
    var video = document.querySelector("#videoElement");
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (err0r) {
            console.log("Something went wrong!");
        });
    }
 }
const grabScreen = (server_url,pk) =>{
    let player = document.querySelector("#videoElement");
    let canvas = document.getElementById('canvas');
    let ctx = canvas.getContext('2d');
    canvas.width = player.videoWidth;
    canvas.height = player.videoHeight;
    //grab a frame from the video
    ctx.drawImage(player, 0, 0);
    //ONLY WORKS IF image is not tainted by CORS
    let imgdata = ctx.getImageData(0,0, canvas.width, canvas.height);
    let blob = canvas.toBlob((blob) => {
        //this code runs AFTER the Blob is extracted
        let fd = new FormData();
        fd.append('snap', blob);
        fd.append('checkin_pk' , pk);  
        console.log(fd);
        let req = new Request(server_url, {
            method: 'POST',
            credentials: 'same-origin',
            body: fd, /*{Object.assign({},fd,{"checkin_pk" : pk}),}*/
            headers : {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            }
        })
        fetch(req)
        .then(response=>response.json())
        .then(data=>{
            console.log(data)
            console.log('response from server after uploading the image');
        })
        .catch(err=>{
            console.log(err.message);
        });
        
        //load the blob into the image tag
        let img = document.createElement('img');
        let url = URL.createObjectURL(blob);
        img.addEventListener('load', (ev)=>{
            //player.pause();  //stop the video playing if desired
            //let vid = document.createElement('video');
            //vid.poster = url;
            //document.body.appendChild(vid);
            
            //clear memory used to create object url
            //this will make it impossible to download the image with a right click
            window.URL.revokeObjectURL(url);
        })
        img.src = url; //use the canvas binary png blob
    }, 'image/png'); //create binary png from canvas contents
    
}
// document.addEventListener('DOMContentLoaded', ()=>{
//     let player = document.querySelector("#videoElement");
//     player.addEventListener('canplay', (ev)=>{
//         console.log('canplay', ev.target.videoWidth, ev.target.videoHeight);
//         console.log(ev.target.clientWidth, ev.target.clientHeight);
//         console.log(ev.target.currentSrc, ev.target.duration, ev.target.currentTime);
//         player.addEventListener('click', (ev)=>{
//             //click the video to grab a screenshot and display in the canvas
//             grabScreen();
//         })
//     });
    
//     player.addEventListener('canplaythrough', (ev)=>{
//         //this is our own autoplay
//         console.log('Enough loaded to play through whole video');
//         player.play();
//     });
    
//     player.addEventListener('load', (ev)=>{
//         //video has loaded entirely
//         console.log('video loaded');
//     });
    
//     player.addEventListener('error', (err)=>{
//         console.log('Failed to load video', err.message);
//     })
// })