// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Fetch call for AI suggestion prompt
function fetchAISuggestions() {
    const prompt = document.getElementById("prompt").value;
    const userKey = document.getElementById("user-api-key").value;
    const resultContainer = document.getElementById("ai-result");

    resultContainer.textContent = "Loading suggestions...";

    fetch("/ai/suggest/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            prompt: prompt,
            api_key: userKey
        })
    })
    .then(async response => {
        const content = await response.text();
        if (!response.ok) throw new Error(`Status ${response.status}: ${content}`);
        return JSON.parse(content);
    })
    .then(data => {
        resultContainer.textContent = data.bullets || data.error || "No result.";
    })
    .catch(error => {
        resultContainer.textContent = "Failed to fetch suggestions: " + error.message;
    });
}