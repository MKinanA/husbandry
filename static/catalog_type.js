const typeFiltersData = [{name: 'Semua jenis', value: 'all'}, ...typeFilters];

// Contoh data produk
let currentTypeFilter = (new URLSearchParams(document.location.search)).get('type') ?? typeFiltersData[0].value;

// Elements
const typeFilterButton = document.querySelector('.type-filter #filterButton');
const typeDropdownMenu = document.querySelector('.type-filter #dropdownMenu');
const typeDropdownIcon = document.querySelector('.type-filter #dropdownIcon');
const selectedTypeFilter = document.querySelector('.type-filter #selectedFilter');
const typeFilterOptions = document.querySelector('.type-filter #filterOptions');

if (currentTypeFilter != typeFiltersData[0].value) selectedTypeFilter.textContent = typeFiltersData.filter(filter => filter.value == currentTypeFilter)[0].name;

// Generate filter options
function generateTypeFilterOptions() {
    typeFilterOptions.innerHTML = typeFiltersData.map(filter => `
        <button 
            class="w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors text-gray-700"
            onclick="selectTypeFilter('${filter.value}', '${filter.name}')"
        >
            ${filter.name}
        </button>
    `).join('');
}

// Toggle dropdown
typeFilterButton.addEventListener('click', (e) => {
    e.stopPropagation();
    const isHidden = typeDropdownMenu.classList.contains('hidden');
    if (isHidden) {
        typeDropdownMenu.classList.remove('hidden');
        typeDropdownIcon.style.transform = 'rotate(180deg)';
    } else {
        typeDropdownMenu.classList.add('hidden');
        typeDropdownIcon.style.transform = 'rotate(0deg)';
    }
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!typeFilterButton.contains(e.target) && !typeDropdownMenu.contains(e.target)) {
        typeDropdownMenu.classList.add('hidden');
        typeDropdownIcon.style.transform = 'rotate(0deg)';
    }
});

// Select filter
function selectTypeFilter(value, name) {
    currentTypeFilter = value;
    selectedTypeFilter.textContent = name;
    typeDropdownMenu.classList.add('hidden');
    typeDropdownIcon.style.transform = 'rotate(0deg)';
    applyTypeFilter();
}

// Apply filter logic
function applyTypeFilter() {
    let params = [...(currentTypeFilter != 'all' ? [`type=${currentTypeFilter}`] : []), ...(loc.split('?')[1]?.split('&').filter(param => param.split('=')[0] != 'type') ?? [])];
    window.open(loc.split('?')[0] + (params.length > 0 ? '?' + params.join('&') : ''), '_self');
}

// Initialize
generateTypeFilterOptions();