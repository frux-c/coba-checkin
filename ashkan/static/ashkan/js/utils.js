function delayedRedirectHome() {
	setTimeout(() => {
		location.assign("/ashkan");
	}, 3000);
}

function getTime() {
	date = new Date();
  return `${date.getHours()}:${date.getMinutes()}`;
}
