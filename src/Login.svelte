<script lang='ts'>
    import { authToken } from "./stores";

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
            error = undefined;
        } else {
            error = parsed.detail;
        }
    };
</script>


<div class="popup">
    <p class="title"><b>Please login to display locations!</b></p>

    <form on:submit|preventDefault="{handleLogin}" method="post">
        <div class="form_input">
            <div>
                <label for="email">Email</label>
                <input type="email" bind:value="{email}"/>
            </div>

            <div>
                <label for="password">Password</label>
                <input type="password" bind:value="{password}" />
            </div>

            <button class="login" type="submit">Login</button>
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

    p.title {
        margin-top: 0;
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
        flex-wrap: wrap;
    }

    label {
        width: 6rem;
        max-width: 100%;
    }

    input {
        width: 15rem;
        max-width: 100%;
    }

    p.error {
        color: red!important;
    }

    button.login {
        width: 4.5rem;
        margin-right: 0;
        margin-left: auto;
        margin-bottom: 0;
    }
</style>