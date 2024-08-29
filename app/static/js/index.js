function updateFileName(input) {
    var fileName = input.files[0].name;
    var fileNameElement = document.getElementById("file-name");
    fileNameElement.textContent = fileName;
}

document.addEventListener('DOMContentLoaded', function () {
    function smoothScrollToTarget(targetId) {
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop,
                behavior: 'smooth'
            });
        }
    }

    // Handle anchor link scroll if on the same page
    const hash = window.location.hash;
    if (hash) {
        const targetId = hash.substring(1);
        smoothScrollToTarget(`#${targetId}`);
    }

    // Handle button click for smooth scrolling
    document.querySelectorAll('.scrollButton').forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            smoothScrollToTarget(targetId);
        });
    });
});


document.getElementById('emailButton').addEventListener('click', function() {
    window.location.href = 'mailto:danylo.provodov@gmail.com';
});
