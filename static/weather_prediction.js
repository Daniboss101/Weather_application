document.getElementById("submit_date_button").addEventListener('click', function(){
    const datePredict = document.getElementById("date_input").value;
    console.log("BUTTON PRESSED");
    console.log("The value sent to predict: ", datePredict);
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ date: datePredict })
    })
    .then(response => response.json())
    .then(data => {
        const predictedTemp = data.predicted_temp;
        document.getElementById("prediction_result").innerHTML = predictedTemp;

    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
