signout = function() {
	$.ajax({
		url: "/api/v0/signout",
		type: "post",
	}).done(function(data){
		if (data && data.status===200) {
			window.location.replace("/");
		} else {
			console.log('signout error with status ' + data.status);
		}
	});
}