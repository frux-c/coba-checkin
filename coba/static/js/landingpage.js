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
    // player.width = Math.floor(player.videoWidth / 2);
    // player.height = Math.floor(player.videoHeight / 2);
    let ctx = canvas.getContext('2d');
    console.log(player.videoWidth,player.videoHeight);
    canvas.width = 500;
    canvas.height = 380;
    //grab a frame from the video
    ctx.scale(0.8, 0.8);
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

function signIn(home_url){
  console.log("signingIn");

  var seconds = 2;
  //countdown status
  var dvCountDown = document.getElementById("CountDown");
  var lblCount = document.getElementById("CountDownLabel");
  //checkmark animation
  var loader = document.getElementById("loader_circle");
  var check_mark = document.getElementById("loader_checkmark");
  setTimeout(function() {
          console.log("running now");
          $('.circle-loader').toggleClass('load-complete');
          $('.checkmark').toggle();
          console.log("finished running!");
  },1000);
  setInterval(function(){
    lblCount.innerHTML = "Redirecting home in " + seconds + "s";
    if(seconds == 0){
      lblCount.innerHTML = ":)";
      window.location = home_url;
    }
    seconds--;
  },1000);
}

function signOut(signout_url,pk,home_url){
  console.log("signingOut");
  //checkmark animation
  var loader = document.getElementById("loader_circle");
  var check_mark = document.getElementById("loader_checkmark");
  loader.style.display = "none";
  StartCamera();
  var seconds = 6;
  var dvCountDown = document.getElementById("CountDown");
  var lblCount = document.getElementById("CountDownLabel");
  let canvas = document.getElementById("canvas");
  let player = document.querySelector("#videoElement");
  // dvCountDown.style.display = "block";
  setInterval(function () {
    console.log(seconds + "seconds");
    if(seconds > 3){
      lblCount.innerHTML = "Snapshot in " + (seconds - 3) + "s";
    }
    else if(seconds == 3 ){
      grabScreen(signout_url,pk);
      canvas.classList.add('animate__animated','animate__fadeIn');
      canvas.style.setProperty('--animate-duration', '0.5s');
      lblCount.innerHTML = "Recived Snapshot";
      player.style.display = "none";
      canvas.style.display = "block";
      canvas.style.border = "3px solid white";
    }
    else if(seconds == 2 ){
      canvas.classList.remove('animate__fadeIn');
      canvas.classList.add('animate__fadeOut');
      canvas.style.display = "none";
      loader.style.display = "block";
      setTimeout(function() {
          $('.circle-loader').toggleClass('load-complete');
          $('.checkmark').toggle();
      },1000);
      lblCount.innerHTML = "Redirecting home in " + seconds + "s";
    }
    else if(seconds > 0){
        lblCount.innerHTML = "Redirecting home in " + seconds + "s";
    }
    else if(seconds == 0) {
      dvCountDown.style.display = "none";
      window.location = home_url;
    }
    seconds--;

  }, 1000);
}
