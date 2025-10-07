// Process every product card and book button
document.querySelectorAll('.product-card').forEach(productCard => {
    const bookButton = document.querySelector(`#${productCard.id} .book-button`);
    if (productStates[productCard.id] != 'saleable') {
        bookButton.classList.add('pointer-events-none');
        bookButton.classList.remove('bg-green-700');
        bookButton.classList.remove('hover:bg-green-900');
        bookButton.classList.add('bg-gray-950');
        bookButton.classList.add('opacity-50');
        bookButton.innerText = 'Booked'
    };
});