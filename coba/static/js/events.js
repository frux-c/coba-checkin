let names = [
  "John",
  "Jane",
  "Michael",
  "Emily",
  "David",
  "Sarah",
  "Robert",
  "Jessica",
  "William",
  "Olivia",
  "James",
  "Sophia",
  "Benjamin",
  "Emma",
  "Daniel",
  "Ava",
  "Joseph",
  "Mia",
  "Christopher",
  "Isabella",
  "Matthew",
  "Charlotte",
  "Andrew",
  "Amelia",
  "Ethan",
  "Harper",
  "Alexander",
  "Evelyn",
  "Nicholas",
  "Abigail",
  "Samuel",
  "Grace",
  "Christopher",
  "Lily",
  "Joshua",
  "Chloe",
  "Anthony",
  "Zoe",
  "Thomas",
  "Madison",
  "Daniel",
  "Scarlett",
  "William",
  "Lily",
  "Matthew",
  "Aria",
  "Jackson",
  "Layla",
  "Logan",
  "Sofia"
];


let sortedNames = names.sort()

const sname_input = document.getElementById("username"); 
const sid_input = document.getElementById("password");
const suggestionList = document.getElementById("suggestion-dropdown");
const submit_button = document.getElementById("submit");

function submitForm(){
	console.log(sname_input.value, sid_input.value);
	sname_input.value = "";
	sid_input.value = "";
}

submit_button.addEventListener("click", function(){
	if(sname_input.value == "" || sid_input.value == "") return
	submit_button.disabled = true;
	submitForm();
	console.log("button is clicked and disabled");
	setTimeout(function(){
		console.log("button is ready to be clicked again");
		submit_button.disabled = false;
	}, 2000);
})

sname_input.addEventListener("keyup", (e) => {
	suggestionList.innerHTML = "";
	for(let i of sortedNames){
		if(sname_input.value != "" && i.toLowerCase().startsWith(sname_input.value.toLowerCase())){
			let listItem = document.createElement("div");
			listItem.setAttribute("onclick", "displayNames('" + i + "')");
			listItem.classList.add("suggestion-item");
			let context = document.createElement("label");
			listItem.appendChild(context);
			// display matched part in bold
			let word = "<b>" + i.substr(0, sname_input.value.length) + "</b>";
			word += i.substr(sname_input.value.length);
			context.innerHTML = word;
			suggestionList.appendChild(listItem);
		}
	}
})

function checkAndToggleSuggestionDropDown(){
	suggestionList.style.display = suggestionList.hasChildNodes()?"block":"none";
}

function displayNames(value){
	sname_input.value = value;
	suggestionList.innerHTML = "";
}

setInterval(checkAndToggleSuggestionDropDown, 100);