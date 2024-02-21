function showModal(message) {
    document.getElementById('modalMessage').textContent = message;
    $('#myModal').modal('show'); // Using Bootstrap's modal functionality
}

function hideModal() {
    $('#myModal').modal('hide'); // Using Bootstrap's modal functionality
}

function check2pwd(event) {
    var nameRegex = /^[A-Za-z]+$/;
    var dateRegex = /^(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/\d{4}$/;
    var emailRegex = /^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(a-zA-Z]{2,})+$/;
    var postalcodeRegex = /^(([gG][iI][rR] 0[aA]{2})|(([a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y]?[0-9][0-9]?)|(([a-pr-uwyzA-PR-UWYZ][0-9][a-hjkstuwA-HJKSTUW])|([a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y][0-9][abehmnprv-yABEHMNPRV-Y]))) [0-9][abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2}))$/;

    var first_name = document.getElementById('first_name');
    var last_name = document.getElementById('last_name');
    var gender = document.getElementById('gender');
    var dob = document.getElementById('dob');
    var email = document.getElementById('email');
    var postcode = document.getElementById('postcode');
    var password = document.getElementById('password');
    var passwordnot = document.getElementById('passwordnot');

    // Validation logic here, showing modals on error
    // Each validation block would look something like this:
    if(first_name.value == ""){
        showModal("First name is empty, please enter your first name.");
        event.preventDefault();
        return false; // Stop form submission
    }
    // Similar validation checks for other fields...

    // If all validations pass
    return true; // Allow form submission
}

// Ensure jQuery is loaded to use Bootstrap's jQuery dependent features
document.addEventListener('DOMContentLoaded', function () {
    // Your code to run since DOM is loaded and ready
});
