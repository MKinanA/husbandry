const loc = window.location.href;
const bookButton = document.getElementById('book-button');

if (productState != 'saleable') {
    bookButton.classList.add('pointer-events-none');
    bookButton.classList.remove('bg-green-700');
    bookButton.classList.remove('hover:bg-green-900');
    bookButton.classList.add('bg-gray-950');
    bookButton.classList.add('opacity-50');
    bookButton.innerText = 'Booked'
};

bookButton.addEventListener('click', async event => {
    console.log('book button clicked');
    response = await fetch(`${bookButton.dataset.bookApi}?customer_name=example&customer_number=example&customer_email=example&customer_address=example`);
    if ((await response.json()) === true) location.reload();
});