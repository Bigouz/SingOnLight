async function reset_data() {

                // envoie une requête au serveur pour supprimer les données de score de la BDD
                const response = await fetch('/reset_data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                
                const data = await response.json();
                location.reload(); // recharge la page pour appliquer les modifications
            }
 

function showChart(data) {
    // affiche le graphique avec les données de la BDD en paramètre
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

async function apparition(button) {
    // affiche les GIFs dans le mode histoire
    // et système d'état de jeu. 
    let gif = document.getElementById("gifDragon");
    let src = gif.src;
    gif.src = "";
    gif.src = src; // redémarre le gif
    gif.classList.remove("hidden");
    gif.classList.add("visible");

    setTimeout(async function() {
        gif.classList.remove("visible");
        gif.classList.add("hidden");
	const response = await fetch('/run_play_histoire', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({})
                        });
    const data = await response.json();
	var niveau = data["niveau"];
	var etat=data["etat"];
	if (etat == "gagné"){ // si l'utilisateur a gagné le niveau

    	console.log(niveau);
    	document.getElementById("niveau").innerText = niveau; // change le texte du niveau
    	document.getElementById("buttonHistoire").click(); // lance le prochain niveau
	}
	if(etat == "perdu"){ // si l'utilisateur a perdu le niveau
	    let png = document.getElementById("loose")
	    png.classList.remove("hidden");
	    png.classList.add("visible");
	}
	if(etat == "fini"){ // si l'utilisateur a gagné tous les niveaux
	    let png = document.getElementById("victory")
	    png.classList.remove("hidden");
	    png.classList.add("visible");
	}
    }, 2650); // le gif est montré pendant 2.65 secondes
}

