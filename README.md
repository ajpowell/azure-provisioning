# azure-provisioning
Python code to provision Azure objects

---
## Python venv
Full details here: https://docs.python.org/3/library/venv.html

**Setup venv:**
    `python3 -m venv ./venv`

**Activate:**
Mac/Linux   `source ./venv/bin/activate`
Windows     `.\venv\Scripts\Activate.ps1`

## Requirements.txt
Full details here: https://datagy.io/python-requirements-txt/

Once venv is activated...

Update pip to latest version:
`python -m pip install --upgrade pip`

Install required modules using:
`pip install -r requirements.txt`

## Azure cli
Full details here: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-macos

Mac install azure-cli:
`brew update && brew install azure-cli`

## Misc
Store the subscription ID in an environment variable:
`export AZURE_SUBSCRIPTION_ID='xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'`

---
## Markdown Cheat Sheet

Details here: https://www.markdownguide.org/cheat-sheet/