# Topic 2 — Symbolic AI (P. Bonnard)

Separate course from Topic 1 (Agentic AI, D. Parisot, repository root). One folder per notebook, as distributed in `esilv-lecture-2026` (Moodle, Topic 2); only the exercise notebooks are versioned.

| Folder | Notebook | Content |
|---|---|---|
| `00-setup-check/` | `checking-notebook_exo.ipynb` | installation check |
| `lecture-1/` … `lecture-5/` | `lecture-SymPy-N_exo.ipynb` | lecture exercises (graphviz needed for lecture 5) |
| `taylor-pi/` | `taylor-pi-sympy_exo.ipynb` | Taylor series / π |
| `tp1/`, `tp2/`, `tp3/` | `tp-SymPy-N_exo.ipynb` | practical work |

Not versioned (see `.gitignore`): the course archive, the instructor's `solutions/`, the lecture PDFs, `.venv/`, `.ipynb_checkpoints/`.

## Run

```powershell
cd topic2-symbolic-ai
python -m venv .venv
.venv\Scripts\Activate.ps1            # macOS/Linux: source .venv/bin/activate
python -m pip install jupyterlab sympy numpy graphviz
# optional, lecture 5: winget install --id Graphviz.Graphviz --exact --source winget
#                      $env:PATH = "C:\Program Files\Graphviz\bin;$env:PATH"; dot -V
python -m jupyterlab
```
