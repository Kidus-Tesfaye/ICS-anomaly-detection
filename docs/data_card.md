# Data Card (Milestone 2)

Raw data is **never committed or redistributed** — this file documents provenance, access,
licensing, and known quirks; the download script verifies checksums.

## HAI (primary)

- **Source:** https://github.com/icsdataset/hai (public, no registration)
- **Version pinned:** TODO (exact release tag)
- **License / terms:** TODO (record from the repo at download time)
- **Sampling rate / sensors / actuators:** TODO (M2 exploration)
- **Class imbalance ratio:** TODO
- **Known quirks:** attack labels may lag true onset (verify against dataset docs); TODO
- **Split rule used here:** contiguous blocks, boundary gap ≥ window size (ADR-0001)
- **Processed-artifact checksums:** TODO (committed so others can verify reproduction)

### SWaT / community implementations

Not literature, but useful as preprocessing sanity checks (unvetted, no
accompanying paper — do not cite as related work):

- `ngoclesydney/Anomaly-Detection-with-Swat-Dataset` (GitHub, 2020) —
  https://github.com/ngoclesydney/Anomaly-Detection-with-Swat-Dataset
  Linked from the iTrust SWaT page, which describes it as "a comprehensive
  implementation of deep learning-based anomaly detection techniques applied to
  the iTrust Secure Water Treatment (SWaT) dataset". Accessed 2026-07-24.

## SWaT (secondary, pending iTrust access)

- **Status:** pending approval — request submitted 2026-07-24, no response yet. Follow up
  2026-08-07 if still silent. Not blocking: SWaT is only needed at M7.
- **Source:** iTrust, SUTD — request form required; approval can take days–weeks.
- **License / terms:** redistribution forbidden (do not use third-party copies).
- Remaining fields: TODO on access.

### Fallback: BATADAL

Openly available water-distribution dataset, used alongside SWaT/WADI in the literature. If
iTrust access hasn't arrived by M7, use BATADAL as the second dataset instead of delaying.
