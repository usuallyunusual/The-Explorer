const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
	container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
	container.classList.remove("right-panel-active");
});
function signup_verify(){
	var a = document.querySelector("#num1").value;
	var b = document.querySelector("#num2").value;
	var c = document.querySelector("#num3").value;
	var d = document.querySelector("#num4").value;
	var data = new Object();
	data.username = document.mform.username.value;
	data.email = document.mform.email.value;
	data.password = document.mform.password.value;
	data = JSON.stringify(data);

	var con = String(a)+String(b)+String(c)+String(d);

	if(con===window.otp){
		alert("Successfully verified");
		$.ajax({
			url:"/signup",
			type : "POST",
			datatype:'json',
			data:{'data':data},
			success:function(data){
				console.log("Logged in");
				document.write(data);
			}
		});
		
	}
}