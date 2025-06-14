document.addEventListener("DOMContentLoaded", function () {
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const loginBtn = document.getElementById("loginBtn");
  const form = document.getElementById("loginForm");

  function validateInputs() {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    // التحقق من الإيميل باستخدام regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isEmailValid = emailRegex.test(email);

    // التحقق من كلمة السر
    const isPasswordValid = password.length >= 6;

    // تفعيل أو تعطيل الزر
    loginBtn.disabled = !(isEmailValid && isPasswordValid);
  }

  emailInput.addEventListener("input", validateInputs);
  passwordInput.addEventListener("input", validateInputs);

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    console.log("Email:", email);
    console.log("Password:", password);

    // الانتظار 2 ثانية قبل التحويل
    setTimeout(() => {
      window.location.href = "BMW_Home.html";
    }, 2000); // 2000ms = 2 seconds

  });
    
});
