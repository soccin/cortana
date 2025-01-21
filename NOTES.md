# Notes

## Working Notes: 2025-01-21

### Working directory:

```
/juno/bic/work/socci/Work/Halo/MachineLearn/Cortana/Cortana
```

### Run command:

```
cat INPUTS | xargs -n 2 bsub -o LSF/ -n 32 -J MESMER -R cmorsc1 python Cortana/segment.py 
```

### Image paths:

```
/juno/bic/work/shared/MIRROR/mellinghofflab/1_ForHALO/GBM_project/EGFR_Cohort1_TME
```

### Sample Hierarchy:

The following hierarchy is used for labeling biological objects:

- Patient - individual human
    - Sample - tumor sample from patient
        - FOV [SPOT] - part of a sample


