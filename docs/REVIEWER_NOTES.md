# Reviewer Notes

This package is prepared for private verification of the submitted research workflow.

## Important Notes

1. The original uploaded notebook is preserved under `notebooks/`.
2. The modular scripts under `src/` are prepared to organize the notebook workflow into reproducible components.
3. The repository is private and not intended for public release at this stage.
4. The author may provide controlled access to editors or reviewers if required.
5. Final manuscript tables should be verified against the final submitted version before sharing with reviewers.

## Reproducibility Caution

Some numerical results may vary slightly depending on:

- data version,
- sorting,
- random seed,
- library version,
- final corrected result values used in the manuscript.

For this reason, the file `src/05_generate_paper_figures_reference.py` stores the final manuscript reference values separately for figure regeneration.
