const priceFiltersData = [{name: 'Semua harga', value: 'all'}, ...priceFilters];

// Contoh data produk
let currentPriceFilter = (new URLSearchParams(document.location.search)).get('price') ?? priceFiltersData[0].value;

// Elements
const priceFilterButton = document.querySelector('.price-filter #filterButton');
const priceDropdownMenu = document.querySelector('.price-filter #dropdownMenu');
const priceDropdownIcon = document.querySelector('.price-filter #dropdownIcon');
const selectedPriceFilter = document.querySelector('.price-filter #selectedFilter');
const priceFilterOptions = document.querySelector('.price-filter #filterOptions');

if (currentPriceFilter != priceFiltersData[0].value) selectedPriceFilter.textContent = priceFiltersData.filter(filter => filter.value == currentPriceFilter)[0].name;

// Generate filter options
function generatePriceFilterOptions() {
    priceFilterOptions.innerHTML = priceFiltersData.map(filter => `
        <button 
            class="w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors text-gray-700"
            onclick="selectPriceFilter('${filter.value}', '${filter.name}')"
        >
            ${filter.name}
        </button>
    `).join('');
}

// Toggle dropdown
priceFilterButton.addEventListener('click', (e) => {
    e.stopPropagation();
    const isHidden = priceDropdownMenu.classList.contains('hidden');
    if (isHidden) {
        priceDropdownMenu.classList.remove('hidden');
        priceDropdownIcon.style.transform = 'rotate(180deg)';
    } else {
        priceDropdownMenu.classList.add('hidden');
        priceDropdownIcon.style.transform = 'rotate(0deg)';
    }
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!priceFilterButton.contains(e.target) && !priceDropdownMenu.contains(e.target)) {
        priceDropdownMenu.classList.add('hidden');
        priceDropdownIcon.style.transform = 'rotate(0deg)';
    }
});

// Select filter
function selectPriceFilter(value, name) {
    currentPriceFilter = value;
    selectedPriceFilter.textContent = name;
    priceDropdownMenu.classList.add('hidden');
    priceDropdownIcon.style.transform = 'rotate(0deg)';
    applyPriceFilter();
}

// Apply filter logic
function applyPriceFilter() {
    let params = [...(currentPriceFilter != 'all' ? [`price=${currentPriceFilter}`] : []), ...(loc.split('?')[1]?.split('&').filter(param => param.split('=')[0] != 'price') ?? [])];
    window.open(loc.split('?')[0] + (params.length > 0 ? '?' + params.join('&') : ''), '_self');
}

// Initialize
generatePriceFilterOptions();