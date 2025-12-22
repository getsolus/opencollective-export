#!/usr/bin/python3
import csv

import typer
from typing_extensions import Annotated
from typing import List
import opencollective
import keyring
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.text import Text
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
        console.print(
            "Token not found in the system keyring. Please add one now.", style="yellow"
        )
        set_token()
        token = keyring.get_password("opencollective-export", "token")
    return token


@app.command()
def list_backers(
    org: Annotated[str, typer.Option()] = "getsolus",
    tier: Annotated[str or None, typer.Argument()] = None,
):
    """
    Lists all current backers (backers with monthly donations) for a given Open Collective organization.
    """
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    backers = opencollective.get_active_backers(org=org, client=client)
    if tier:
        backers = opencollective.filter_backers(backers, tier)
        console.print(
            f"Found the following {len(backers)} backers for tier {tier} and organization {org}:",
            style="bold",
        )
    else:
        console.print(
            f"Found the following {len(backers)} backers for all tiers on organization {org}:",
            style="bold",
        )
    for backer in backers:
        console.print(backer["name"])


@app.command()
def list_tiers(org: Annotated[str, typer.Option()] = "getsolus"):
    """
    Lists all valid tiers for a given Open Collective organization.
    """
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    tiers = opencollective.get_tiers(org=org, client=client)
    console.print(
        f"The following tiers are available for the organization {org}:", style="bold"
    )
    for tier in tiers:
        console.print(tier)


@app.command()
def export(
    org: Annotated[str, typer.Option(help="Open Collective organization to query.")] = "getsolus",
    tier: Annotated[List[str], typer.Argument(help="Specify one or more tiers to export. Leave empty to export all tiers.")] = (),
    base_filename: Annotated[
        pathlib.Path, typer.Option(help="Base filename to export to. Will have exported tier names added.")
    ] = f"./solus-backers_{datetime.datetime.now().strftime("%m-%d-%Y")}.csv",
):
    """
    Exports Open Collective backer names and email addresses to CSV files per tier.
    """
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    console.print("Querying OpenCollective (may take a moment)...")
    all_backers = opencollective.get_active_backers(client=client, org=org)
    if tier:
        tiers = tier
    else:
        console.print("No tiers specified, using all available tiers.", style="yellow")
        tiers = opencollective.get_tiers(org=org, client=client)
    for tier in tiers:
        backers = opencollective.filter_backers(
            all_backers,
            [
                tier,
            ],
        )
        backers.sort(key=lambda b: b["account"]["emails"][:1])
        filename = (
            base_filename.parent / f"{base_filename.stem}-{tier.replace(' ', '_')}.csv"
        ).with_suffix(".csv")
        if filename.exists() and not Confirm.ask(
            Text.assemble(
                ("Warning:", "bold yellow"),
                f' Output file "{filename}" aready exists. Overwrite it?',
            )
        ):
            exit()
        skipped_backers = []
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for backer in backers:
                if len(backer["account"]["emails"]) < 1:
                    skipped_backers.append(backer)
                else:
                    writer.writerow([backer["name"], backer["account"]["emails"][-1]])
        console.print(f"Successfully exported {len(backers)} backers to {filename}.")
        if skipped_backers:
            console.print(
                f"The following {len(skipped_backers)} backers were skipped; they lack email addresses:"
            )
            for backer in skipped_backers:
                console.print(backer["name"])


@app.command()
def set_token(
    token: Annotated[
        str or None,
        typer.Option(
            help="Open Collective Personal Token (optional - can be specified via CLI to keep the token out of shell history)"
        ),
    ] = None,
):
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


if __name__ == "__main__":
    app()
