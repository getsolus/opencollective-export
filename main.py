import typer
from typing_extensions import Annotated
import opencollective
import keyring
from rich.console import Console
from rich.prompt import Confirm, Prompt

app = typer.Typer()
console = Console()
error_console = Console(stderr=True, style="bold red")

def __get_token():
    """
    Attempt to get an Open Collective token from the keyring; prompt the user if it isn't found.
    """
    token = keyring.get_password("opencollective-export", "token")
    if not token:
        console.print("Token not found in the system keyring. Please add one now.", style="yellow")
        set_token()
        token = keyring.get_password("opencollective-export", "token")
    return token

@app.command()
def print_backers(org: Annotated[str, typer.Argument()] = "getsolus"):
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    opencollective.get_backers(org=org, client=client)

@app.command()
def set_token(token: Annotated[str or None, typer.Option(help="Open Collective Personal Token (optional - can be specified via CLI to keep the token out of shell history)")] = None):
    """
    Adds your Open Collective token to the system keyring for future use.
    """
    if keyring.get_password("opencollective-export", "token"):
        if not Confirm.ask("Overwrite existing token? "):
            exit()
    if not token:
        token = Prompt.ask("Please enter your Open Collective Personal Token")
    try:
        keyring.set_password("opencollective-export", "token", token)
    except keyring.errors.PasswordSetError:
        error_console.print("Failed to save token: Keyring access error.")
        exit()
    if keyring.get_password("opencollective-export", "token") == token:
        console.print("Successfully saved token.", style="green")


if __name__ == '__main__':
    app()