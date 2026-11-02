# Single project folder and OULAD codes

The only local working copy is `C:/Users/DELL/OneDrive/Yash/OneDrive/Desktop/LearnPathAI`.
Its Git history now lives at this root. The nested `Neural-Code-Ninjas` source copy was removed from the project after verifying 134 identical files. Its unique `.gitignore` and `learnaipath.txt` were preserved at the root. No commit or push was made.

The duplicate `backend/data/oulad/raw/oulad/anonymiseddata` directory was removed from the project after SHA-256 verification of all seven files against the retained files in `raw/oulad`. This removed 464,367,129 bytes (about 443 MiB) from the project.

Automatic approval review rejected permanent deletion, so the duplicate folders were moved outside the project to `C:/Users/DELL/Documents/Codex/2026-10-31/bas/work/removed-duplicates` for recovery. A compressed pre-cleanup source backup is also retained outside the project.

The database directory, .env configuration, credentials, Python environment, dependencies, active frontend and Git history were preserved. The `frontend` directory is a separate legacy interface still referenced by FastAPI; `frontend-react` is the active interface. Numbered SQL scripts are distinct migrations and reports, not duplicate databases. Dependency lock files and the short backend startup wrapper have different purposes and remain necessary.

## OULAD identifiers

| Module identifiers | Published domain |
| --- | --- |
| AAA, BBB, GGG | Social Sciences |
| CCC, DDD, EEE, FFF | STEM: Science, Technology, Engineering and Mathematics |

These are anonymized module identifiers. Original course titles are not provided. They must not be relabeled as the college's actual subjects or UG/PG majors.

`B` presentations start in February, and `J` presentations start in October. For example, `2014J` identifies the October 2014 offering. The same module can have multiple offerings, so repeated module codes across presentations are expected.

Sources: [original OULAD paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC5704676/) and [Open University dataset description](https://research.stem.open.ac.uk/ouanalyse/dataset/).

## Run

From the LearnPathAI root:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-project.ps1
```

The frontend remains at http://127.0.0.1:8001/app/. Refresh the browser to load the clarified research module labels.
