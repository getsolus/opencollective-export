import typer
from typing_extensions import Annotated
import opencollective
import keyring
from rich.console import Console
from rich.prompt import Confirm, Prompt
import pathlib
import datetime

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
def print_backers(org: Annotated[str, typer.Option()] = "getsolus"):
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    opencollective.get_active_backers(org=org, client=client)

@app.command()
def list_backers(org: Annotated[str, typer.Option()] = "getsolus", tier: Annotated[str or None, typer.Argument()] = None):
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    backers = opencollective.get_active_backers(org=org, client=client)
    if tier:
        backers = opencollective.filter_backers(backers, tier)
        console.print(f"Found the following {len(backers)} backers for tier {tier} and organization {org}:", style="bold")
    else:
        console.print(f"Found the following {len(backers)} backers for all tiers on organization {org}:", style="bold")
    for backer in backers:
        console.print(backer["name"])

@app.command()
def list_tiers(org: Annotated[str, typer.Option()] = "getsolus"):
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    tiers = opencollective.get_tiers(org=org, client=client)
    console.print(f"The following tiers are available for the organization {org}:", style="bold")
    for tier in tiers:
        console.print(tier)

@app.command()
def export(
        org: Annotated[str, typer.Argument()] = "getsolus",
        tier: Annotated[str or None, typer.Option("--tier", "-t")] = None,
        filename: Annotated[pathlib.Path, typer.Argument()] = f"./solus-backers{datetime.datetime.now().strftime("%m-%d-%Y")}.csv"
):
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    all_backers = opencollective.get_active_backers(client=client)





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