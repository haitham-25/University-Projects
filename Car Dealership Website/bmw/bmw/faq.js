
const chatButton = document.querySelector('.chat-button');
const chatPopup = document.getElementById('chatPopup');
const closeBtn = document.getElementById('closeBtn');

chatButton.addEventListener('click', function() {
    chatPopup.style.display = 'block';
});

closeBtn.addEventListener('click', function() {
    chatPopup.style.display = 'none';
});

document.querySelectorAll('.option').forEach(option => {
    option.addEventListener('click', function() {
        if (this.textContent.includes('FAQ')) {

            window.open('FAQ.html', '_blank');
        } else if (this.textContent.includes('Contact')) {

            window.open('Contact_a_Dealer.html', '_blank');
        }
    });
});






