document.addEventListener('DOMContentLoaded', () => {
    const scoreTableBody = document.querySelector('#scoreTable tbody');
    const averagesDiv = document.querySelector('#averages');

    // Fetch scores.json
    fetch('./game-data.json')
        .then(response => response.json())
        .then(data => {
            calculateAndDisplayAverages(data);
        })
        .catch(error => console.error('Error fetching data:', error));

    // Calculate and display averages for the last 10 games
    function calculateAndDisplayAverages(data) {
        const playerAverages = [];

        Object.entries(data).forEach(([player, matches]) => {
            // Get last 10 matches (or fewer if not enough games played)
            const last10Games = matches.slice(10);

            // Calculate average placement
            const totalPlacement = last10Games.reduce((acc, match) => acc + match.placement, 0);
            const avgPlacement = (totalPlacement / last10Games.length).toFixed(2);

            // Calculate most used trait
            const traitCounter = {};
            last10Games.forEach(match => {
                const trait = match.most_used_trait;
                if (trait) {
                    traitCounter[trait] = (traitCounter[trait] || 0) + 1;
                }
            });

            // Find the most used trait(s)
            const maxCount = Math.max(...Object.values(traitCounter));
            const favoriteTraits = Object.keys(traitCounter).filter(trait => traitCounter[trait] === maxCount);

            // Calculate number of games played today
            const today = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
            const gamesToday = last10Games.filter(match => match.timestamp.startsWith(today)).length;

            playerAverages.push({
                player,
                average: avgPlacement,
                favoriteTrait: favoriteTraits.join(', '),
                gamesToday: gamesToday,
            });
        });

        // Sort players by average (ascending)
        playerAverages.sort((a, b) => a.average - b.average);

        // Display averages
        scoreTableBody.innerHTML = '';  // Clear previous rows
        playerAverages.forEach(entry => {
            const row = `<tr>
                <td>${entry.player}</td>
                <td>${entry.average}</td>
                <td>${entry.favoriteTrait}</td>
                <td>${entry.gamesToday} game(s) idag</td>
            </tr>`;
            scoreTableBody.innerHTML += row;
        });
    }
});
