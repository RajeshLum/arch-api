Entity Matching: api/match/ - Match entities (e.g., persons, companies) against a dataset using specific criteria✅
Entity Searching: api/search/ - Perform free-text queries to search for entities in a dataset✅
Risk Scoring: api/aml/risk/score - compute risk scores for individuals or entities based on data provided✅
Risk Scoring: api/aml/risk/score/{entity_id} - compute risk scores for specific entity✅
Entity Fetching: /api/entities/{entity_id} - Fetch entity with all it's related entity✅
Batch Uploading: /api/aml/batch/upload - Upload batch data to populate db✅
Reconcile Entity: /api/reconcile/ - Reconcile local data with external datasets for data cleaning, validation✅
OCR Uploading: /api/ocr/upload - Upload the OCR image to lookup❌



Questions:
1) User Registration/Login is missing
2) Where to get the adverse media lookup ? 
3) Where to get the geographic risk place ? 
4) Only use ftm.json for upload. 
5) Budget is low(You want batch upload, OCR feature on 200, deploymnet, doumentaiton all stuff on 200)