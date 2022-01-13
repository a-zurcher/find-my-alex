<script>
	import L from 'leaflet';
	import 'leaflet/dist/leaflet.css';

	// let apiServer = "http://localhost:8000"
	let apiServer = "https://api.zurcher.digital"

    let markerLocations = [];
	let lastLocationCircle;
	var lastLocation;
    let map;
    let error = null;

    // marker - source : https://onestepcode.com/leaflet-markers-svg-icons/
	const svgIcon = L.divIcon({
        html: `
            <svg
            width="24"
            height="40"
            viewBox="0 0 100 100"
            version="1.1"
            preserveAspectRatio="none"
            xmlns="http://www.w3.org/2000/svg"
            >
            <path d="M0 0 L50 100 L100 0 Z" fill="#7A8BE7"></path>
            </svg>`,
            className: "",
            iconSize: [24, 40],
            iconAnchor: [12, 40],
    });

	
	// obtient les coordonnées depuis FastAPI
	async function loadData() {
		const parseJSON = (resp) => (resp.json ? resp.json() : resp);
		const checkStatus = (resp) => {
			if (resp.status >= 200 && resp.status < 300) {
				return resp;
			}
			return parseJSON(resp).then((resp) => {
				throw resp;
			});
		};

		try {
			const res = await fetch(apiServer + '/coordinates', {
				method: "GET",
			}).then(checkStatus)
		.then(parseJSON);
			// les coordonées ne sont pas stockées dans le même ordre pour Redis et Leaflet -> ici latitudes et longitudes sont inversées
			res.forEach(element => {
				let timestamp = element[0]
				let latitude = element[1][1]
				let longitude = element[1][0]

				let marker = [timestamp, L.latLng(latitude, longitude)]

				markerLocations.push(marker)
			});

		} catch (e) {
			error = e
		}
	};
    
	// créer une nouvelle carte
	function createMap(container) {
		let m = L.map(container).setView(lastLocation, 11);
		
		L.tileLayer(
			'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
			{
				attribution: `&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>`,
				subdomains: 'abcd',
				maxZoom: 20,
				updateWhenZooming: true,
				markerZoomAnimation: true,
			}
		).addTo(m);

		return m;
	}

	// afficher une nouvelle carte avec les markers de position
	async function mapAction(container) {
		await loadData();

		// obtient la dernière location enregistrée
		lastLocation = markerLocations[markerLocations.length - 1][1];
        
		map = createMap(container);

		markerLocations.forEach(element => {
			L.marker(element[1], { icon: svgIcon }).addTo(map);
		});

		return {
			destroy: () => {
				map.remove();
			},
		};
	}

	async function flyToLastCoordinates() {
		// vérifie si la carte a déjà un cercle
		if (map.hasLayer(lastLocationCircle)) {
			// si oui, le supprime
			lastLocationCircle.removeFrom(map);
		}

		lastLocationCircle = L.circle(lastLocation, {radius:30, opacity:0.5});

		await map.flyTo(lastLocation, 18);

		map.on('zoomend', function () {
			lastLocationCircle.addTo(map);
		});
	}

	function flyToCoordinates() {
		map.flyTo([19,-99],8)
	}
</script>


<style>
	#map {
		height: 100%;
		width: 100%;
		background:white;
	}

	#buttons button {
		color:white;
		font-weight: bold;
		background-color: var(--button-color);
		border: none;
		border-radius: 10px;
		cursor: pointer;
	}
</style>


<div id="buttons">
	<button on:click={flyToLastCoordinates}>Show last known location</button>
	<button on:click={flyToCoordinates}>Travel to Mexico City</button>
</div>

<div id="map" style="flex-grow:1; width=100%;" use:mapAction/>