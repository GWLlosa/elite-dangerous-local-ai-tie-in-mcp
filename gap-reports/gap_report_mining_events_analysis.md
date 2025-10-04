# Gap Report: Mining Events Analysis

## Summary
MEDIUM **Severity**: MEDIUM

**Issue Type**: mining_events_verification

**Date**: 2025-10-04T14:29:55.944043

## Description
Analysis of all mining-related events found in journal files to verify the fix for GitHub issue #8.

## Mining Event Types Found

### AsteroidCracked
**Sample Count**: 6

**Sample Event**:
```json
{
  "timestamp": "2025-10-04T14:31:30Z",
  "event": "AsteroidCracked",
  "Body": "HR 8461 6 A Ring"
}
```

**Fields**: `timestamp`, `event`, `Body`


### MiningRefined
**Sample Count**: 20

**Sample Event**:
```json
{
  "timestamp": "2025-10-04T14:06:40Z",
  "event": "MiningRefined",
  "Type": "$gold_name;",
  "Type_Localised": "Gold"
}
```

**Fields**: `timestamp`, `event`, `Type`, `Type_Localised`


### ProspectedAsteroid
**Sample Count**: 18

**Sample Event**:
```json
{
  "timestamp": "2025-10-04T14:06:06Z",
  "event": "ProspectedAsteroid",
  "Materials": [
    {
      "Name": "gold",
      "Proportion": 30.257496
    },
    {
      "Name": "Samarium",
      "Proportion": 17.849192
    }
  ],
  "Content": "$AsteroidMaterialContent_Medium;",
  "Content_Localised": "Material Content: Medium",
  "Remaining": 100.0
}
```

**Fields**: `timestamp`, `event`, `Materials`, `Content`, `Content_Localised`, `Remaining`

