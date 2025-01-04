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

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Hide all tab contents
            tabContents.forEach(content => content.style.display = 'none');

            // Add active class to the clicked tab
            this.classList.add('active');
            // Show the corresponding tab content
            const activeTab = this.getAttribute('data-tab');
            document.getElementById(activeTab).style.display = 'block';
        });
    });
});


