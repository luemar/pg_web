// script.js - Required for the special.html page

// Function to force a refresh of the page with a cache-busting parameter
function refreshData() {
    // Add a timestamp to prevent caching
    const timestamp = new Date().getTime();
    window.location.href = '/special?t=' + timestamp;
}

// Function to check if Excel file has been updated
function checkExcelUpdate() {
    fetch('/check_excel_update')
        .then(response => response.text())
        .then(data => {
            alert(data);
        })
        .catch(error => {
            console.error('Error checking Excel update:', error);
        });
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add any page initialization code here
    console.log('Script loaded successfully');
});