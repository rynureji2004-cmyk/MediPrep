// Global JavaScript functions for Hospital Readiness Platform
document.addEventListener("DOMContentLoaded", () => {
    console.log("MediPrep Client Readiness System Initialized.");
    
    // Auto fade-out system alerts after 5 seconds
    const alerts = document.querySelectorAll('.flash-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s ease-out";
            alert.style.opacity = "0";
            setTimeout(() => {
                alert.style.display = "none";
            }, 500);
        }, 5000);
    });
});
