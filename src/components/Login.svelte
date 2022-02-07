<script lang='ts'>
    import Button from "./Button.svelte";
import { authToken } from "../stores";

    let email: string;
    let password: string;
    export let error: any = undefined;

    const handleLogin = async () => {
        const response = await fetch("https://api.zurcher.digital/user/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
            body: JSON.stringify({email, password}),
        });

        const parsed = await response.json();

        if (parsed.access_token) {
            $authToken = parsed.access_token;
            location.reload();
        } else {
            error = parsed.detail;
        }
    };
</script>


<div class="popup">
    <form on:submit|preventDefault="{handleLogin}" method="post">
        <div class="form_input">
            <div>
                <label for="email">Email</label>
                <input type="email" bind:value="{email}" required/>
            </div>

            <div>
                <label for="password">Password</label>
                <input type="password" bind:value="{password}" required/>
            </div>

            <Button buttonType="submit" buttonText="Login"/>
        </div>
        
    </form>

    {#if error}
    <p class="error"><b>{error}</b></p>
    {/if}
</div>


<style>
    div.popup {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        max-width: 32rem;
    }

    div.form_input {
        display: flex;
        flex-direction: column;
        max-width: 100%;
    }

    div.form_input div {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        flex-wrap: nowrap;
        align-items: baseline;
    }

    label {
        width: 6rem;
        max-width: 100%;
        flex-shrink: 0;
    }

    input {
        width: 100%;
    }

    p.error {
        color: red!important;
    }
</style>