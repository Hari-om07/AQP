// Handle the response from the server
function handleResponse(response) {
    // Display result or error message
    if (response['error']) {
        document.getElementById('result').innerText = 'Error: ' + response['error'];
    } else {
        document.getElementById('result').innerText = 'Air Quality Index: ' + response['Air Quality Index'];
    }
}

// Handle the form submission
function handleSubmit(event) {
    event.preventDefault();

    var form = document.getElementById('predictionForm');
    var formData = new FormData(form);

    fetch('/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => handleResponse(data))
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerText = 'Error: Could not process request.';
    });
}
