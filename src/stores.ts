import { writable } from "svelte/store";

// DEV: deletes localStorage value
localStorage.removeItem("authToken");

// get token from localStorage
const storedAuthToken = localStorage.getItem("authToken");
export const authToken = writable(storedAuthToken);

// saves token to localStorage
authToken.subscribe(value => localStorage.setItem("authToken", value));