<svelte:head>
	<title>find my Alex</title>
</svelte:head>

<script lang="ts">
	import Router from "svelte-spa-router";
	import Sources from "./routes/Sources.svelte";
	import Locations from "./routes/Locations.svelte";
	import Poop from "./routes/Poop.svelte";
	import Login from "./components/Login.svelte";
	import Logout from "./components/Logout.svelte";
	import { authentificated } from "./stores";

	let routes = {
		"/": Locations,
		"/poop": Poop,
		"/sources": Sources,
		"/login": Login
	}
</script>

<div class="container">
	<nav>
		<h1>find my Alex</h1>

		<div class="links">
			<a href="/#/"><span role="img" aria-label="globe">🌍</span></a>
			<a href="/#/Poop"><span role="img" aria-label="poop">💩</span></a>
			<a href="/#/Sources">Sources</a>
		</div>

		{#if $authentificated}
		<div class="logout">
			<Logout/>
		</div>
		{/if}
	</nav>

	<main>
		<Router {routes}/>
	</main>
</div>


<style>
	:global(:root) {
		--text-color: #140176;
		--link-color: #3f62ec;
		--button-color: #007eff;
		--max-width: 86rem;
	}

	:global(html) {
		background: linear-gradient(166deg, #8fd3f3 0%, #d683d7 100%);
	}

	:global(p) {
		color: var(--text-color)!important;
	}

	:global(a) {
		color: var(--link-color)!important;
	}

	div.container {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	nav {
		display: flex;
		flex-direction: row;
		align-items: baseline;
		flex-wrap: wrap;
		gap: 1rem;

		max-width: var(--max-width);
		width: 100%;
		left: 0; right: 0; margin-inline: auto;
	}

	nav h1 {
		color: var(--text-color);
	}

	nav div.links a {
		color: var(--link-color);
		color:white;
		font-weight: bold;
		background-color: white;
		border: none;
		border-radius: 10px;
		cursor: pointer;
		text-decoration:none!important;
		padding: 3px;
	}

	nav div.logout {
		margin-right: 0;
		margin-left: auto;
	}

	main {
		display: flex;
		flex-flow: column;
		flex-grow: 1;
	}
</style>
