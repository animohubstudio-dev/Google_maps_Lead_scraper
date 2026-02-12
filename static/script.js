document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scrapeForm');
    const scrapeBtn = document.getElementById('scrapeBtn');
    const loadingArea = document.getElementById('loadingArea');
    const resultsArea = document.getElementById('resultsArea');
    const errorArea = document.getElementById('errorArea');
    const downloadLink = document.getElementById('downloadLink');
    const resultMessage = document.getElementById('resultMessage');
    const totalLeads = document.getElementById('totalLeads');
    const errorMessage = document.getElementById('errorMessage');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Reset
        resultsArea.classList.add('hidden');
        errorArea.classList.add('hidden');
        loadingArea.classList.remove('hidden');
        scrapeBtn.disabled = true;
        scrapeBtn.querySelector('.btn-text').textContent = 'Processing...';
        scrapeBtn.querySelector('.spinner').classList.remove('hidden');

        // Get Form Data
        const formData = {
            city: document.getElementById('city').value,
            query: document.getElementById('query').value,
            max_leads: document.getElementById('max_leads').value
        };

        try {
            const response = await fetch('/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            loadingArea.classList.add('hidden');
            scrapeBtn.disabled = false;
            scrapeBtn.querySelector('.btn-text').textContent = 'Start Scraping';
            scrapeBtn.querySelector('.spinner').classList.add('hidden');

            if (response.ok && data.status === 'success') {
                // Success
                resultsArea.classList.remove('hidden');
                resultMessage.textContent = data.summary.message;
                totalLeads.textContent = data.summary.total_leads;
                downloadLink.href = `/download/${data.filename}`;
            } else {
                // Warning or Error from API
                errorArea.classList.remove('hidden');
                errorMessage.textContent = data.message || "An unknown error occurred.";
            }

        } catch (error) {
            console.error('Error:', error);
            loadingArea.classList.add('hidden');
            scrapeBtn.disabled = false;
            scrapeBtn.querySelector('.btn-text').textContent = 'Start Scraping';
            scrapeBtn.querySelector('.spinner').classList.add('hidden');

            errorArea.classList.remove('hidden');
            errorMessage.textContent = "Failed to connect to the server.";
        }
    });
});
