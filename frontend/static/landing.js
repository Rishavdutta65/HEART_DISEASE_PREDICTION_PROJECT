function showTransition() {
    const shell = document.getElementById("landingShell");
    shell.classList.add("slide-up");
    setTimeout(() => {
        window.location.href = "/dashboard";
    }, 900);
}
