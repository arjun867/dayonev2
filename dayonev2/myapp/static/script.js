document.addEventListener('DOMContentLoaded', function() {
    let activeTimerId = null;

    let weeklyChart;
    let monthlyChart;

    // Hide all category sections except the first one
    $('.custom-categorysection').not(':first').hide();

    // Smooth scrolling for categories
    $('.custom-navlink').on('click', function(e){
        e.preventDefault();
        var target = $(this).attr('href');
        $('html, body').animate({
            scrollLeft: $(target).offset().left
        }, 500);
    });

    // Show/hide product cards based on selected category
    $('.custom-navlink').on('click', function(){
        var category = $(this).attr('href');
        $('.custom-categorysection').hide();
        $(category).show();
    });

    
    $('.purchase-form').on('submit', function(e){
        e.preventDefault();
        var form = $(this);
        $.ajax({
            url: form.attr('action'),
            type: form.attr('method'),
            data: form.serialize(),
            dataType: 'json',
            success: function(response){
                console.log(response); // Log the response to check its structure and content
                if(response.success){
                    // Update virtual currency balance
                    $('#virtualCurrency').text(response.virtual_currency_balance);
                    // Hide purchase button and show success message
                    form.find('.btn-primary').hide();
                    alert('Product purchased successfully!');
                } else {
                    alert('Failed to purchase product: ' + response.error);
                }
            },
            error: function(xhr, status, error){
                console.error('Failed to make purchase request:', error);
            }
        });
    });    

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Check if the cookie name matches the requested name
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');


    function updateVirtualCurrency() {
        $.ajax({
            url: '/convert_pomodoros_to_currency/',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(response) {
                if (response.success) {
                    // Update the virtual currency balance on the page
                    $('#virtualCurrency').text(response.virtual_currency);
                } else {
                    console.error('Failed to update virtual currency');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    }
    
    // Call the function to update virtual currency on page load or as needed
    updateVirtualCurrency();
    

    function updatePomodoroCounts() {
        $.ajax({
            url: '/get_daily_pomodoro_count/',
            type: 'GET',
            success: function(response) {
                const dailyCount = response.daily_count;
                // Update UI with daily count
                $('#dailyCount').text(dailyCount);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
        

        $.ajax({
            url: '/get_yearly_pomodoro_count/',
            type: 'GET',
            success: function(response) {
                const yearlyCounts = response.yearly_counts;
                // Clear previous counts
                $('#yearlyCounts').empty();
                // Update UI with year-wise breakdown for each year
                yearlyCounts.forEach(function(yearlyCount) {
                    const year = yearlyCount.year;
                    const count = yearlyCount.count;
                    // Update UI with year-wise count
                    $('#yearlyCounts').append(`<li>${year}: ${count}</li>`);
                });
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });

        
        $.ajax({
            url: '/get_total_pomodoro_count/',
            type: 'GET',
            success: function(response) {
                const totalCount = response.total_count;
                // Update UI with the total count of Pomodoros
                $('#totalPomodoroCount').text(totalCount);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    
    
        // Function to get month name from month number
        function getMonthName(monthNumber) {
            const months = [
                'January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December'
            ];
            return months[monthNumber - 1];
        }
    
        // Function to update weekly chart
        function updateWeeklyChart(weeklyCounts) {
            const labels = weeklyCounts.map(entry => new Date(entry.day).toLocaleDateString('en-US', { weekday: 'short' }));
            const data = weeklyCounts.map(entry => entry.count);
    
            // Check if the chart is already initialized
            if (weeklyChart) {
                // Update existing chart
                weeklyChart.data.labels = labels;
                weeklyChart.data.datasets[0].data = data;
                weeklyChart.update();
            } else {
                // Create a new chart
                const ctx = document.getElementById('weeklyChart').getContext('2d');
                weeklyChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Weekly Pomodoros',
                            data: data,
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            tooltip: {
                                enabled: false
                            },
                            legend: {
                                display: false
                            },
                            datalabels: {
                                anchor: 'end',
                                align: 'end',
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                },
                                formatter: function(value, context) {
                                    return value; // Display the Pomodoro count above each bar
                                }
                            }
                        }
                    }
                });
            }
        }
    
        // Function to update monthly chart
        function updateMonthlyChart(monthlyCounts) {
            const labels = monthlyCounts.map(entry => getMonthName(entry.month));
            const data = monthlyCounts.map(entry => entry.count);
    
            // Check if the chart is already initialized
            if (monthlyChart) {
                // Update existing chart
                monthlyChart.data.labels = labels;
                monthlyChart.data.datasets[0].data = data;
                monthlyChart.update();
            } else {
                // Create a new chart
                const ctx = document.getElementById('monthlyChart').getContext('2d');
                monthlyChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Monthly Pomodoros',
                            data: data,
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgba(255, 159, 64, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            legend: {
                                display: false  // Hide the legend
                            }
                        }
                    }
                });
            }
        }
    
        // AJAX requests to update charts
        $.ajax({
            url: '/get_weekly_pomodoro_count/',
            type: 'GET',
            success: function(response) {
                const weeklyCounts = response.weekly_counts;
                updateWeeklyChart(weeklyCounts);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    
        $.ajax({
            url: '/get_monthly_pomodoro_count/',
            type: 'GET',
            success: function(response) {
                const monthlyCounts = response.monthly_counts;
                updateMonthlyChart(monthlyCounts);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    }
    
    // Call the function to update counts when the page loads or as needed
    updatePomodoroCounts();
    
    // Add click event listener to each timer icon
    document.querySelectorAll('.custom-timer-icon').forEach(timerIcon => {
        timerIcon.addEventListener('click', function(event) {
            // Get the task ID from the data-task-id attribute
            const taskId = this.dataset.taskId;
            
            // Log the task ID to the console
            console.log('Clicked Task ID:', taskId);

            // If there is an active timer, do not start a new one
            if (activeTimerId !== null) {
                console.log('Another timer is already active');
                return;
            }

            // Display the time on the timer
            updateTimerDisplay(taskId);
        });
    });

    
    // Function to update timer display
    function updateTimerDisplay(taskId) {
        var timercards = document.querySelector(`.custom-timer-card[data-task-id="${taskId}"]`)
        var timerDisplay = document.querySelector(`.custom-timer-display[data-task-id="${taskId}"]`)
        var startbtn = document.querySelector(`.custom-start-timer[data-task-id="${taskId}"]`)
        var skipbtn = document.querySelector(`.custom-skip-timer[data-task-id="${taskId}"]`)
        var pausebtn = document.querySelector(`.custom-pause-timer[data-task-id="${taskId}"]`)

        if (timercards) {
            // Update the timer display content
            console.log('Timer card element found for Task ID:', taskId);

            // Clear any existing active timer
            clearInterval(activeTimerId);

            var intervalid;
            var totalseconds = 0.2 * 60 //time in seconds
            var currentseconds = totalseconds
            var ispomodoro = true //flag to track if its pomodoro or break timer

            if (ispomodoro) {
                skipbtn.style.display = 'none'
            }

            function startTimer() {

                intervalid = setInterval(function() {
                    if (currentseconds > 0) {
                        currentseconds--;
                        var minutes = Math.floor(currentseconds / 60)
                        var seconds = currentseconds % 60
                        var formattedtime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
                        timerDisplay.textContent = formattedtime
                    } else {
                        onTimerEnd(); // Call onTimerEnd when the timer reaches zero
                    }
                }, 1000);
                // Store the interval ID for this task
                activeTimerId = intervalid;
                
            }

            function onTimerEnd() {
                clearInterval(intervalid);
                activeTimerId = null; // Set activeTimerId to null when the timer ends

                // var csrftoken = getCookie('csrftoken');

                // ajax code
                function addPomodoro(taskId) {
                    // Get the user ID dynamically
                    $.ajax({
                        url: '/get_current_user_id/',  // URL of your Django view to get the current user ID
                        type: 'GET',
                        success: function(response) {
                            const userId = response.user_id;
                            console.log('User ID:', userId);
                            
                            // Make the AJAX request to add the Pomodoro with the dynamically obtained userId
                            var csrftoken = getCookie('csrftoken');
                
                            $.ajax({
                                url: '/add_pomodoro/',
                                type: 'POST',
                                headers: {
                                    'X-CSRFToken': csrftoken
                                },
                                data: {
                                    'taskId': taskId,
                                    'userId': userId
                                },
                                success: function(response) {
                                    console.log('New Pomodoro added with ID:', response.id);
                                },
                                error: function(xhr, status, error) {
                                    console.error('Error:', error);
                                }
                            });
                        },
                        error: function(xhr, status, error) {
                            console.error('Error:', error);
                        }
                    });
                }

                if (ispomodoro) {
                    addPomodoro(taskId);
                    setTimeout(function() {
                        updateVirtualCurrency();
                        setTimeout(function() {
                            updatePomodoroCounts();
                        }, 500);
                    }, 500);
                    console.log('Tried to update stats instantly');
                }                                
                
                // Function to get CSRF token from cookie
                function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = cookies[i].trim();
                            // Check if the cookie name matches the requested name
                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
                var csrftoken = getCookie('csrftoken');

                if (ispomodoro) {
                    // Start break timer
                    startbtn.disabled = false;
                    ispomodoro = false;
                    totalseconds = 0.1 * 60; // 10 seconds for demonstration, change to 5 * 60 for 5 minutes
                    currentseconds = totalseconds;
                    skipbtn.style.display = 'inline-block'; // Show skip button for break timer
                    timerDisplay.textContent = '00:06';
                } else {
                    // Reset pomodoro timer
                    startbtn.disabled = false;
                    ispomodoro = true;
                    totalseconds = 0.2 * 60; // 20 seconds for demonstration, change to 25 * 60 for 25 minutes
                    currentseconds = totalseconds;
                    skipbtn.style.display = 'none'; // Hide skip button for pomodoro timer
                    timerDisplay.textContent = '00:12';
                }
            }

            startbtn.addEventListener('click', function(event) {
                event.stopPropagation()

                // Start the timer
                startTimer();
                // Disable the start button
                startbtn.disabled = true;

            });

            pausebtn.addEventListener('click', function(event) {
                event.stopPropagation();
                clearInterval(intervalid);
                console.log('Timer paused for task ID:', taskId);
                activeTimerId = null; // Reset the activeTimerId
            
                // Enable the start button
                startbtn.disabled = false;
            });
            
                        
            skipbtn.addEventListener('click', function(event) {
                event.stopPropagation();
                timerDisplay.textContent = '00:12'; // Reset the timer display to initial value
            
                // Clear the active timer
                // clearInterval(activeTimerId);
                // activeTimerId = null;
            
                if (!ispomodoro) {
                    // Start the pomodoro timer only if it's not already started
                    ispomodoro = true;
                    totalseconds = 0.2 * 60; // 20 seconds for demonstration, change to 25 * 60 for 25 minutes
                    currentseconds = totalseconds;
                    skipbtn.style.display = 'none'; // Hide skip button for pomodoro timer
                    // Do not start the timer automatically here
                    
                }
            });
            
            
        } else {
            console.error('Timer card element not found for Task ID:', taskId);
        }
    }
});
