/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function toggleDropdown() {
    document.getElementById("navmenu").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
    if (!(event.target.matches('#hamburger-menu') || event.target.matches('#hamburger-menu img')) && !document.getElementsByClassName("navmenu")[0].contains(event.target)) {
        var openDropdown = document.getElementsByClassName("navmenu")[0];
        if (openDropdown.classList.contains('show')) {
            openDropdown.classList.remove('show');
        }
    }
}