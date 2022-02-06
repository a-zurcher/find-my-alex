import { writable } from "svelte/store";

// get token from localStorage
export const authToken = writable(localStorage.getItem("authToken"));

// saves token to localStorage
authToken.subscribe(value => localStorage.setItem("authToken", value));