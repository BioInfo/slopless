# Data Processing Rules

- **Duplicate Detection**: Filter at source (database query) not downstream.
- **Timestamp Matching**: Check full date+time tuple, not just date. Parse exact times.
- **Batch Operations**: Verify time-level uniqueness to prevent duplicate processing.
