signin = function(){
	input_secret = document.getElementById("input_secret").value;
	if (input_secret) {
		$.ajax("/api/v0/signin", {
			test: "test",
			secret: input_secret,
		}).done(function(data){
			console.log(data.status);
			console.log(data.secret);
		});
	}
	return 0;
}