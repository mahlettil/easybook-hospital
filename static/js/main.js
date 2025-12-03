// Easybook Hospital Appointment System - JavaScript

// Auto-dismiss alerts after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      alert.style.transition = "opacity 0.5s";
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });
});

// Appointment Booking - Load doctors by specialty
function loadDoctorsBySpecialty() {
  const specialtySelect = document.getElementById("specialty");
  const doctorSelect = document.getElementById("doctor_id");

  if (!specialtySelect || !doctorSelect) return;

  specialtySelect.addEventListener("change", async function () {
    const specialtyId = this.value;
    doctorSelect.innerHTML = '<option value="">Select a doctor</option>';

    if (!specialtyId) {
      doctorSelect.disabled = true;
      return;
    }

    try {
      const response = await fetch(`/api/doctors/${specialtyId}`);
      const doctors = await response.json();

      if (doctors.length === 0) {
        doctorSelect.innerHTML =
          '<option value="">No doctors available</option>';
        doctorSelect.disabled = true;
        return;
      }

      doctors.forEach((doctor) => {
        const option = document.createElement("option");
        option.value = doctor.id;
        option.textContent = `${doctor.name} - ${doctor.qualification} (${doctor.experience_years} years exp)`;
        doctorSelect.appendChild(option);
      });

      doctorSelect.disabled = false;
    } catch (error) {
      console.error("Error loading doctors:", error);
      doctorSelect.innerHTML =
        '<option value="">Error loading doctors</option>';
    }
  });
}

// Load available time slots
function loadAvailableSlots() {
  const doctorSelect = document.getElementById("doctor_id");
  const dateInput = document.getElementById("appointment_date");
  const timeSelect = document.getElementById("appointment_time");

  if (!doctorSelect || !dateInput || !timeSelect) return;

  async function updateSlots() {
    const doctorId = doctorSelect.value;
    const date = dateInput.value;

    timeSelect.innerHTML = '<option value="">Select time</option>';

    if (!doctorId || !date) {
      timeSelect.disabled = true;
      return;
    }

    try {
      const response = await fetch(`/api/available-slots/${doctorId}/${date}`);
      const slots = await response.json();

      if (slots.length === 0) {
        timeSelect.innerHTML = '<option value="">No slots available</option>';
        timeSelect.disabled = true;
        return;
      }

      slots.forEach((slot) => {
        const option = document.createElement("option");
        option.value = slot;
        option.textContent = slot;
        timeSelect.appendChild(option);
      });

      timeSelect.disabled = false;
    } catch (error) {
      console.error("Error loading slots:", error);
      timeSelect.innerHTML = '<option value="">Error loading slots</option>';
    }
  }

  doctorSelect.addEventListener("change", updateSlots);
  dateInput.addEventListener("change", updateSlots);
}

// Set minimum date for appointment booking (today)
function setMinimumDate() {
  const dateInput = document.getElementById("appointment_date");
  if (dateInput) {
    const today = new Date().toISOString().split("T")[0];
    dateInput.setAttribute("min", today);
  }
}

// Confirm cancellation
function confirmCancel(event) {
  if (!confirm("Are you sure you want to cancel this appointment?")) {
    event.preventDefault();
  }
}

// Add cancel confirmation to all cancel forms
document.addEventListener("DOMContentLoaded", function () {
  const cancelForms = document.querySelectorAll(
    'form[action*="cancel-appointment"]'
  );
  cancelForms.forEach((form) => {
    form.addEventListener("submit", confirmCancel);
  });
});

// Initialize all functions
document.addEventListener("DOMContentLoaded", function () {
  loadDoctorsBySpecialty();
  loadAvailableSlots();
  setMinimumDate();
});

// Admin - Delete confirmation
function confirmDelete(itemName) {
  return confirm(
    `Are you sure you want to delete ${itemName}? This action cannot be undone.`
  );
}

// Format phone numbers
function formatPhone(input) {
  let value = input.value.replace(/\D/g, "");
  if (value.startsWith("251")) {
    value = "+" + value;
  } else if (value.startsWith("0")) {
    value = "+251" + value.substring(1);
  }
  input.value = value;
}

// Add phone formatting to phone inputs
document.addEventListener("DOMContentLoaded", function () {
  const phoneInputs = document.querySelectorAll('input[type="tel"]');
  phoneInputs.forEach((input) => {
    input.addEventListener("blur", () => formatPhone(input));
  });
});

// Table search functionality
function searchTable(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);

  if (!input || !table) return;

  input.addEventListener("keyup", function () {
    const filter = this.value.toLowerCase();
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const cells = row.getElementsByTagName("td");
      let found = false;

      for (let j = 0; j < cells.length; j++) {
        const cell = cells[j];
        if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
          found = true;
          break;
        }
      }

      row.style.display = found ? "" : "none";
    }
  });
}

// Print functionality
function printTable(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const printWindow = window.open("", "", "height=600,width=800");
  printWindow.document.write("<html><head><title>Print</title>");
  printWindow.document.write("<style>");
  printWindow.document.write(
    "table { border-collapse: collapse; width: 100%; }"
  );
  printWindow.document.write(
    "th, td { border: 1px solid black; padding: 8px; text-align: left; }"
  );
  printWindow.document.write("th { background-color: #f2f2f2; }");
  printWindow.document.write("</style></head><body>");
  printWindow.document.write(table.outerHTML);
  printWindow.document.write("</body></html>");
  printWindow.document.close();
  printWindow.print();
}
