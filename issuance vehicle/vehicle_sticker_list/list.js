
        // JavaScript to toggle the dropdown
        var dropdownBtns = document.querySelectorAll('.dropdown-btn');
        var dropdownContainers = document.querySelectorAll('.dropdown-container, .dropdown-container2');

        // Loop through each button to add click event listeners
        dropdownBtns.forEach((btn, index) => {
            btn.addEventListener('click', function() {
                // Toggle the display of the corresponding dropdown container
                var dropdownContainer = dropdownContainers[index];
                dropdownContainer.style.display = dropdownContainer.style.display === 'block' ? 'none' : 'block';
            });
        });

        // Show Modal with Vehicle Info
        var viewButtons = document.querySelectorAll('.view-btn');
        viewButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Fetch data from table row (you can enhance this to fetch from a database)
                var vehicleNo = this.getAttribute('data-vehicle');
                var name = this.closest('tr').querySelector('td:nth-child(2)').textContent;
                
                // Fill modal fields with data
                document.getElementById('vehicleNo').value = vehicleNo;
                document.getElementById('name').value = name;
                // Additional data fields can be populated here

                // Show the modal
                $('#vehicleModal').modal('show');
            });
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

let currentSlide = 0;

function changeSlide(direction) {
    const slides = document.querySelectorAll('.slide');
    slides[currentSlide].classList.remove('active');

    currentSlide = (currentSlide + direction + slides.length) % slides.length;

    slides[currentSlide].classList.add('active');
}

// Handle Sticker Number Submission
document.getElementById('saveStickerBtn').addEventListener('click', function () {
    var stickerNumber = document.getElementById('stickerNumber').value;
    if (stickerNumber) {
        // Action with the sticker number
        alert("Sticker Number Saved: " + stickerNumber);

        // Close the modal
        $('#stickerModal').modal('hide');
    } else {
        alert("Please enter a sticker number.");
    }
});

// Show Reason Modal on Denied Button Click
document.querySelector('.denied-btn').addEventListener('click', function () {
            $('#reasonModal').modal('show');
        });

        // Handle Reason Submission
        document.getElementById('submitReasonBtn').addEventListener('click', function () {
            var denialReason = document.getElementById('denialReason').value;
            if (denialReason) {
                alert("Reason for Denial: " + denialReason);
                $('#reasonModal').modal('hide');
            } else {
                alert("Please enter a reason for denial.");
            }
        });

