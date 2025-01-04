const itemsPerPage = 10; // Number of items to display per page
let currentPage = 1;
const rows = document.querySelectorAll('#vehicleTableBody .vehicle-row');
const pageCount = Math.ceil(rows.length / itemsPerPage);

function showPage(page) {
  const startIndex = (page - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;

  rows.forEach((row, index) => {
    if (index >= startIndex && index < endIndex) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

function setupPagination() {
  const paginationElement = document.getElementById('pagination');
  paginationElement.innerHTML = '';

  for (let i = 1; i <= pageCount; i++) {
    const li = document.createElement('li');
    li.classList.add('page-item');
    if (i === currentPage) {
      li.classList.add('active');
    }
    const a = document.createElement('a');
    a.classList.add('page-link');
    a.href = '#';
    a.textContent = i;
    a.addEventListener('click', (e) => {
      e.preventDefault();
      currentPage = i;
      showPage(currentPage);
      setupPagination();
    });
    li.appendChild(a);
    paginationElement.appendChild(li);
  }
}

// Initial setup
showPage(currentPage);
setupPagination();


// JavaScript to toggle the dropdown
var dropdownBtns = document.querySelectorAll(".dropdown-btn");
var dropdownContainers = document.querySelectorAll(
  ".dropdown-container, .dropdown-container2"
);

// Loop through each button to add click event listeners
dropdownBtns.forEach((btn, index) => {
  btn.addEventListener("click", function () {
    // Toggle the display of the corresponding dropdown container
    var dropdownContainer = dropdownContainers[index];
    dropdownContainer.style.display =
      dropdownContainer.style.display === "block" ? "none" : "block";
  });
});


document.addEventListener("DOMContentLoaded", function () {
  const tabs = document.querySelectorAll(".tab");
  const tabContents = document.querySelectorAll(".tab-content");

  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      // Remove active class from all tabs
      tabs.forEach((t) => t.classList.remove("active"));
      // Hide all tab contents
      tabContents.forEach((content) => (content.style.display = "none"));

      // Add active class to the clicked tab
      this.classList.add("active");
      // Show the corresponding tab content
      const activeTab = this.getAttribute("data-tab");
      document.getElementById(activeTab).style.display = "block";
    });
  });
});

let currentSlide = 0;

function changeSlide(direction) {
  const slides = document.querySelectorAll(".slide");
  slides[currentSlide].classList.remove("active");

  currentSlide = (currentSlide + direction + slides.length) % slides.length;

  slides[currentSlide].classList.add("active");
}

// Show Sticker Number Input Modal on Approve Button Click

// Show Sticker Number Input Modal on Approve Button Click

// Handle Sticker Number Submission
document
  .getElementById("saveStickerBtn")
  .addEventListener("click", function () {
    var stickerNumber = document.getElementById("stickerNumber").value;
    if (stickerNumber) {
      // Action with the sticker number
      alert("Sticker Number Saved: " + stickerNumber);

      // Close the modal
      $("#stickerModal").modal("hide");
    } else {
      alert("Please enter a sticker number.");
    }
  });

  const saveBtn = document.querySelector(".save-btn");
  if (saveBtn) {
      saveBtn.addEventListener("click", function () {
          $("#stickerModal").modal("show");
      });
  }
  
  // For denied button
  const deniedBtn = document.querySelector(".denied-btn");
  if (deniedBtn) {
      deniedBtn.addEventListener("click", function () {
          $("#reasonModal").modal("show");
      });
  }
$("#viewModal").on("show.bs.modal", function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal
  var modal = $(this);

  // Populate modal fields with data from the button
  modal.find(".modal-body #user-name").text(button.data("user-name"));
  modal.find(".modal-body #user-id").text(button.data("user-id"));
  modal.find(".modal-body #user-photo").attr("src", button.data("user-photo"));
  modal.find(".modal-body #contactNo").val(button.data("contact"));
  modal.find(".modal-body #driversLicense").val(button.data("license"));
  modal.find(".modal-body #dateIssued").val(button.data("date-issued"));
  modal.find(".modal-body #dateExpiry").val(button.data("date-expiry"));
  modal.find(".modal-body #vehicleType").val(button.data("vehicle-type"));
  modal.find(".modal-body #vehicleMake").val(button.data("vehicle-make"));
  modal.find(".modal-body #vehicleModel").val(button.data("vehicle-model"));
  modal.find(".modal-body #vehicleYear").val(button.data("vehicle-year"));
  modal.find(".modal-body #plateNumber").val(button.data("plate-number"));
  modal.find(".modal-body #color").val(button.data("color"));
  modal.find(".modal-body #certificate").val(button.data("certificate"));
  modal.find(".modal-body #dateCertIssued").val(button.data("cert-issued"));
  modal.find(".modal-body #receipt").val(button.data("receipt"));
  modal
    .find(".modal-body #dateReceiptIssued")
    .val(button.data("receipt-issued"));
  modal.find(".modal-body #driverName").val(button.data("driver-name"));
  modal.find(".modal-body #licenseNumber").val(button.data("license-number"));
  modal.find(".modal-body #relationship").val(button.data("relationship"));
  modal
    .find(".modal-body #vehicleOrcr")
    .attr("src", button.data("vehicle-orcr"));
  modal
    .find(".modal-body #licenseCard")
    .attr("src", button.data("license-card"));
  modal
    .find(".modal-body #vehiclePhoto")
    .attr("src", button.data("vehicle-photo"));
  modal.find(".modal-body #dropIssued").val(button.data("drop-issued"));
  modal.find(".modal-body #dropExpiry").val(button.data("drop-expiry"));
});

document
  .getElementById("date-filter-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const startDate = new Date(document.getElementById("start-date").value);
    const endDate = new Date(document.getElementById("end-date").value);
    const rows = document.querySelectorAll("tbody tr");

    rows.forEach((row) => {
      const dateExpiryText = row.querySelector(".date-expiry").textContent;
      const [day, month, year] = dateExpiryText.split("-");
      const dateExpiry = new Date(year, month - 1, day); // month is zero-based

      if (dateExpiry >= startDate && dateExpiry <= endDate) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  });

document.getElementById("reset-button").addEventListener("click", function () {
  document.getElementById("start-date").value = "";
  document.getElementById("end-date").value = "";
  const rows = document.querySelectorAll("tbody tr");
  rows.forEach((row) => {
    row.style.display = "";
  });
});

document.getElementById("search-button").addEventListener("click", function () {
  const searchQuery = document
    .getElementById("search-input")
    .value.toLowerCase();
  const rows = document.querySelectorAll("tbody tr");

  rows.forEach((row) => {
    const ownerName = row
      .querySelector(".owner-name")
      .textContent.toLowerCase();
    const plateNumber = row
      .querySelector(".plate-number")
      .textContent.toLowerCase();

    if (ownerName.includes(searchQuery) || plateNumber.includes(searchQuery)) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
});



