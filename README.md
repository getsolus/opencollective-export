A simple CLI tool to export backer data from Open Collective. Current list of features:
- List available backer tiers for a given organization.
- List backers for a given organization.
- Export mailing-list-ready CSV files per backer tier.
# Setup
1. Clone this repository somewhere and `cd` into it.
2. Install this program's dependencies: `eopkg it python-keyring python-gql python-typer`
3. Acquire an Open Collective [personal token](https://documentation.opencollective.com/development/personel-tokens).
> [!Note]
> Current operations are possible using only the "account" scope. For security, don't add any others.
4. Add your token to the keyring with `./oc-export.py set-token`. The program will prompt you for your token.
5. Move on to usage!

# Usage
> [!Note]
> Most of this program's documentation lives in its built-in help. Run commands with `--help` to see detailed usage.

The usual operation (getting mailing list CSVs for each backer tier) is very simple: `./oc-export.py export <org>`.
