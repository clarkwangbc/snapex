var input_secret;

signin = function(){
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
			if (data && data.status===200) {
				window.location.replace("http://snapex.duapp.com/mypage");
			} else {
				$("#wrong_secret_msg")[0].style.display = "";
				$("#empty_secret_msg")[0].style.display = "none";
			}
		});
	} else {
		$("#empty_secret_msg")[0].style.display = "";
		$("#wrong_secret_msg")[0].style.display = "none"
	}
}