let currentRating = 0;

// Handle star rating
document.querySelectorAll('.star').forEach(star => {
    star.addEventListener('click', () => {
        currentRating = star.getAttribute('data-value');
        document.getElementById('rating-value').textContent = currentRating;
        document.querySelectorAll('.star').forEach(s => {
            s.classList.toggle('filled', s.getAttribute('data-value') <= currentRating);
        });
    });
});



// Handle form submission
document.getElementById('submit').addEventListener('click', () => {
    const comment = document.getElementById('comment').value.trim();
    if (currentRating === 0) {
        alert('Please select a star rating!');
        return;
    }
    if (!comment) {
        alert('Please write a comment!');
        return;
    }

    // Log review to console
    console.log(`Rating: ${currentRating} stars`);
    console.log(`Comment: ${comment}`);

    // Reset form
    currentRating = 0;
    document.getElementById('rating-value').textContent = '0';
    document.getElementById('comment').value = '';
    document.querySelectorAll('.star').forEach(s => s.classList.remove('filled'));


});

