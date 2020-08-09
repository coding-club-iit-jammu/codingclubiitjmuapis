# Ava
All apis created for Coding Club IIT Jammu currently used in discord Server.

[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)

## Technology stack

- Python 3.7
- Azure Serverless Functions
    
# Instructions to Run locally and contribute
1. Install [Python](https://www.python.org/downloads/).
2. Clone this repository and open terminal, change directory to the repo.
3. Run `python -m venv ./venv` to create virtual environment.
4. Run `venv\Scripts\activate` command to activate virtual environment.
5. Run `pip install -r reqirements.txt` command to install dependencies.
6. Create a **local.settings** file in the folder, containing

```
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "reddit" : <REDDIT_KEY>,
    "DISCORD_CONTACT" : <DISCORD_WEBHOOK>
  }
}
```
You can create a demo server and a bot application for testing purpose. Details [here](https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot).

7. Run `func start`.

If creating first function refer to [Create a function in Azure that responds to HTTP requests](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-azure-function-azure-cli?tabs=bash%2Cbrowser&pivots=programming-language-python)
