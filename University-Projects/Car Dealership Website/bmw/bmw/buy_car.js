document.addEventListener("DOMContentLoaded", function () {
    const nameInput = document.querySelector('input[type="text"]');
    const emailInput = document.querySelector('input[type="email"]');
    const phoneInput = document.querySelector('input[type="tel"]');
    const addressInput = document.getElementById("address");
    const carModelSelect = document.getElementById("car_model");
    const colorSelect = document.getElementById("color");
    const paymentSelect = document.getElementById("paymentMethod");
    const notesInput = document.querySelector('textarea[placeholder^="Write"]');
    const form = document.querySelector("form");

    const modelColors = {
        "BMW 3 Series": ["Black", "White", "Blue"],
        "BMW 5 Series": ["Silver", "Grey", "Dark Blue"],
        "BMW X3": ["White", "Brown", "Green"],
        "BMW X5": ["Black", "Silver", "Navy"],
        "BMW 7 Series": ["Champagne", "Dark Grey", "White"]
    };

    carModelSelect.addEventListener("change", () => {
        const selectedModel = carModelSelect.value;
        console.log("Selected Car Model:", selectedModel);

        // تحديث الألوان حسب الموديل
        colorSelect.innerHTML = '<option value="">-- Choose a Color --</option>';
        if (modelColors[selectedModel]) {
            modelColors[selectedModel].forEach(color => {
                const option = document.createElement("option");
                option.value = color;
                option.textContent = color;
                colorSelect.appendChild(option);
            });
        }
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault(); 

        console.log("=== FORM SUBMITTED ===");
        console.log("Full Name:", nameInput.value);
        console.log("Email:", emailInput.value);
        console.log("Phone Number:", phoneInput.value);
        console.log("Address:", addressInput.value);
        console.log("Car Model:", carModelSelect.value);
        console.log("Preferred Color:", colorSelect.value);
        console.log("Payment Method:", paymentSelect.value);
        console.log("Notes:", notesInput.value);

        alert("Thank you! Your request has been submitted.");
    });
});
