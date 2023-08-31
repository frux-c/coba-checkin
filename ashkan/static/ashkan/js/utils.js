function delayedRedirectHome(delaySecs) {
	setTimeout(() => {
		location.assign("/ashkan");
	}, delaySecs*1000);
}

function getTime() {
	date = new Date();
  return `${date.getHours()}:${date.getMinutes()}`;
}
