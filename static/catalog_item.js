const loc = window.location.href;
const bookButton = document.getElementById('book-button');
const bookForm = document.getElementById('book-form');

if (productState != 'saleable') {
    bookButton.classList.add('pointer-events-none');
    bookButton.classList.remove('bg-green-700');
    bookButton.classList.remove('hover:bg-green-900');
    bookButton.classList.add('bg-gray-950');
    bookButton.classList.add('opacity-50');
    bookButton.innerText = 'Booked'
};

async function book(customerName = undefined, customerNumber = undefined, customerEmail = undefined, customerAddress = undefined) {
    response = await fetch(`${bookButton.dataset.bookApi}${{
        'farm': '',
        'dkm': `?customer_name=${customerName}&customer_number=${customerNumber}&customer_email=${customerEmail}&customer_address=${customerAddress}`,
    }[catalogType]}`);
    if ((await response.json()) === true) location.reload();
};

function submitBookForm(event) {
    event.preventDefault()

    customerName = document.getElementById('book-form-customer-name').value;
    customerNumber = document.getElementById('book-form-customer-number').value;
    customerEmail = document.getElementById('book-form-customer-email').value;
    customerAddress = document.getElementById('book-form-customer-address').value;

    if (customerName === '') {
        alert('Name must be set.');
        return;
    };

    if (customerNumber === '' && customerEmail === '') {
        alert('Number or email must be set.');
        return;
    };

    book(customerName, customerNumber, customerEmail, customerAddress);
};

function showBookForm() {bookForm.classList.remove('hidden');};
function hideBookForm() {bookForm.classList.add('hidden');};

bookButton.addEventListener('click', async event => {
    console.log('book button clicked');
    if (catalogType == 'dkm') showBookForm();
    else book()
});