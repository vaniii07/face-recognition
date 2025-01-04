const provinceSelect = document.getElementById('province');
const citySelect = document.getElementById('city');
const barangaySelect = document.getElementById('barangay');
let provinces = {};

// Fetch provinces
fetch('https://psgc.gitlab.io/api/provinces/')
  .then(response => response.json())
  .then(data => {
    data.forEach(province => {
      const option = document.createElement('option');
      option.value = province.code;
      option.textContent = province.name;
      provinceSelect.appendChild(option);
      provinces[province.code] = [];
    });
  });

// Fetch cities when a province is selected
provinceSelect.addEventListener('change', function() {
  const provinceCode = this.value;
  citySelect.innerHTML = '<option value="">Please Select City</option>';
  barangaySelect.innerHTML = '<option value="">Please Select Barangay</option>';

  if (provinceCode) {
    fetch(`https://psgc.gitlab.io/api/provinces/${provinceCode}/cities-municipalities/`)
      .then(response => response.json())
      .then(data => {
        data.forEach(city => {
          const option = document.createElement('option');
          option.value = city.code;
          option.textContent = city.name;
          citySelect.appendChild(option);
          provinces[provinceCode].push(city.code);
        });
      });
  }
});

// Fetch barangays when a city is selected
citySelect.addEventListener('change', function() {
  const cityCode = this.value;
  barangaySelect.innerHTML = '<option value="">Please Select Barangay</option>';

  if (cityCode) {
    fetch(`https://psgc.gitlab.io/api/cities-municipalities/${cityCode}/barangays/`)
      .then(response => response.json())
      .then(data => {
        data.forEach(barangay => {
          const option = document.createElement('option');
          option.value = barangay.code;
          option.textContent = barangay.name;
          barangaySelect.appendChild(option);
        });
      });
  }
});

function validateStep(step) {
  const formStep = formSteps[step - 1];
  const inputs = formStep.querySelectorAll('input, select');
  let valid = true;
  let emptyFields = [];

  inputs.forEach(input => {
    // Skip the middle initial if it's empty
    if (input.placeholder === "e.g. Optional" && !input.value) {
      return;
    }

     // Skip city and barangay validation if the selected province has no cities
     if (input.name === "city" || input.name === "barangay") {
      const selectedProvince = document.getElementById('province').value;
      const cities = provinces[selectedProvince] || [];
      if (cities.length === 0) {
        input.removeAttribute('required');
        return;
      } else {
        input.setAttribute('required', 'required');
      }
    }

    if (!input.value) {
      valid = false;
      emptyFields.push(input.previousElementSibling ? input.previousElementSibling.innerText : 'Unknown field');
      input.style.border = '1px solid red'; // Make the border of empty fields red
    } else {
      input.style.border = ''; // Reset border style if field is not empty
    }
  });

  if (!valid) {
    // Display header and list of empty fields in red
    alert(`Please fill in the following fields:\n\n${emptyFields.join('\n')}`);
  }

  return valid;
}