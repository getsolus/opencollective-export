A simple CLI tool to export backer data from OpenCollective for ISO mailings. It might do more in the future.

# Setup
1. Clone this repository somewhere and `cd` into it.
2. Create a venv: `python3 -m venv venv`.
3. Activate your new venv: `source venv/bin/activate`.
4. Install requirements for this program into the venv: `pip install -r requirements.txt`.
5. Acquire an Open Collective [personal token](https://documentation.opencollective.com/development/personel-tokens).
> [!Note]
> Current operations are possible using only the "account" scope. For security, don't add any others.
6. Add your token to the keyring with `./oc-export.py set-token`. The program will prompt you for your token.
7. Move on to usage!

# Usage
> [!Warning]
> Remember to activate your venv before each time you use this program!

> [!Note]
> Most of this program's documentation lives in its built-in help. Run commands with `--help` to see detailed usage.

The usual operation (getting mailing list CSVs for each backer tier) is very simple: `./oc-export.py export`.
