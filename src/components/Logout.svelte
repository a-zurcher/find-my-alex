<script>
import Button from "./Button.svelte";

    function logout() {
		localStorage.removeItem("authToken");
        location.reload();
	}
</script>

<Button
    buttonText="Logout"
    buttonAction={logout}/>