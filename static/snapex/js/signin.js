var input_secret;

signin = function(){
	console.log("in sign in");
	input_secret = $("#input_secret")[0].value;
	if (input_secret) {
		$.ajax({
			url: "/api/v0/signin",
			type: "post",
			data: {
				test: "test",
				secret: input_secret,
			},
		}).done(function(data){
			console.log(data.status);
			console.log(data.msg);
		});
	} else {
		$("#empty_secret_msg")[0].style.display = "";
	}
}