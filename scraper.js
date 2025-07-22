/**
 * Vaktija.dev Scraper for Node.js
 *
 * This script fetches the prayer times data from vaktija.dev by making an
 * HTTP request and then parsing the HTML response to extract the
 * necessary data object. It sends a cookie to specify the desired city.
 *
 * How to Run:
 * 1. Make sure you have Node.js installed on your system.
 * 2. Save this code as a file (e.g., `scraper.js`).
 * 3. Run the script from your terminal using the command: `node scraper.js`
 *
 * Dependencies:
 * This script uses the built-in `fetch` API available in modern Node.js versions
 * (v18+). No external libraries are needed.
 */

// The main function that orchestrates the scraping process.
async function fetchVaktijaData() {
  const url = 'https://vaktija.dev/';
  console.log(`Fetching data from ${url} for Novi Pazar...`);

  try {
    // 1. Fetch the HTML content of the page, sending the city cookie.
    const response = await fetch(url, {
      headers: {
        'Cookie': 'city=Novi%20Pazar'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const html = await response.text();

    // 2. Parse the HTML to find the data.
    // We use a specific regular expression to find the 'wire:initial-data'
    // attribute that belongs to the 'public.daily-times' component, which
    // contains the prayer times.
    const regex = /wire:initial-data="([^"]*public\.daily-times[^"]*)"/;
    const match = html.match(regex);

    if (!match || !match[1]) {
      throw new Error('Could not find the prayer times data attribute in the HTML response.');
    }

    // The captured JSON string needs to have HTML entities like '&quot;' decoded.
    const encodedJsonString = match[1];
    const decodedJsonString = encodedJsonString.replace(/&quot;/g, '"');

    // 3. Parse the JSON string to get the raw data object.
    const rawData = JSON.parse(decodedJsonString);
    const prayerData = rawData.serverMemo.data;

    // 4. Structure the extracted data into a clean, readable object.
    const vaktija = {
      location: {
        city: prayerData.city_name,
        country: prayerData.country_name,
        latitude: prayerData.latitude,
        longitude: prayerData.longitude,
      },
      date: {
        gregorian: prayerData.current_date,
        dayOfWeek: prayerData.day_week,
      },
      prayerTimes: {
        fajr: prayerData.zora,       // Zora
        sunrise: prayerData.izlazak, // Izlazak sunca
        dhuhr: prayerData.podne,     // Podne
        asr: prayerData.ikindija,    // Ikindija
        maghrib: prayerData.aksam,   // Akšam
        isha: prayerData.jacija,     // Jacija
      },
      otherTimes: {
        midnight: prayerData.pola_n,  // Polovina noći
        lastThird: prayerData.zadnja, // Zadnja trećina
      },
      countdown: {
        nextPrayerName: prayerData.naredni,
        nextPrayerTime: prayerData.naredni_value,
        currentTime: prayerData.trenutni,
        currentTimeValue: prayerData.trenutni_value,
      }
    };

    return vaktija;

  } catch (error) {
    console.error('An error occurred during the scraping process:', error);
    return null;
  }
}

// Execute the main function and log the result to the console.
(async () => {
  const data = await fetchVaktijaData();
  if (data) {
    console.log('Successfully scraped data:');
    console.log(JSON.stringify(data, null, 2)); // Pretty-print the JSON object
  } else {
    console.log('Failed to scrape data.');
  }
})();

