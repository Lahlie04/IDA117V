# Data dictionary

| Source field | Type | Model use | Meaning / treatment |
|---|---|---|---|
| Sub_Council | Categorical | Yes | Administrative/service grouping; missing values retained as `Missing`. |
| Ward | Categorical label | Yes | Ward label preserved as text; missing/odd labels monitored. |
| Suburb | Categorical | Yes | High-cardinality place label; privacy-sensitive when linked. |
| C3_Complaint_Type | Categorical | Yes | Primary complaint category. |
| Work_Center | Categorical | Yes, subject to confirmation | Routing/work-centre label assumed available at creation time. |
| Notification | Identifier-like | No | Excluded to avoid memorisation and leakage. |
| Notification_type | Mixed identifier/text | No | Excluded because it is high-cardinality and identifier-like. |
| X_Y_Co_ordinate_1 / 2 | Numeric coordinates | Flags only | Raw values excluded; only missing and `0,0` quality flags are used. |
| Created_On_Date | Datetime | Derived features | Creation timestamp used for chronological split and date features. |
| Changed_on | Datetime | No | Excluded as post-creation leakage. |
| Completed_Date | Datetime | Target only | Used only to derive the seven-day outcome. |
| Notifications_Created | Count | No | Excluded because it is nearly constant. |
| ObjectId | Identifier | No | Excluded from model features. |
| risk_7d | Binary target | Target | `1` when not completed within 0-7 days inclusive; missing/invalid completion is treated as at risk. |

## Derived model features

- `day_of_week`
- `day_index` from 1 April 2026
- `day_of_month`
- `is_weekend`
- `coord_missing`
- `coord_zero`
