// static/js/visualize.js
$(document).ready(function() {
    // Chart instances
    let progressTrendChart, timeDistributionChart, skillRadarChart, vocabGrowthChart;

    // WebSocket connection
    const socket = io();
    console.log('Socket initialized:', socket);
        socket.on('connect', function() {
        console.log('Connected to WebSocket.');
    });

    socket.on('disconnect', function() {
        console.log('Disconnected from WebSocket.');
    });

    socket.on('new_data', function(msg) {
        console.log('Received new_data message:', msg);
        if (msg.user_id === current_user_id) {
            console.log('User ID matches, fetching data.');
            fetchData($('.time-selector .time-button.active').data('days'));
        } else {
            console.log('User ID does not match.');
        }
    });
    // Fetch data and render charts
    function fetchData(days) {
        $('.chart-wrapper').addClass('loading');
        $.ajax({
            url: '/api/visualization_data',
            data: { days: days },
            success: function(response) {
                renderCharts(response);
                updateInsights(response); // Pass the entire response
                $('.chart-wrapper').removeClass('loading');
            },
            error: function() {
                alert('Error loading data');
                $('.chart-wrapper').removeClass('loading');
            }
        });
    }

    // Render all charts
    function renderCharts(data) {
        // Progress Trend Chart (Line)
        if (!data.skill_trends || !data.skill_trends.length) {
            $('#progressTrendChart').replaceWith('<p>No data available</p>');
        } else {
            if (progressTrendChart) progressTrendChart.destroy();
            progressTrendChart = new Chart(document.getElementById('progressTrendChart'), {
                type: 'line',
                data: {
                    labels: data.skill_trends.map(item => item.date),
                    datasets: [
                        { label: 'Listening', data: data.skill_trends.map(item => item.listening), borderColor: '#0040ff', fill: false },
                        { label: 'Reading', data: data.skill_trends.map(item => item.reading), borderColor: '#00cc00', fill: false },
                        { label: 'Speaking', data: data.skill_trends.map(item => item.speaking), borderColor: '#ff3300', fill: false },
                        { label: 'Writing', data: data.skill_trends.map(item => item.writing), borderColor: '#9900cc', fill: false }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }
            });
        }

        // Time Distribution Chart (Pie)
        if (!data.distribution_data || !Object.values(data.distribution_data).some(item => item.hours > 0)) {
            $('#timeDistributionChart').replaceWith('<p>No data available</p>');
        } else {
            if (timeDistributionChart) timeDistributionChart.destroy();
            timeDistributionChart = new Chart(document.getElementById('timeDistributionChart'), {
                type: 'pie',
                data: {
                    labels: Object.keys(data.distribution_data),
                    datasets: [{
                        data: Object.values(data.distribution_data).map(item => item.hours),
                        backgroundColor: ['#0040ff', '#00cc00', '#ff3300', '#9900cc', '#ffcc00']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Skill Radar Chart
        if (!data.radar_data || !Object.values(data.radar_data).some(value => value > 0)) {
            $('#skillRadarChart').replaceWith('<p>No data available</p>');
        } else {
            if (skillRadarChart) skillRadarChart.destroy();
            skillRadarChart = new Chart(document.getElementById('skillRadarChart'), {
                type: 'radar',
                data: {
                    labels: ['Listening', 'Reading', 'Speaking', 'Writing', 'Vocabulary'],
                    datasets: [{
                        label: 'Skills',
                        data: [
                            data.radar_data.listening,
                            data.radar_data.reading,
                            data.radar_data.speaking,
                            data.radar_data.writing,
                            data.radar_data.vocabulary
                        ],
                        backgroundColor: 'rgba(0, 64, 255, 0.2)',
                        borderColor: '#0040ff'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { r: { beginAtZero: true, max: 100 } } }
            });
        }

        // Vocabulary Growth Chart (Area)
        if (!data.vocab_data || !data.vocab_data.length) {
            $('#vocabGrowthChart').replaceWith('<p>No data available</p>');
        } else {
            if (vocabGrowthChart) vocabGrowthChart.destroy();
            vocabGrowthChart = new Chart(document.getElementById('vocabGrowthChart'), {
                type: 'line',
                data: {
                    labels: data.vocab_data.map(item => item.date),
                    datasets: [
                        { label: 'Active Vocabulary', data: data.vocab_data.map(item => item.active), backgroundColor: 'rgba(0, 64, 255, 0.2)', borderColor: '#0040ff', fill: true },
                        { label: 'Passive Vocabulary', data: data.vocab_data.map(item => item.passive), backgroundColor: 'rgba(0, 204, 0, 0.2)', borderColor: '#00cc00', fill: true }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            });
        }
    }

    // Update insights
    function updateInsights(data) {
        const insights = data.insights;
        $('#growth').text(insights.growth);
        $('#mostImproved').text(insights.most_improved);
        $('#leastImproved').text(insights.least_improved);
        $('#currentLevel').text(insights.current_level);

        $('#strongestScore').text(insights.strongest_score);
        $('#weakestScore').text(insights.weakest_score);

        // Dynamically set strongest and weakest skills
        let strongestSkill = '';
        let weakestSkill = '';
        let maxScore = -1;
        let minScore = 101;
        const radarData = data.radar_data;
        for (const skill in radarData) {
            if (radarData.hasOwnProperty(skill) && skill !== 'vocabulary') {
                if (radarData[skill] > maxScore) {
                    maxScore = radarData[skill];
                    strongestSkill = skill.charAt(0).toUpperCase() + skill.slice(1);
                }
                if (radarData[skill] < minScore) {
                    minScore = radarData[skill];
                    weakestSkill = skill.charAt(0).toUpperCase() + skill.slice(1);
                }
            }
        }
        $('#strongestSkill').text(strongestSkill);
        $('#weakestSkill').text(weakestSkill);

        $('#listeningGrowth').text(insights.listening_growth);
        $('#activeVocab').text(insights.active_vocab);
        $('#activeVocabGrowth').text(insights.active_vocab_growth);
        $('#passiveVocab').text(insights.passive_vocab);
        $('#passiveVocabGrowth').text(insights.passive_vocab_growth);
        $('#vocabLevel').text(insights.vocab_level);

        // Update distribution details
        const distributionData = data.distribution_data;
        for (const skill in distributionData) {
            if (distributionData.hasOwnProperty(skill)) {
                $(`#${skill}Hours`).text(distributionData[skill].hours);
                $(`#${skill}Percent`).text(distributionData[skill].percentage);
            }
        }
    }

    // Time selector event
    $('.time-selector .time-button').click(function() {
        $('.time-selector .time-button').removeClass('active');
        $(this).addClass('active');
        let days = $(this).data('days');
        fetchData(days);
    });

    // Initial load
    fetchData(7);

});