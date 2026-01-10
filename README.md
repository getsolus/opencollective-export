# opencollective-export
A simple CLI tool to export backer data from Open Collective. Current list of features:
- List available backer tiers for a given organization.
- List backers for a given organization.
- Export mailing-list-ready CSV files per backer tier.

## Development Setup
1. Clone this repository somewhere and `cd` into it.
2. Create a virtual environment: `python3 -m venv .venv`.
3. Activate your virtual environment: `source .venv/bin/activate`.
4. Install the project locally: `pip install -e .`. This will install an editable copy, so you can hack without having to reinstall all the time!

## Usage
Most of this program's documentation lives in its built-in help. Run commands with `--help` to see detailed usage. Here are a few brief examples:

> [!Note]
> All operations require the use of an Open Collective [personal token](https://documentation.opencollective.com/development/personel-tokens). Please create one before continuing
> Current operations are possible using only the "account" scope. For security, don't add any others. 

Once you have your token, add it to the system keyring with `oc-export set-token`.

The usual operation (getting mailing list CSVs for each backer tier) is very simple: `oc-export export <org> [tier1, tier2]`. If no tiers are specified, all available tiers will be exported.

Available tiers can be found using `oc-export list-tiers <org>`.
