// script.js
const wrapper = document.querySelector('.wrapper');
const loginLink = document.querySelector('.login-link');
const registerLink = document.querySelector('.register-link');
const btnPopup = document.querySelector('.btnlogin-popup');
const iconClose = document.querySelector('.icon-close');

registerLink?.addEventListener('click', (event) => {
    event.preventDefault();
    wrapper.classList.add('active');
});

loginLink?.addEventListener('click', (event) => {
    event.preventDefault();
    wrapper.classList.remove('active');
});

btnPopup?.addEventListener('click', () => {
    wrapper.classList.add('active-popup');
});

iconClose?.addEventListener('click', () => {
    wrapper.classList.remove('active-popup');
});

// Fix API URLs
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;
    try {
        const response = await fetch("http://localhost:3000/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (response.ok && data.redirect) {
            localStorage.setItem("userEmail", data.userEmail);
            window.location.href = data.redirect;
        } else {
            alert(data.error || "Login failed");
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        alert("Something went wrong. Check console for details.");
    }
}

document.getElementById("loginForm")?.addEventListener("submit", handleLogin);

// Ensure event listeners are attached after form rendering
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("registerForm")) {
        document.getElementById("registerForm").addEventListener("submit", async function(event) {
            event.preventDefault();
            const username = document.getElementById("registerUsername").value;
            const email = document.getElementById("registerEmail").value;
            const password = document.getElementById("registerPassword").value;
            try {
                const response = await fetch("http://localhost:3000/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await response.json();
                alert(data.message);
                if (response.ok) {
                    window.location.href = "/";
                }
            } catch (error) {
                console.error("Fetch Error:", error);
                alert("Something went wrong. Check console for details.");
            }
        });
    }
});