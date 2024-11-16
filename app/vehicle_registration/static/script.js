function populateDays(selectId) {
    const selectElement = document.getElementById(selectId);
    // Create a default option that is not selectable
    const defaultOption = new Option("DD", "", true, true);
    defaultOption.disabled = true; // Make it non-clickable
    selectElement.appendChild(defaultOption);

    for (let i = 1; i <= 31; i++) {
        selectElement.options[selectElement.options.length] = new Option(i, i);
    }
}

function populateMonths(selectId) {
    const months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    const selectElement = document.getElementById(selectId);
    // Create a default option that is not selectable
    const defaultOption = new Option("MM", "", true, true);
    defaultOption.disabled = true; // Make it non-clickable
    selectElement.appendChild(defaultOption);

    months.forEach((month, index) => {
        selectElement.options[selectElement.options.length] = new Option(month, index + 1);
    });
}

function populateYears(selectId) {
    const currentYear = new Date().getFullYear();
    const selectElement = document.getElementById(selectId);
    // Create a default option that is not selectable
    const defaultOption = new Option("YYYY", "", true, true);
    defaultOption.disabled = true; // Make it non-clickable
    selectElement.appendChild(defaultOption);

    for (let i = currentYear; i >= 1900; i--) {
        selectElement.options[selectElement.options.length] = new Option(i, i);
    }
}

// Populate all dropdowns when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    populateDays('daySelectIssued');
    populateMonths('monthSelectIssued');
    populateYears('yearSelectIssued');

    populateDays('daySelectCertIssued');
    populateMonths('monthSelectCertIssued');
    populateYears('yearSelectCertIssued');

    populateDays('daySelectReceiptIssued');
    populateMonths('monthSelectReceiptIssued');
    populateYears('yearSelectReceiptIssued');

    populateDays('daySelectExpiry');
    populateMonths('monthSelectExpiry');
    populateYears('yearSelectExpiry');
});


document.addEventListener("DOMContentLoaded", function() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const saveButton = document.querySelector('.save-btn');

    function validateTab(tabContent) {
        const requiredFields = tabContent.querySelectorAll('[required]');
        let allFilled = true;

        requiredFields.forEach(field => {
            if (!field.value) {
                allFilled = false;
                field.classList.add('error'); // Add error class to highlight the field
            } else {
                field.classList.remove('error'); // Remove error class if field is filled
            }
        });

        return allFilled;
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', function(event) {
            const currentTabContent = document.querySelector('.tab-content.active');

            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Hide all tab contents
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to the clicked tab
            this.classList.add('active');
            // Show the corresponding tab content
            const activeTab = this.getAttribute('data-tab');
            document.getElementById(activeTab).classList.add('active');
        });
    });

    saveButton.addEventListener('click', function(event) {
        let allTabsValid = true;
        let firstInvalidTab = null;

        tabContents.forEach(tabContent => {
            if (!validateTab(tabContent)) {
                allTabsValid = false;
                if (!firstInvalidTab) {
                    firstInvalidTab = tabContent;
                }
            }
        });

        if (!allTabsValid) {
            event.preventDefault(); // Prevent form submission
            alert('Please fill all required fields before submitting the form.');

            // Switch to the first tab with invalid fields
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            const invalidTabId = firstInvalidTab.getAttribute('id');
            document.querySelector(`.tab[data-tab="${invalidTabId}"]`).classList.add('active');
            firstInvalidTab.classList.add('active');
        }
    });
});

