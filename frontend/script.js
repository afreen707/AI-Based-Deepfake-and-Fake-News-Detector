const form = document.getElementById('analyzeForm');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    
    // Show loading state
    const resultsDiv = document.getElementById('results');
    resultsDiv.style.display = 'block';
    document.getElementById('credibility').innerText = 'Analyzing...';
    document.getElementById('textScore').innerText = '...';
    document.getElementById('phrases').innerText = '...';
    document.getElementById('mediaScore').innerText = '...';
    document.getElementById('verdict').innerHTML = '⏳ Analyzing...';
    document.getElementById('verdict').style.backgroundColor = '#9E9E9E';
    document.getElementById('verdict').style.color = 'white';

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data);

        // Display scores
        document.getElementById('credibility').innerText = data.credibility_score || 'N/A';
        document.getElementById('textScore').innerText = data.text_score || 'N/A';
        document.getElementById('phrases').innerText = 
            data.suspicious_phrases && data.suspicious_phrases.length > 0 
                ? data.suspicious_phrases.join(', ') 
                : 'None detected';
        document.getElementById('mediaScore').innerText = data.media_score || 'N/A';

        // Determine verdict based on credibility score
        const score = data.credibility_score;
        const verdictDiv = document.getElementById('verdict');
        const explanationDiv = document.getElementById('explanation');
        
        if (score >= 80) {
            verdictDiv.innerHTML = '✅ LIKELY AUTHENTIC';
            verdictDiv.style.backgroundColor = '#4CAF50';
            verdictDiv.style.color = 'white';
            explanationDiv.innerHTML = '<strong>Assessment:</strong> This content shows high credibility. Few or no suspicious patterns were detected. However, always verify important claims with multiple reliable sources.';
        } else if (score >= 60) {
            verdictDiv.innerHTML = '⚠️ QUESTIONABLE';
            verdictDiv.style.backgroundColor = '#FF9800';
            verdictDiv.style.color = 'white';
            explanationDiv.innerHTML = '<strong>Assessment:</strong> This content shows moderate credibility concerns. Some suspicious patterns were detected. Verify claims with trusted sources before sharing.';
        } else if (score >= 40) {
            verdictDiv.innerHTML = '❌ LIKELY MISLEADING';
            verdictDiv.style.backgroundColor = '#F44336';
            verdictDiv.style.color = 'white';
            explanationDiv.innerHTML = '<strong>Assessment:</strong> This content shows significant credibility issues. Multiple suspicious patterns detected. Exercise caution and fact-check thoroughly.';
        } else {
            verdictDiv.innerHTML = '🚫 HIGHLY SUSPICIOUS';
            verdictDiv.style.backgroundColor = '#C62828';
            verdictDiv.style.color = 'white';
            explanationDiv.innerHTML = '<strong>Assessment:</strong> This content shows very low credibility with numerous red flags including clickbait, conspiracy theories, or misinformation patterns. Do not share without thorough verification.';
        }

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('verdict').innerHTML = '❌ ERROR';
        document.getElementById('verdict').style.backgroundColor = '#757575';
        document.getElementById('verdict').style.color = 'white';
        document.getElementById('explanation').innerHTML = '<strong>Error:</strong> Analysis failed. Please try again.';
        alert('Analysis failed! Check console for details.');
    }
});