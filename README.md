# simulations

**HRCM global and regional climate model simulations documentation**

This repo contains `.yml` files, each describing an individual Met Office Unified Model (`UM/`) or LFRic (`LFRic/`) simulation, which are used to populate the HRCM simulation catalogue at **[hrcm.ceda.ac.uk/data](https://hrcm.ceda.ac.uk/data)**.

To add a simulation, use the **`create-simulation-template`** workflow under Actions to create a new, blank `simulation_id.yml` template file. This workflow runs `scripts/create_simulation_template.py`.

(Additionally, `scripts/` contains code used to develop the workflow on [cedadev/hrcm-website](https://github.com/cedadev/hrcm-website), which is retained here.)
