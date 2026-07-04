## Python Execution & Virtual Environment (uv)
When operating within this repository, the agent sandbox does not automatically source the virtual environment. 
- NEVER run bare `python <script.py>` or `jupyter` commands. 
- ALWAYS prefix python executions with `uv run` (e.g., `uv run python <script.py>`) to ensure dependencies are resolved correctly.

## Jupyter Notebook Verification Standard
When a module is completed and the workflow requires "notebook verification", you must execute the notebooks programmatically and save the executed outputs in-place.
- Use the exact command: `uv run jupyter nbconvert --to notebook --execute --inplace notebooks/<notebook_name>.ipynb`
- If executing multiple notebooks, use a bash loop to execute them sequentially and check for errors, rather than a glob which will halt prematurely on the first failure.
