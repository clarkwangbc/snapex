login = function(){
	$.ajax("/api/v0/signin", {
		test: "test",
		secret: $("#input_secret").value,
	}).done(function(data){
		console.log(data.status);
		console.log(data.secret);
	});
}