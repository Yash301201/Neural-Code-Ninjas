# OULAD source data

See the single [integration guide](../../docs/oulad-integration.md).

- `manifest.json`: import checksum, source, attribution and counts.
- `raw/oulad/`: one retained set of seven distinct CSV tables.
- The extra `anonymiseddata` copy was moved outside the project after SHA-256 verification.
- Repeated module codes with different presentations represent distinct offerings.

New downloads use `raw/oulad.zip`. The importer validates repeated CSV members inside the original archive and reads one copy.
