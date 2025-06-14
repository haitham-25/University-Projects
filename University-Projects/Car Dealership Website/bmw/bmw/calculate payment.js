// Handle calculate button click
document.getElementById('calculate').addEventListener('click', () => {
    // Get input values
    const carPrice = parseFloat(document.getElementById('car-price').value);
    const downPayment = parseFloat(document.getElementById('down-payment').value);
    const loanTerm = parseInt(document.getElementById('loan-term').value);

    // Validate inputs
    if (isNaN(carPrice) || carPrice <= 0) {
        alert('Please enter a valid car price!');
        return;
    }
    if (isNaN(downPayment) || downPayment < 0 || downPayment > carPrice) {
        alert('Please enter a valid down payment (less than or equal to car price)!');
        return;
    }
    if (isNaN(loanTerm) || loanTerm <= 0) {
        alert('Please enter a valid loan term!');
        return;
    }



    // Calculate remaining amount and monthly payment
    const remainingAmount = carPrice - downPayment;
    const monthlyPayment = remainingAmount / loanTerm;

    // Display results
    document.getElementById('results').innerHTML = `
        <p>Down Payment: $${downPayment.toFixed(2)}</p>
        <p>Remaining Amount: $${remainingAmount.toFixed(2)}</p>
        <p>Monthly Payment: $${monthlyPayment.toFixed(2)} for ${loanTerm} months</p>
    `;

    // Log results to console
    console.log(`Down Payment: $${downPayment.toFixed(2)}`);
    console.log(`Remaining Amount: $${remainingAmount.toFixed(2)}`);
    console.log(`Monthly Payment: $${monthlyPayment.toFixed(2)} for ${loanTerm} months`);

});