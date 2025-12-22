A simple CLI tool to export backer data from OpenCollective for ISO mailings. It might do more in the future.

# Setup
1. Clone this repository somewhere and `cd` into it.
2. Install this program's dependencies: `eopkg it python-keyring python-gql python-typer`
3. Acquire an Open Collective [personal token](https://documentation.opencollective.com/development/personel-tokens).
> [!Note]
> Current operations are possible using only the "account" scope. For security, don't add any others.
4. Add your token to the keyring with `python oc-export.py set-token`. The program will prompt you for your token.
5. Move on to usage!

# Usage
> [!Note]
> Most of this program's documentation lives in its built-in help. Run commands with `--help` to see detailed usage.

The usual operation (getting mailing list CSVs for each backer tier) is very simple: `python oc-export.py export`.
