async function sendPrompt() {
    const promptInput = document.getElementById("prompt-input").value;

    // Kirim request ke endpoint Flask
    const response = await fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: promptInput }),
    });

    // Tampilkan hasil ke halaman
    const result = await response.json();
    const outputDiv = document.getElementById("output");

    if (result.error) {
        outputDiv.textContent = `Error: ${result.error}`;
    } else {
        outputDiv.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
    }
}