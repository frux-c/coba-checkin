const root = document.documentElement;
const eye = document.getElementById('eyeball');
const beam = document.getElementById('beam');
const passwordInput = document.getElementById('password');

root.addEventListener('mousemove', (e) => {
  let rect = beam.getBoundingClientRect();
  let mouseX = rect.right + (rect.width / 2); 
  let mouseY = rect.top + (rect.height / 2);
  let rad = Math.atan2(mouseX - e.pageX, mouseY - e.pageY);
  let degrees = (rad * (20 / Math.PI) * -1) - 350;

  root.style.setProperty('--beamDegrees', `${degrees}deg`);
});

eye.addEventListener('click', e => {
  e.preventDefault();
  document.body.classList.toggle('show-password');
  passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password'
  passwordInput.focus();
});

async function asyncLoop() {
  var success_anim = document.getElementById("success-div");
  var failure_anim = document.getElementById("failure-div");
  while (true) {
    // Wait for 3 seconds
    await new Promise(resolve => setTimeout(resolve, 3000));
    if(success_anim.style.display === "none"){
      failure_anim.style.display = "none";
      success_anim.style.display = "block";
    }
    else{
      failure_anim.style.display = "block";
      success_anim.style.display = "none";
    }
  }
}

// Start the asynchronous loop
asyncLoop();
