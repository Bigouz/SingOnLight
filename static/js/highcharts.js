async function reset_data() {

                // Send parameters via POST with JSON body
                const response = await fetch('/reset_data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });

                const data = await response.json();
                location.reload();
            }
 

function showChart(data) {

    const str = data;
    const fixed = str.replace(/'/g, '"');
    const data2 = JSON.parse(fixed);


    Highcharts.chart('container', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Scores des parties jouées'
        },
        subtitle: {
            text: ''
        },
        xAxis: {
            type: 'category',
            labels: {
                autoRotation: [-45, -90],
                style: {
                    fontSize: '13px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Parties jouées'
            }
        },
        legend: {
            enabled: false
        },
        tooltip: {
            pointFormat: 'Nombre de parties <b>{point.y:.0f}</b>'
        },
        series: [{
            name: 'Scores',
            colors: [
                '#9b20d9',  '#861ec9',  '#7010f9', 
                '#6225ed',  '#533be1',  '#4551d5', 
                '#3667c9',  '#277dbd',  '#1693b1', 
                '#03c69b',  '#00f194'
            ],
            colorByPoint: true,
            groupPadding: 0,
            data: data2,
            dataLabels: {
                enabled: true,
                rotation: -90,
                color: '#FFFFFF',
                inside: true,
                verticalAlign: 'top',
                format: '{point.y:.0f}', // one decimal
                y: 10, // 10 pixels down from the top
                style: {
                    fontSize: '13px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        }]
    });

};


function apparition(id_gif) {
    let gif = document.getElementById(id_gif);
    gif.classList.remove("hidden");
    gif.classList.add("visible");

    // Recacher le GIF après 3 secondes
    setTimeout(function() {
        gif.classList.remove("visible");
        gif.classList.add("hidden");
	}, 3000);
}




