![Screenshot 2025-02-05 001059](https://github.com/user-attachments/assets/032b9d61-6760-4505-ade5-a846722f467e)

A game of shoggoth. 

to install...

0) clone the repo using git and `cd` into it or use cursooooor or whatever
1) install `uv` somehow. google it
2) in the base directory, one after the other, `uv venv`, `source .venv/bin/activate`, `uv pip install -r requirements.txt` 
4) you will need an `OPENAI_API_KEY` and an `ANTHROPIC_API_KEY` from the respective developer portals. toss 5 buckaroos in each
5) you'll want to add those to your ~/.zshrc environment. chatgpt can help you with that but basically you need to create/edit a file in your home directory named .zshrc and add two lines:

```sh
export OPENAI_API_KEY='blahblah'
export ANTHROPIC_API_KEY='blahblah'
```

6) should be all set. close and reopen your terminal, navigate to the git directory. reactivate the virtual environment with `source .venv/bin/activate`.

    then you can run the game with  `python3 ./src/shoggoth.py` (takes a couple seconds to start up initially). Use the up and down arrow keys + enter to navigate.