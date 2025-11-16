A simple CLI tool to export backer data from OpenCollective for ISO mailings. It might do more in the future.

# Setup
1. Ensure that you have the following packages installed:
```
python-typer
python-gql
python-rich
python-keyring
```
2. Clone this repository somewhere.
3. Acquire an Open Collective [personal token](https://documentation.opencollective.com/development/personel-tokens).
> [!Note]
> Current operations are possible using only the "account" scope. For security, don't add any others.
4. Add your token to the keyring with `./oc-export.py set-token`. The program will prompt you for your token.
5. Move on to usage!

# Usage
> [!Note]
> Most of this program's documentation lives in its built-in help. Run any subcommand with `--help` to see detailed usage.

The usual operation (getting mailing list CSVs for each backer tier) is very simple: `./oc-export.py export`.
