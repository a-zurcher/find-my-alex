<svelte:head>
	<title>find my Alex</title>
</svelte:head>

<script lang='ts'>
	import L from 'leaflet';
	import 'leaflet/dist/leaflet.css';
	import Login from './Login.svelte';
	import { authToken } from './stores';

	//let apiServer: string = "http://localhost:8000";
	let apiServer: string = "https://api.zurcher.digital";

	export let apiQuery: string;
	export let markerColor: string;

    let markerLocations = [];
	let lastLocation;
	let lastLocationCircle;
    let map;
	let initFinished: boolean = false;
    let error: any;

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
            <path d="M0 0 L50 100 L100 0 Z" fill="` + markerColor + `"></path>
			</svg>`,
            className: "",
            iconSize: [24, 40],
            iconAnchor: [12, 40],
    });

	
	// obtient les coordonnées depuis FastAPI
	async function init() {
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
			const res = await fetch(apiServer + '/' + apiQuery, {
				method: "GET",
				headers: {"Authorization": "Bearer " + $authToken},
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

			markerLocations.sort

		} catch (e) {
			error = e
		}
		initFinished = true;
	};
    
	// créer une nouvelle carte
	function createMap(container) {
		let m = L.map(container).setView(lastLocation, 10);
		
		L.tileLayer(
			'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
			{
				attribution: `&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions" target="_blank">CARTO</a>`,
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
		await init();

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
</script>

{#if initFinished && error != undefined}
	<div id="buttons">
		<button on:click={flyToLastCoordinates}>Show last known {apiQuery}</button>
	</div>

	<div id="map" style="flex-grow:1; width=100%;" use:mapAction/>
{:else}
	<div class="login">
		<Login/>
	</div>
{/if}


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

	div.login {
		position: absolute;
		left: 0; right: 0; top: 50%;
		transform: translateY(-50%);
		margin-inline: auto;
		width: clamp(23rem, 23rem, 100%);
		z-index: 100;
	}
</style>