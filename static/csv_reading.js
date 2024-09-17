document.addEventListener("DOMContentLoaded", function() {
    const csvInput = document.getElementById("csv_input_file");
    var csv_name ='';
    if (csvInput) {
        csvInput.addEventListener('keypress', function(event) {
            if (event.key === "Enter") {
                event.preventDefault(); // Prevent default form submission or other actions
                handleUrlInput(); // Call the function to handle the input
                csvInput.value = '';
            }
        });
    }

    function handleUrlInput() {
        csv_name = getFileName(csvInput.value);
        const url = csvInput.value.trim();

        if (url) {
            // Validate URL (you can use a more sophisticated validation if needed)
            if (isValidUrl(url)) {
                fetchFile(url);
            } else {
                console.error("Invalid URL format.");
            }
        } else {
            console.log("No URL entered.");
        }
    }

    function isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch (error) {
            return false;
        }
    }

    function fetchFile(url) {
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.blob();
            })
            .then(blob => {
                const formData = new FormData();
                formData.append('file', blob, csv_name);
                formData.append('csv_url', url);

                return fetch('http://localhost:5000/upload', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Accept': 'application/json'
                    }
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.message) {
                    console.log(data.message);
                    displayResult(data.filename); // Assume `data.filename` is the result filename
                } else if (data.error) {
                    console.error(data.error);
                }
            })
            .catch(error => {
                console.error(error);
            });
    }
   function getFileName(url) {
        if (url.includes('year')) {
            return "data_year.csv";
        } else if (url.includes('month')) {
            return "data_month.csv";
        } else if (url.includes('daily')) {
            return "data_daily.csv";
        } else {
            return "data.csv";
        }
    }
    function displayResult(filename) {
        const suffix = filename.split('_').pop();
        var elementID = '';
        var forecastID = ''


        if (suffix === "year"){
            elementID ="year_chart";
            forecastID ="year_forecast_chart";
        }
        else if (suffix === "month"){
            elementID ="month_chart";
            forecastID ="month_forecast_chart";
        }
        else if (suffix === 'daily')
        {
            elementID ="daily_chart";
            forecastID ="daily_forecast_chart";
        }

        console.log("CUrrent suffix: ", suffix);
        const forecastElement = document.getElementById(forecastID);
        const chartElement = document.getElementById(elementID);

       if (chartElement) {
            const imageUrl = `static/plots/${filename}.png`;
            const image = document.createElement("img");
            image.src = imageUrl;
            image.alt = 'Trend Plot';


            image.style.width = '100%';
            image.style.height = '100%';

            chartElement.innerHTML = '';
            chartElement.appendChild(image);
        }
       if (forecastElement) {
           const image_Url = `static/plots/${forecastID}.png`;
           const img = document.createElement("img");
           img.src = image_Url;
           img.alt = 'Trend Plot';


           img.style.width = '100%';
           img.style.height = '100%';

           forecastElement.innerHTML = '';
           forecastElement.appendChild(img);
        }
    }
});
