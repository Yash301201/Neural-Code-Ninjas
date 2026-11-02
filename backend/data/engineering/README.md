# LearnPath Academic College Dataset

Locally generated fictional sample snapshots from MySQL. Not a public research dataset. Names omit demo suffixes; provenance is retained here and in manifest.json.

Current exported counts:

- students: 232
- faculty: 11
- hods: 5
- admins: 1
- staff evidence: 85
- enrollments: 232
- curriculum: 216
- topics: 648
- topic coverage: 1314
- subjects: 216
- teaching assignments: 438
- student subject performance: 1474

Join student IDs to enrollments; use study_year and semester in curriculum and teaching mappings. Topic coverage joins faculty_assignment_id and topic_id. No passwords, hashes or JWTs are included.

See backend/docs/year-wise-curriculum.md for year/section behavior and the read-only MySQL queries. CSVs are snapshots; the application reads live MySQL records.
