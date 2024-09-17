const weatherSymbols =
    {
        1: 'clear-sky',
        2: 'light-clouds',
        3: 'partly-cloudy',
        4: 'cloudy',
        6: 'rain-and-snow',
        5: 'rain',
        7: 'snow',
        8: 'showers',
        9: 'snow-shower',
        10: 'rain-and-snow',
        11: 'light-fog',
        12: 'fog',
        13: 'showers',
        14: 'thunderstorm',
        15: 'drizzle',
            16: 'sandstorm',
        101: 'night-clear',
        102: 'light-clouds-night',
        103: 'partly-cloudy-night',
        104: 'clouds-night',
        105: 'rainy-night',
        106: 'rain-and-snow',
        107: 'snow-night',
        108: 'showers-night',
        109: 'snow-shower',
        110: 'rain-and-snow',
        111: 'fog-night',
        112: 'fog-night',
        113: 'showers-night',
        114: 'thunderstorm',
        115: 'drizzle-night',
            116: 'sandstorm'

    };
export function setCurrentBackground(value)
{
    const weatherSymbol = weatherSymbols[value];

    if (weatherSymbol)
    {
            const imgURL = `/static/images/${weatherSymbol}.jpg`;
            document.getElementById('first_page').style.backgroundImage = `url(${imgURL})`;
    }

}