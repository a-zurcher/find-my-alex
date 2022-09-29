<script lang='ts'>
    export let buttonAction = undefined;
    export let buttonType: string = "submit";
    export let buttonText: string;
</script>

<button
    type={buttonType}
    on:click={buttonAction}>
        {buttonText}
</button>

<style>
    button {
        color:white;
        font-weight: bold;
        background-color: var(--button-color);
        border: none;
        border-radius: 10px;
        cursor: pointer;
    }
</style>