# Marker importance — `reference_set_real` (target: `v3_theme`, n=30)

Which lexical markers most distinguish each theme the pipeline assigns. Small-n diagnostic — read as indicative, not confirmatory.

## Weighted log-odds (distinctive markers per theme)
| theme | top markers (z-scored log-odds) |
|-------|----------------------------------|
| ACCOUNTABILITY | issues (2.38), trust (2.38), unlike (2.23), training (2.23), support (1.9), health (1.62) |
| ACCURACY | wouldn't (2.45), accurate (2.4), advice (2.25), ai (1.98), sense (1.95), better (1.95) |
| EMPATHY | human (2.68), mental (2.46), health (2.06), people (2.0), speaking (1.91), personal (1.88) |
| OTHER | ai (2.53), information (2.43), human (2.3), support (2.23), needed (2.21), i'd (2.18) |
| PRIVACY | information (2.67), data (2.3), confidential (2.28), concern (2.18), offer (2.18), expect (2.18) |
| SAFETY | chatbot (2.72), people (2.11), cause (1.84), ai (1.73), mental (1.71), years (1.61) |

## Logistic-regression importance (top positive coefficients)
| theme | top markers (coef) |
|-------|--------------------|
| ACCOUNTABILITY | unlike (0.55), training (0.55), trust (0.53), professional (0.29), past (0.29), say (0.29) |
| ACCURACY | accurate (0.5), concerns (0.49), therapy (0.41), i'd (0.4), advice (0.38), ai (0.32) |
| EMPATHY | just (0.52), people (0.46), human (0.45), offer (0.36), speaking (0.35), capable (0.34) |
| OTHER | needed (0.39), i'd (0.37), like (0.35), unless (0.35), need (0.35), time (0.34) |
| PRIVACY | information (0.77), confidential (0.63), concern (0.36), leaked (0.33), wrong (0.33), privacy (0.27) |
| SAFETY | cause (0.52), chatbot (0.44), life (0.43), risk (0.43), individuals (0.42), people (0.39) |
