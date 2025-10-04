# KarmaChain v2: Dual-Ledger Karmic Engine

## Overview

KarmaChain v2 extends the original system with a dual-ledger approach that tracks both positive (Punya) and negative (Paap) karmic actions. This enhancement creates a more balanced and realistic model of karmic accounting, allowing users to accumulate both merit and demerit, with mechanisms for atonement and rebirth.

## Core Concepts

### Dual-Ledger System

The dual-ledger system maintains two separate token categories:

1. **Positive Tokens (Existing)**
   - DharmaPoints
   - SevaPoints
   - PunyaTokens (minor, medium, major)

2. **Negative Tokens (New)**
   - PaapTokens (minor, medium, maha)

### Paap Classification

Actions that generate negative karma are classified into three severity levels:

- **Minor Paap**: Small transgressions (e.g., false speech, breaking promises)
- **Medium Paap**: Moderate transgressions (e.g., cheating, disrespecting teachers)
- **Maha Paap**: Severe transgressions (e.g., violence, causing harm to others)

### Atonement System

Users can atone for negative actions through four types of practices:

1. **Jap**: Recitation of mantras or prayers
2. **Tap**: Austerities like fasting
3. **Bhakti**: Devotional practices
4. **Daan**: Charitable giving

### Rebirth Mechanics

When a user completes their current lifecycle (death event), their karma determines their rebirth destination:

- **Swarga**: Heavenly realm for those with excellent karma
- **Martya**: Middle realm (human world) for those with balanced karma
- **Naraka**: Lower realm for those with predominantly negative karma

## API Endpoints

### Appeal System

```
POST /appeal/karma
```
Submit an appeal for a negative action.

**Request Body:**
```json
{
  "user_id": "string",
  "action": "string",
  "note": "string"
}
```

**Response:**
```json
{
  "appeal_id": "string",
  "status": "pending",
  "atonement_plan_id": "string"
}
```

```
POST /appeal/submit-atonement
```
Submit proof of atonement activities.

**Request Body:**
```json
{
  "user_id": "string",
  "atonement_plan_id": "string",
  "atonement_type": "string",
  "proof": "string",
  "units": "number"
}
```

**Response:**
```json
{
  "status": "string",
  "progress": {
    "Jap": "number",
    "Tap": "number",
    "Bhakti": "number",
    "Daan": "number"
  },
  "completed": "boolean"
}
```

```
POST /appeal/submit-atonement-file
```
Submit proof of atonement with file upload.

```
GET /appeal/status/{user_id}
```
Check the status of a user's appeals and atonement plans.

```
POST /appeal/death
```
Trigger a death event for rebirth processing.

**Request Body:**
```json
{
  "user_id": "string"
}
```

**Response:**
```json
{
  "assigned_loka": "string",
  "net_karma": "number",
  "carryover": {
    "carryover_paap": "number",
    "carryover_punya": "number",
    "starting_level": "string"
  }
}
```

### Updated Actions API

The existing `/actions/log` endpoint now supports Paap-generating actions:

**Response includes:**
```json
{
  "paap_severity": "string",
  "paap_tokens": {
    "minor": "number",
    "medium": "number",
    "maha": "number"
  },
  "atonement_plan_id": "string (optional)"
}
```

## Implementation Details

### Token Schema

The token schema is defined in `schemas/token_schema.json` and includes:

- Existing tokens (DharmaPoints, SevaPoints, PunyaTokens)
- New PaapTokens with severity classes
- Atonement credits (Jap, Tap, Bhakti, Daan)

### Configuration

New constants in `config.py`:

- `PaapTokens`: Definition of negative token types
- `PAAP_CLASSES`: Classification of actions by severity
- `PRAYASCHITTA_MAP`: Atonement requirements for each severity level
- `LOKA_THRESHOLDS`: Thresholds for rebirth assignment

### Utility Modules

1. **utils/paap.py**
   - Classifies actions into Paap severity categories
   - Calculates Paap values based on severity
   - Applies PaapTokens to user balances
   - Calculates total weighted Paap score

2. **utils/atonement.py**
   - Retrieves prescribed atonement plans
   - Creates new atonement plans
   - Validates and records atonement proofs
   - Updates atonement progress
   - Marks plans as completed
   - Reduces PaapTokens upon successful atonement

3. **utils/loka.py**
   - Calculates net karma (Punya vs Paap)
   - Assigns users to appropriate Loka
   - Creates rebirth carryover objects
   - Applies rebirth effects

4. **utils/qlearning.py** (Enhanced)
   - Added support for atonement rewards
   - Q-learning steps for atonement completion

### Vedic Dataset

The system includes a dataset of Vedic references in `data/vedic_corpus/`:

- `mahapaap_map.json`: Maps actions to severity classes with textual references
- `sources.md`: Documentation of Vedic sources

## Migration

To migrate from KarmaChain v1 to v2:

1. Run the migration script: `python scripts/migrate_to_v2.py`
2. The script will:
   - Create new collections for appeals and atonements
   - Update user schema to include PaapTokens
   - Create necessary indexes
   - Initialize default values

## Testing

Test files are provided to verify the functionality:

1. **tests/test_appeal.py**: Tests the appeal lifecycle
2. **tests/test_paap.py**: Tests Paap issuance and atonement processes

## Security Considerations

1. **Validation**: All user inputs are validated before processing
2. **Authentication**: Ensure proper authentication for all endpoints
3. **File Uploads**: Atonement proof file uploads are validated for type and size
4. **Data Integrity**: Transactions are atomic to prevent partial updates

## Future Enhancements

1. **Community Validation**: Allow community members to validate atonement proofs
2. **Karma Visualization**: Graphical representation of karma balance
3. **Smart Contracts**: Blockchain integration for immutable karma records
4. **AI-Powered Atonement**: Personalized atonement recommendations