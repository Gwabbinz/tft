document.addEventListener('DOMContentLoaded', () => {
    const matchTableBody = document.querySelector('#matchTable tbody');

    // Fetch game-data.json
    fetch('./game-data.json')
        .then(response => response.json())
        .then(data => {
            displayAllMatches(data);
        })
        .catch(error => console.error('Error fetching data:', error));

    // Function to display all matches in the table
    function displayAllMatches(data) {
        matchTableBody.innerHTML = '';  // Clear table

        Object.entries(data).forEach(([player, matches]) => {
            matches.forEach(match => {
                const row = `<tr>
                    <td>${player}</td>
                    <td>${match.placement}</td>
                    <td>${match.most_used_trait}</td>
                    <td>${match.timestamp}</td>
                </tr>`;
                matchTableBody.innerHTML += row;
            });
        });
    }
});
