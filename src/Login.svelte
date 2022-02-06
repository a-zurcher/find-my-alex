<script lang='ts'>
    import { authToken } from "./stores";

    let email: string = "alexandre@zurcher.digital";
    let password: string = "bestpassword";
    let error;

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
        } else {
            error = parsed.detail;
        }
    };
</script>


<div class="popup">
    <p class="title"><b>Please login to display locations!</b></p>

    <form on:submit|preventDefault="{handleLogin}" method="post">
        <div>
            <div>
                <label for="email">Email</label>
                <input type="email" bind:value="{email}"/>
            </div>

            <div>
                <label for="password">Password</label>
                <input type="password" bind:value="{password}" />
            </div>
        </div>
        
        <button type="submit">Login</button>
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
    }

    p.title {
        margin-top: 0;
    }

    form div {
        display: flex;
    }

    p.error {
        color: red!important;
    }

    button {
        justify-self: flex-end;
    }
</style>