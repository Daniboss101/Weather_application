import{setCurrentBackground} from "./background.js";
export const appState = {
    currentUTCTime: '',
    weatherData: null,
    UTCOffset: 0,
    dayDifference:0
};

document.addEventListener('DOMContentLoaded', function() {
    displayCurrentTimeAndTemperature();
    setDayOfWeek();
    setInterval(displayCurrentTimeAndTemperature, 10000);

    try {
        const locationSearchbar = document.getElementById('locationSearchbar');
        if (locationSearchbar) {
            locationSearchbar.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    const address = locationSearchbar.value;
                    locationSearchbar.value = '';
                    changeLocation(address);
                    updateLocationTitle(address);
                }
            });
        } else {
            console.error('Element with ID "locationSearchbar" not found.');
        }

        const selectDayOfWeek = document.getElementById('selectDayOfWeek');
        if (selectDayOfWeek) {
            selectDayOfWeek.addEventListener('change', function(event) {
                const selectedDayOfWeek = parseInt(event.target.value, 10);
                updateCurrentDayOfWeek(selectedDayOfWeek);
            });
        }
    } catch (error) {
        console.error('Error initializing event listeners or initial display setup:', error);
    }
});

export function setDayOfWeek() {
    const utcDate = getUTCTime(0);
    const localDate = convertToLocalTime(utcDate);

    const selectedDayOfWeek = document.getElementById('selectDayOfWeek');

    const localDayOfWeek = localDate.getDay();

    if (selectedDayOfWeek) {
        selectedDayOfWeek.value = (localDayOfWeek === 0) ? 7 : localDayOfWeek;
    } else {
        console.error('Element with ID "selectDayOfWeek" not found.');
    }
}
export async function changeLocation(address) {
    try {
        const response = await fetch(`/get_location?address=${encodeURIComponent(address)}`);
        if (response.ok) {
            const data = await response.json();
            const { weather_data, local_time, utc_offset, lat, lon } = data;

            document.getElementById('myDiv').dataset.weather = JSON.stringify(weather_data);

            const localTime = new Date(local_time);

            const formattedTime = localTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const formattedDate = localTime.toLocaleDateString([], { month: '2-digit', day: '2-digit' });



            appState.UTCOffset = utc_offset || 0;  // Set default to 0 if undefined

            const utcTime = new Date(localTime.getTime() - (utc_offset * 1000));

            appState.currentUTCTime = utcTime;

            appState.weatherData = weather_data;


            document.getElementById('current_time').innerHTML = `<p>${formattedTime}</p>`;
            document.getElementById('current_date').innerHTML = `<p>${formattedDate}</p>`;

            displayCurrentTimeAndTemperature();
            displayTimeAndTempOfThatDay();
            setDayOfWeek();
        } else {
            console.error('Failed to fetch location');
        }
    } catch (error) {
        console.error("Could not fetch location", error);
    }
}

export function updateLocationTitle(location) {
    try {
        const titleElement = document.getElementById('locationHeader');
        if (titleElement) {
            titleElement.textContent = location.toUpperCase();
        } else {
            console.error('Element with ID "locationHeader" not found.');
        }
    } catch (error) {
        console.error('Error initializing location', error);
    }
}

export function updateCurrentDayOfWeek(selectedDayOfWeek) {
    try {
        const currentDate = getUTCTime(0); // Get current UTC time
        const currentDay = currentDate.getDay(); // Get current day of the week (0 - Sunday, 6 - Saturday)

        // Calculate day difference
        let dayDifference = selectedDayOfWeek - currentDay;
        if (dayDifference < 0) {
            dayDifference += 7; // Adjust if selected day is earlier in the week than current day
        }

        appState.dayDifference = dayDifference;

        displayCurrentTimeAndTemperature();
        displayTimeAndTempOfThatDay();
    } catch (error) {
        console.error('Error initializing current time', error);
    }
}

