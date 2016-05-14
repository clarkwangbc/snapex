var input_secret,
	input_device_id,
	input_remember;

signin = function(){
	input_secret = $("#input_secret")[0].value;
	input_device_id = $("#input_account")[0].value;
	input_remember = $("#input_remember")[0].checked;
	if (input_secret) {
		$.ajax({
			url: "/api/v0/signin",
			type: "post",
			data: {
				secret: input_secret,
				device_id: input_device_id,
				remember: input_remember
			},
		}).done(function(data){
			if (data && data.status===200) {
				window.location.replace("/myview/project");
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