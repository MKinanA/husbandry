const loc = window.location.href;
const filtersData = [{name: 'All', value: 'all'}, ...filters];

// Contoh data produk
let currentFilter = (new URLSearchParams(document.location.search)).get('filter') ?? filtersData[0].value;

// Elements
const filterButton = document.querySelector('.type-filter #filterButton');
const dropdownMenu = document.querySelector('.type-filter #dropdownMenu');
const dropdownIcon = document.querySelector('.type-filter #dropdownIcon');
const selectedFilter = document.querySelector('.type-filter #selectedFilter');
const filterOptions = document.querySelector('.type-filter #filterOptions');
const productGrid = document.querySelector('.type-filter #productGrid');

if (currentFilter != filtersData[0].value) selectedFilter.textContent = filtersData.filter(filter => filter.value == currentFilter)[0].name;

// Generate filter options
function generateFilterOptions() {
    filterOptions.innerHTML = filtersData.map(filter => `
        <button 
            class="w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors text-gray-700"
            onclick="selectFilter('${filter.value}', '${filter.name}')"
        >
            ${filter.name}
        </button>
    `).join('');
}

// Toggle dropdown
filterButton.addEventListener('click', (e) => {
    e.stopPropagation();
    const isHidden = dropdownMenu.classList.contains('hidden');
    if (isHidden) {
        dropdownMenu.classList.remove('hidden');
        dropdownIcon.style.transform = 'rotate(180deg)';
    } else {
        dropdownMenu.classList.add('hidden');
        dropdownIcon.style.transform = 'rotate(0deg)';
    }
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!filterButton.contains(e.target) && !dropdownMenu.contains(e.target)) {
        dropdownMenu.classList.add('hidden');
        dropdownIcon.style.transform = 'rotate(0deg)';
    }
});

// Select filter
function selectFilter(value, name) {
    currentFilter = value;
    selectedFilter.textContent = name;
    dropdownMenu.classList.add('hidden');
    dropdownIcon.style.transform = 'rotate(0deg)';
    applyFilter();
}

// Apply filter logic
function applyFilter() {
    let params = [...(currentFilter != 'all' ? [`filter=${currentFilter}`] : []), ...(loc.split('?')[1]?.split('&').filter(param => param.split('=')[0] != 'filter') ?? [])];
    window.open(loc.split('?')[0] + (params.length > 0 ? '?' + params.join('&') : ''), '_self');
}

// Initialize
generateFilterOptions();