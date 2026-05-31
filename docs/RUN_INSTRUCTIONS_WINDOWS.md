# Windows PowerShell Run Instructions

Open PowerShell inside the repository folder.

## Step 1: Create virtual environment

```powershell
py -m venv .venv
```

## Step 2: Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then activate again.

## Step 3: Install dependencies

```powershell
pip install -r requirements.txt
```

## Step 4: Run scripts one by one

```powershell
python src\01_dataset_inventory.py
python src\02_graph_feature_construction.py
python src\03_baseline_proposed_evaluation.py
python src\04_ablation_study.py
python src\05_generate_paper_figures_reference.py
```

## Step 5: Check outputs

Generated tables:

```text
results/tables/
```

Generated figures:

```text
results/figures/
```

Execution logs:

```text
results/logs/
```
