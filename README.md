# karaoke-bot
This is a Telegram bot that I'm making to track songs I'd be singing with friends.





## Installation
To run this bot, you need to set up a Conda environment with the necessary dependencies.

### Setting Up the Conda Environment
1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) if you haven't already.
2. Clone this repository:

```bash
git clone https://github.com/yourusername/karaoke-bot.git
cd karaoke-bot
```
3. Create a Conda environment using the `environment.yml` file:
```bash
conda env create -f environment.yml
```
4. Activate the environment:
```bash
conda activate karaoke-bot
```



## Usage
To run the bot:
`\path-to-miniconda\miniconda3\envs\karaoke-bot\python.exe main.py`

It is important to point to the correct version of python being used to run the file for some reason. Ensure that you do not run this notebook in an interactive window as well. 


# Setting up the bot with @BotFather

Make sure to get the API key from BotFather, and also set the privacy of the bot off to enable messages from groups.