const vehicleMakes = {
    motorcycle: ['Honda', 'Yamaha', 'Suzuki', 'Kawasaki', 'KTM', 'Royal Enfield', 'BMW Motorrad', 'Others'],
    car: ['Toyota', 'Honda', 'Mitsubishi', 'Nissan', 'Hyundai', 'Kia', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz', 'Others'],
    suv: ['Toyota', 'Mitsubishi', 'Nissan', 'Honda', 'Hyundai', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz', 'Others'],
    van: ['Toyota', 'Nissan', 'Hyundai', 'Ford', 'Foton', 'Others'],
    pickup: ['Toyota', 'Mitsubishi', 'Nissan', 'Ford', 'Chevrolet', 'Isuzu', 'Others'],
    truck: ['Isuzu', 'Hino', 'Fuso', 'Foton', 'Others'],
    others: ['Others']
};

const vehicleModels = {
    // Motorcycle Models
    honda: {
        motorcycle: ['Click 125i', 'Click 160', 'Beat', 'PCX 160', 'TMX Supremo', 'XRM 125', 'RS150', 'ADV 160', 'CBR 150', 'Others'],
        car: ['Civic', 'City', 'Accord', 'BR-V', 'Brio'],
        suv: ['CR-V', 'HR-V']
    },
    yamaha: {
        motorcycle: ['Mio i125', 'Mio Soul i125', 'Mio Aerox', 'NMAX', 'Sniper 155', 'XSR 155', 'MT-15', 'YZF-R15', 'Others']
    },
    suzuki: {
        motorcycle: ['Raider R150', 'Skydrive', 'Smash', 'Burgman', 'Gixxer', 'Others'],
        car: ['Swift', 'Dzire', 'Ertiga', 'Jimny']
    },
    kawasaki: {
        motorcycle: ['Ninja 400', 'Ninja 650', 'Barako II', 'CT125', 'Rouser NS160', 'Dominar 400', 'Others']
    },
    ktm: {
        motorcycle: ['Duke 200', 'Duke 390', 'RC 200', 'RC 390', 'Adventure 390', 'Others']
    },
    'royal enfield': {
        motorcycle: ['Classic 350', 'Meteor 350', 'Himalayan', 'Continental GT 650', 'Others']
    },
    'bmw motorrad': {
        motorcycle: ['G 310 R', 'R 1250 GS', 'S 1000 RR', 'F 900 R', 'Others']
    },
    // Car Models
    toyota: {
        car: ['Vios', 'Corolla Altis', 'Camry', 'Raize', 'Wigo'],
        suv: ['Fortuner', 'RAV4', 'Rush', 'Land Cruiser'],
        van: ['Hiace', 'Grandia'],
        pickup: ['Hilux']
    },
    mitsubishi: {
        car: ['Mirage', 'Mirage G4'],
        suv: ['Montero Sport', 'Xpander Cross'],
        pickup: ['Strada']
    },
    nissan: {
        car: ['Almera', 'Sylphy'],
        suv: ['Terra', 'X-Trail', 'Patrol'],
        van: ['NV350 Urvan'],
        pickup: ['Navara']
    },
    // Add more manufacturers as needed
    others: {
        motorcycle: ['Other'],
        car: ['Other'],
        suv: ['Other'],
        van: ['Other'],
        pickup: ['Other'],
        truck: ['Other']
    },
    // Car Manufacturers
    hyundai: {
        car: ['Accent', 'Elantra', 'Reina', 'Ioniq', 'Veloster', 'Sonata', 'Others'],
        suv: ['Tucson', 'Santa Fe', 'Palisade', 'Venue', 'Kona', 'Creta', 'Others'],
        van: ['Starex', 'Grand Starex', 'H-100', 'Staria', 'Others']
    },
    kia: {
        car: ['Picanto', 'Rio', 'Forte', 'Soluto', 'K2500', 'K3', 'Others'],
        suv: ['Seltos', 'Sportage', 'Sorento', 'Carnival', 'Stonic', 'Others'],
        van: ['Carnival', 'Grand Carnival', 'Others']
    },
    ford: {
        car: ['Mustang', 'Focus', 'Fiesta', 'GT', 'Raptor'],
        suv: ['Territory', 'Explorer', 'Expedition', 'Everest', 'EcoSport', 'Others'],
        van: ['Transit', 'E-150', 'Others'],
        pickup: ['Ranger', 'Ranger Raptor', 'F-150', 'Others']
    },
    chevrolet: {
        car: ['Spark', 'Sail', 'Malibu', 'Camaro', 'Corvette', 'Others'],
        suv: ['Trailblazer', 'Suburban', 'Tahoe', 'Tracker', 'Trax', 'Others'],
        pickup: ['Colorado', 'Silverado', 'Others']
    },
    bmw: {
        car: ['1 Series', '2 Series', '3 Series', '4 Series', '5 Series', '6 Series', '7 Series', '8 Series', 'M2', 'M3', 'M4', 'M5', 'M8', 'Others'],
        suv: ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'XM', 'Others']
    },
    'mercedes-benz': {
        car: ['A-Class', 'B-Class', 'C-Class', 'E-Class', 'S-Class', 'CLA', 'CLS', 'AMG GT', 'Others'],
        suv: ['GLA', 'GLB', 'GLC', 'GLE', 'GLS', 'G-Class', 'Others'],
        van: ['V-Class', 'Sprinter', 'Others']
    },
    foton: {
        van: ['Gratour TM', 'Toano', 'Transvan', 'View Traveller', 'View C2', 'Gratour iM6', 'Others'],
        truck: ['Tornado', 'Thunder', 'Harabas', 'Gratour', 'EST-M', 'FT-Series', 'Others']
    },
    // Truck Manufacturers
    isuzu: {
        truck: ['ELF/N-Series', 'FRR', 'FSR', 'FTR', 'FVM', 'GVR', 'CYZ', 'EXZ', 'GXZ', 'C&E Series', 'Others'],
        pickup: ['D-MAX', 'D-MAX X-Series', 'Others']
    },
    hino: {
        truck: ['300 Series', '500 Series', '700 Series', 'XZU', 'FG', 'FL', 'FM', 'SG', 'SS', 'ZS', 'Others']
    },
    fuso: {
        truck: ['Canter', 'Fighter', 'Super Great', 'FI', 'FJ', 'FG', 'FZ', 'TV', 'TF', 'Others']
    },
    foton: {
        van: ['Gratour TM', 'Toano', 'Transvan', 'View Traveller', 'View C2', 'Gratour iM6', 'Others'],
        truck: ['Tornado', 'Thunder', 'Harabas', 'Gratour', 'EST-M', 'FT-Series', 'ETX', 'GTL', 'Others']
    },
    others: {
        motorcycle: ['Other'],
        car: ['Other'],
        suv: ['Other'],
        van: ['Other'],
        pickup: ['Other'],
        truck: ['Other']
    }
};

document.addEventListener('DOMContentLoaded', function() {
    const typeSelect = document.getElementById('vehicleType');
    const makeSelect = document.getElementById('vehicleMake');
    const modelSelect = document.getElementById('vehicleModel');

    // Update makes when type changes
    typeSelect.addEventListener('change', function() {
        const selectedType = this.value;
        makeSelect.innerHTML = '<option value="" disabled selected>Select Make</option>';
        modelSelect.innerHTML = '<option value="" disabled selected>Select Model</option>';
        
        if (selectedType && vehicleMakes[selectedType]) {
            // Filter makes based on vehicle type
            vehicleMakes[selectedType].forEach(make => {
                const option = document.createElement('option');
                option.value = make.toLowerCase();
                option.textContent = make;
                makeSelect.appendChild(option);
            });
        }
    });

    // Update models when make changes
    makeSelect.addEventListener('change', function() {
        const selectedType = typeSelect.value;
        const selectedMake = this.value;
        modelSelect.innerHTML = '<option value="" disabled selected>Select Model</option>';
        
        if (selectedMake && vehicleModels[selectedMake] && vehicleModels[selectedMake][selectedType]) {
            vehicleModels[selectedMake][selectedType].forEach(model => {
                const option = document.createElement('option');
                option.value = model.toLowerCase();
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        }
    });

    // Add validation for form submission
    const form = document.getElementById('vehiclePassForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const selectedType = typeSelect.value;
            const selectedMake = makeSelect.value;
            const selectedModel = modelSelect.value;

            if (!selectedType || !selectedMake || !selectedModel) {
                e.preventDefault();
                alert('Please select vehicle type, make, and model');
                return false;
            }

            // Additional validation for motorcycle
            if (selectedType === 'motorcycle' && !vehicleMakes.motorcycle.includes(makeSelect.options[makeSelect.selectedIndex].text)) {
                e.preventDefault();
                alert('Please select a valid motorcycle manufacturer');
                return false;
            }
        });
    }

    const colorSelect = document.getElementById('color');
    
    colorSelect.addEventListener('change', function() {
        if (this.value === 'others') {
            const customColor = prompt('Please enter the color:');
            if (customColor && customColor.trim() !== '') {
                // Add new option for custom color
                const option = document.createElement('option');
                option.value = customColor.toLowerCase();
                option.textContent = customColor;
                this.insertBefore(option, this.lastElementChild); // Insert before "Others"
                this.value = customColor.toLowerCase(); // Select the new option
            } else {
                this.value = ''; // Reset to default if no color entered
            }
        }
    });
});