export function displayCurrentTimeAndTemperature() {

try {
        const weatherData = appState.weatherData || JSON.parse(document.getElementById('myDiv').dataset.weather);

        const temperatureElement = document.getElementById('temperature');
        const timeElement = document.getElementById('current_time');
        const dateElement = document.getElementById('current_date');

        const utctime = getUTCTime(appState.dayDifference);



        const localTime = new Date(utctime.getTime() + (appState.UTCOffset * 1000));
        const formattedTime = localTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const formattedDate = localTime.toLocaleDateString([], { month: '2-digit', day: '2-digit' });


        const utcHours = utctime.getHours();
        const utcDate = utctime.getDate();
        const utcMonth = utctime.getMonth();
        const utcYear = utctime.getFullYear();

       let currentWeather = null;

if (weatherData && Array.isArray(weatherData.data)) {
    // Iterate over each entry in the weather data
    weatherData.data.forEach(entry => {
        // Check if the entry has the correct parameter
        if (entry.coordinates && Array.isArray(entry.coordinates)) {
            // Iterate over each coordinate
            entry.coordinates.forEach(coord => {
                // Check if the coordinate has date entries
                if (coord.dates && Array.isArray(coord.dates)) {
                    // Find the date entry that matches the current UTC time
                    const foundWeather = coord.dates.find(dateEntry => {
                        const weatherDate = new Date(dateEntry.date);
                        return (
                            weatherDate.getUTCFullYear() === utcYear &&
                            weatherDate.getUTCMonth() === utcMonth &&
                            weatherDate.getUTCDate() === utcDate &&
                            weatherDate.getUTCHours() === utcHours
                        );
                    });

                    if (foundWeather) {
                        if (entry.parameter === "t_2m:C")
                        {
                            currentWeather = foundWeather.value;
                        }
                        if( entry.parameter === "weather_symbol_1h:idx" )
                        {
                            setCurrentBackground(foundWeather.value)
                            console.log("background: ", foundWeather.value)
                        }
                    }
                }
            });
        }
    });
}

        if (currentWeather) {
            temperatureElement.innerHTML = `<h2>${currentWeather}°C</h2>`;
        } else {
            temperatureElement.innerHTML = `<h1>${formattedDate} ${formattedTime}</h1><p>No weather data found for the current hour</p>`;
        }

        timeElement.innerHTML = `<p>${formattedTime}</p>`;
        dateElement.innerHTML = `<p>${formattedDate}</p>`;

    } catch (error) {
        console.error('Error displaying current time and temperature', error);
        const timesContainer = document.getElementById('time_temperature');
        if (timesContainer) {
            timesContainer.textContent = 'Error displaying current time and temperature';
        }
    }
}


export function displayTimeAndTempOfThatDay() {
    try {
        const weatherData = appState.weatherData || JSON.parse(document.getElementById('myDiv').dataset.weather);
        console.log(document.getElementById('myDiv').dataset.weather);

        const timeElement = document.getElementById('select_time');
        const tempElement = document.getElementById('select_temp');

        const utcDate = getUTCTime(appState.dayDifference);

        const currentYear = utcDate.getFullYear();
        const currentMonth = utcDate.getMonth() ;
        const currentDay = utcDate.getDate();


        timeElement.innerHTML = '';
        tempElement.innerHTML = '';

        var max = 0;
        var min = 100;

        if (weatherData && Array.isArray(weatherData.data)) {
            let timeTempArray = [];

            weatherData.data.forEach(entry => {
                if (entry.coordinates && Array.isArray(entry.coordinates)) {
                    entry.coordinates.forEach(coord => {
                        if (coord.dates && Array.isArray(coord.dates)) {
                            coord.dates.forEach(dateEntry => {
                                const weatherDate = new Date(dateEntry.date); // Adjusted to access date properly

                                if (
                                    weatherDate.getUTCFullYear() === currentYear &&
                                    weatherDate.getUTCMonth()  === currentMonth &&
                                    weatherDate.getUTCDate() === currentDay
                                ) {
                                    const localTime = convertToLocalTime(weatherDate);
                                    const timeString = localTime.toISOString().substring(11, 16); // "HH:MM" format
                                    if (entry.parameter === "t_2m:C") {
                                        timeTempArray.push({time: timeString, temp: dateEntry.value});
                                    }

                                    if (entry.parameter === "t_max_2m_24h:C")
                                    {
                                        max = Math.max(max, dateEntry.value);
                                        document.getElementById("current_high").innerHTML = `Hi: ${max} `;
                                    }
                                    if (entry.parameter === "t_min_2m_24h:C")
                                    {
                                        min = Math.min(min, dateEntry.value);
                                        document.getElementById("current_low").innerHTML = ` Lo: ${min}`;
                                    }
                                }
                            });
                        }
                    });
                }
            });

            // Sort the array by time
            timeTempArray.sort((a, b) => a.time.localeCompare(b.time));

            if (timeTempArray.length > 0) {
                timeTempArray.forEach(entry => {
                    timeElement.innerHTML += `<div class="cell">${entry.time}</div>`;
                    tempElement.innerHTML += `<div class="cell">${entry.temp}°C</div>`;
                });
            } else {
                timeElement.innerHTML = '<div class="cell">No weather data available</div>';
                tempElement.innerHTML = '<div class="cell">No weather data available</div>';
            }
        } else {
            timeElement.innerHTML = '<div class="cell">No weather data available</div>';
            tempElement.innerHTML = '<div class="cell">No weather data available</div>';
        }
    } catch (error) {
        console.error('Error displaying weather data for the selected day', error);
    }
}

export function convertToLocalTime(utcDate) {
    try {
        const localTime = new Date(utcDate.getTime() + (appState.UTCOffset * 1000));
        return localTime;
    } catch (error) {
        console.error('Error converting to local time', error);
    }
}
export function getUTCTime(days) {
    const currentTime = new Date();
    const offsetRightNow = currentTime.getTimezoneOffset();
    currentTime.setMinutes(currentTime.getMinutes() + offsetRightNow);
    currentTime.setDate(currentTime.getDate() + days);
    console.log(currentTime);
    return currentTime;
}
