const sname_input = document.getElementById("username");
const sid_input = document.getElementById("password");
const suggestionList = document.getElementById("suggestion-dropdown");
const submit_button = document.getElementById("submit");
const success_anim = document.getElementById("success-div");
const failure_anim = document.getElementById("failure-div");

async function playSuccess() {
	success_anim.style.display = "block";
	await new Promise(resolve => setTimeout(resolve, 3000));
	success_anim.style.display = "none";
}

async function playFailure() {
	failure_anim.style.display = "block";
	await new Promise(resolve => setTimeout(resolve, 3000));
	failure_anim.style.display = "none";
}

// Get all employees' names from the database
async function populateStudentNameList() {
	let names = [];
	await fetch(window.location.href + "api/employees/", {
		method: "GET",
		cors: "cors",
		headers: {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"X-CSRFToken": document.getElementsByName("csrfmiddlewaretoken")[0].value,
		},
	})
	.then((response) => response.json())
	.then((response) => {
		for (employee of response["employees"])
			names.push(employee.first_name + " " + employee.last_name);
		// sort the names alphabetically
		names = names.sort();
	})
	.catch((err) => {
		console.log(err)
	});
	return names;
}

// Sort the names alphabetically
let sortedNames = [];
populateStudentNameList().then((names) => sortedNames = names);

// suggest names as user types
sname_input.addEventListener("keyup", (e) => {
	suggestionList.innerHTML = "";
	for (let i of sortedNames) {
		if (
			sname_input.value != "" &&
			i.toLowerCase().startsWith(sname_input.value.toLowerCase())
		) {
			let listItem = document.createElement("div");
			listItem.setAttribute("onclick", "selectName('" + i + "')");
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
});

// hanlde if user presses tab key while in sname_input
document.addEventListener("keydown", (e) => {
	// if user presses tab key while in sname_input
	if (e.key === "Tab" &&  document.activeElement === sname_input) {
		// e.preventDefault();
		if (suggestionList.hasChildNodes())
			var word = suggestionList.firstChild.firstChild.innerText;
			selectName(word);
	}
});

// submit form when user clicks submit button
submit_button.addEventListener("click", function () {
	if (sname_input.value == "" || sid_input.value == "") return;
	submit_button.disabled = true;
	submitForm();
	setTimeout(function () {
		submit_button.disabled = false;
	}, 2000);
});

// select name from suggestion list
function selectName(value) {
	sname_input.value = value;
	suggestionList.innerHTML = "";
}

// change submit button if user is checking in or out
function changeSubmitButton() {
	var temp_employees = employees_list.getElementsByTagName("li");
	for(let i = 0; i < temp_employees.length; i++){
		if(sname_input.value === temp_employees[i].innerText.replace("👋", "")){
			submit_button.innerHTML = "Sign out";
			return;
		}
	}
	submit_button.innerHTML = "Sign in";
}

// hide suggestion list when user clicks outside of it
// check if user is checking in or out
setInterval(() => {
	suggestionList.style.display = suggestionList.hasChildNodes() && document.activeElement === sname_input
		? "block"
		: "none";
	changeSubmitButton()
}, 250);

// submit form to server
function submitForm() {
	fetch(window.location.href + "api/checkins/", {
		method: "POST",
		cors: "cors",
		body: JSON.stringify({
			employee_name: sname_input.value,
			employee_id: sid_input.value,
			type: "form",
		}),
		headers: {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"X-CSRFToken": document.getElementsByName("csrfmiddlewaretoken")[0].value,
		},
	})
	.then((response) => response.json())
	.then((response) => {
		if (response["check_in"] === true) {
			playSuccess();
		} else if (response["check_in"] === false) {
			playSuccess();
		} else {
			playFailure();
		}
	})
	.catch((err) => console.log(err));
	sname_input.value = "";
	sid_input.value = "";
}
