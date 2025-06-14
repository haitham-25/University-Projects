
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".form309");
    const inputs = form.querySelectorAll("input, select, textarea");

    // Log full value on blur only
    inputs.forEach(input => {
        input.addEventListener("blur", () => {
            if (input.type !== "submit") {
                console.log(`${input.name || input.id || 'Field'}: ${input.value.trim()}`);
            }
        });
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        let isValid = true;
        let messages = [];

        const emailInput = form.querySelector('input[type="email"]');
        const email = emailInput.value.trim();

        // Email validation regex
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            isValid = false;
            messages.push("Please enter a valid email address.");
        }

        // Check required fields
        inputs.forEach(input => {
            if (input.hasAttribute("required") && !input.value.trim()) {
                isValid = false;
                messages.push(`Please fill in the ${input.name || input.id} field.`);
            
            }
        
        });
       if (!isValid) {
        alert(messages.join("\n"));
    } else {
        alert("Thank you! Your request has been submitted.");
        form.reset(); // (اختياري) إعادة تعيين النموذج
    } 
    });
});
