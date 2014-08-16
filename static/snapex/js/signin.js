var input_secret;

signin = function(){
	input_secret = $("#input_secret")[0].value;
	if (input_secret) {
		$.ajax("/api/v0/signin", {
			test: "test",
			secret: input_secret,
		}).done(function(data){
			console.log(data.status);
			console.log(data.secret);
		});
	} else {
		$("#empty_secret_msg")[0].style.display = "";
	}
	return 0;
}