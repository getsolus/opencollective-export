#!/usr/bin/python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import csv

from cyclopts import App, Parameter, Group
from gql.transport.exceptions import TransportError
from typing_extensions import Annotated
from opencollective_export import opencollective
import keyring
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.text import Text
import pathlib
import datetime

app = App()
app.meta.group_parameters = Group("Global Parameters", sort_key=0)
console = Console()
error_console = Console(stderr=True, style="bold red")
global_state = {}


def __handle_exception(exception: Exception):
    """
    Handle exceptions nicely, printing to stderr, then exit.
    """
    match exception.__class__.__name__:
        case "TransportServerError":
            if exception.args[0].startswith("401"):
                error_console.print("[red]401 Unauthorized.[/red] [black]Please check the status of your Open Collective token.[/black]")
            elif exception.args[0].startswith("500"):
                error_console.print("[red]500 Internal Server Error.[/red] [black]Open Collective can't process our query. Try again later.[/black]")
            else:
                raise exception
        case "TransportQueryError":
            error_console.print(f"[red]Query Error:[/red] [black]{exception.errors[0]['message']}[/black]")
        case _:
            raise exception
    if global_state.get("debug"):
        console.print('--debug specified; re-raising the exception:')
        raise exception
    exit(1)


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


def __find_invalid_tiers(tiers, org, client) -> list[str]:
    """
    Find invalid tiers for the supplied Open Collective organization.

    Parameters
    ----------
    tiers : list[str]
        Tiers to validate.
    org: str
        Open Collective organization to query.
    client:
        Ready-to-use Open Collective client.

    Return
    ------
    list[str]
        Invalid tiers. If a tier is returned, that means it does not exist for the provided organization.
    """
    all_tiers = opencollective.get_tiers(client, org)
    return [tier for tier in tiers if tier not in all_tiers]


@app.meta.default()
def meta_run(*tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)], debug: bool = False) -> None:
    global_state["debug"] = debug
    app(tokens)


@app.command()
def list_backers(
    org: str,
    tier: list[str] or None = None,
):
    """
    Lists all current backers (backers with monthly donations) for a given Open Collective organization.

    Parameters
    ----------
    org : str
        Open Collective organization to query.
    tier : list[str] or None
        Specify one or more tiers to list. Leave empty to list backers from all tiers.
    """
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    try:
        backers = opencollective.get_active_backers(org=org, client=client)
    except TransportError as e:
        __handle_exception(e)
    if tier:
        if nonexistent_tiers := __find_invalid_tiers(tier, org, client):
            error_console.print(f'[red]Error:[/red] [black]The following tiers do not exist in the Open Collective organization {org}:[/black]')
            for tier in nonexistent_tiers:
                error_console.print(f'[black]{tier}[/black]')
            error_console.print('Note that tier names are case-sensitive.')
            exit()
        for tier in tier:
            filtered_backers = opencollective.filter_backers(backers, [tier, ])
            console.print(
                f"Found the following {len(filtered_backers)} backers for tier {tier} and organization {org}:",
                style="bold",
            )
            for backer in filtered_backers:
                console.print(backer["name"])
                if global_state.get("debug"):
                    console.print(backer)
    else:
        console.print(
            f"Found the following {len(backers)} backers for all tiers on organization {org}:",
            style="bold",
        )
        for backer in backers:
            console.print(backer["name"])
            if global_state.get("debug"):
                console.print(backer)


@app.command()
def list_tiers(org: str):
    """
    Lists all valid tiers for a given Open Collective organization.

    Parameters
    ----------
    org : str
        Open Collective organization to query.
    """
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    try:
        tiers = opencollective.get_tiers(org=org, client=client)
    except TransportError as e:
        __handle_exception(e)
    console.print(
        f"The following tiers are available for the organization {org}:", style="bold"
    )
    for tier in tiers:
        console.print(tier)


@app.command()
def export(
    org: str,
    tier: list[str] or None = None,
    base_filename: pathlib.Path = pathlib.Path(f"./backers_{datetime.datetime.now().strftime("%m-%d-%Y")}.csv"),
):
    """
    Exports Open Collective backer names and email addresses to CSV files per tier.

    Parameters
    ----------
    org : str
        Open Collective organization to query.
    tier : list[str] or None
        Specify one or more tiers to export. Leave empty to export backers from all tiers.
    base_filename : pathlib.Path
        Base filename to export to. Will have exported tier names appended before the file extension.
    """
    token = __get_token()
    client = opencollective.get_client(personal_token=token)
    if tier:
        if nonexistent_tiers := __find_invalid_tiers(tier, org, client):
            error_console.print(f'[red]Error:[/red] [black]The following tiers do not exist in the Open Collective organization {org}:[/black]')
            for tier in nonexistent_tiers:
                error_console.print(f'[black]{tier}[/black]')
            error_console.print('Note that tier names are case-sensitive.')
            exit()
        tiers = tier
    else:
        console.print("No tiers specified, using all available tiers.", style="yellow")
        tiers = opencollective.get_tiers(org=org, client=client)
    console.print("Querying OpenCollective (may take a moment)...")
    try:
        all_backers = opencollective.get_active_backers(client=client, org=org)
    except TransportError as e:
        __handle_exception(e)
    for tier in tiers:
        backers = opencollective.filter_backers(
            all_backers,
            [
                tier,
            ],
        )
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

        # If a backer does not have any email addresses, skip them for export and record their name so we can warn
        # the user.
        skipped_backers = [backer for backer in backers if not backer["account"]["emails"]]
        backers = [backer for backer in backers if backer["account"]["emails"]]

        # Sort by email address to match old "oct" behavior
        backers.sort(key=lambda b: b["account"]["emails"][:1])

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for backer in backers:
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
    token: str or None = None,
):
    """
    Adds your Open Collective token to the system keyring for future use.

    Parameters
    ----------
    token : str or None
        Open Collective Personal Token (optional - can be specified via CLI to keep the token out of shell history)
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
    app.meta()
