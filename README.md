CYBER-NEXUS — BACKEND WORK COMPLETED

I completed the backend development and integrated the cybersecurity dataset, machine learning model, database, and AI analysis into the Cyber-Nexus project.

PROJECT BACKEND OVERVIEW

Cyber-Nexus is a cybersecurity investigation system built with a Flask backend. The backend uses SQLite for data storage, a cybersecurity investigation dataset for ML training and analysis, a Random Forest machine-learning model for severity prediction, and Featherless AI with DeepSeek-V3.2 for AI-assisted security analysis.


1. CYBERSECURITY DATASET

I added the cybersecurity investigation dataset:

dataset/cyber_investigation_master_10000.csv

The dataset contains 10,000 cybersecurity investigation records and 35 columns.

The dataset includes information such as:

- Event ID
- Timestamp
- Source type
- Source IP
- Destination IP
- Protocol
- URL information
- URL risk score
- File type
- File size
- File entropy
- Malware risk score
- Process count
- Failed logins
- Packets
- Bytes in/out
- Network activity
- Network anomaly score
- Unusual login
- Large outbound transfer
- Attack detection
- Possible data exfiltration
- Abnormal activity
- Severity
- Incident type
- Threat tactic
- Human approval requirement
- Recommended action


2. DATASET API INTEGRATION

I added API endpoints to verify and access the dataset.

GET /dataset/status

This checks whether the dataset exists and returns:

- Dataset name
- Number of rows
- Number of columns
- Column names

GET /dataset/sample

This returns the first 5 records from the dataset.

The dataset was successfully tested through the Flask API and returned actual dataset records.


3. MACHINE LEARNING MODEL

I created:

ml/train.py

The training script uses:

- pandas
- scikit-learn
- joblib

The target variable is:

severity

The model uses a Random Forest Classifier.

The dataset is divided into:

- 80% training data
- 20% testing data

The preprocessing pipeline handles:

- Numerical features using median imputation
- Categorical features using most-frequent imputation
- One-hot encoding for categorical values
- Unknown categorical values using handle_unknown="ignore"


4. MACHINE LEARNING FEATURES

The model uses cybersecurity-related features including:

Categorical features:

- source_type
- src_ip
- dst_ip
- protocol
- url
- url_class
- file_type
- file_class
- network_activity
- incident_type
- threat_tactic

Numerical features:

- url_length
- url_has_ip
- url_has_at_symbol
- url_has_redirect
- url_risk_score
- file_size_kb
- file_entropy
- malware_risk_score
- process_count
- failed_logins
- packets
- bytes_in
- bytes_out
- network_anomaly_score
- unusual_login
- large_outbound_transfer
- attack_detected
- possible_data_exfiltration
- abnormal_activity
- human_approval_required


5. MODEL TRAINING RESULT

The Random Forest model was trained successfully.

Dataset:

10,000 records

Training data:

8,000 records

Testing data:

2,000 records

The model achieved approximately:

Accuracy: 99.65%
Precision: 99.65%
Recall: 99.65%
F1 Score: 99.65%

The trained model was saved as:

ml/severity_model.pkl


6. MACHINE LEARNING PREDICTION API

I added:

POST /ml/predict

This endpoint loads the trained Random Forest model and predicts the severity of a supplied cybersecurity event.

Example result:

{
  "predicted_severity": "medium",
  "status": "success"
}

The endpoint was successfully tested.


7. FEATHERLESS AI INTEGRATION

The backend already uses Featherless AI through an OpenAI-compatible client.

The configuration uses:

Base URL:
https://api.featherless.ai/v1

Model:

deepseek-ai/DeepSeek-V3.2

The API key is stored through the backend environment configuration.

The AI is instructed to analyze cybersecurity events and return:

- Threat Level
- Confidence
- Indicators
- Recommendation

The AI is designed to provide defensive cybersecurity analysis and not instructions for performing attacks.


8. INTEGRATED ML + AI ANALYSIS

I modified:

POST /analyze

so that it can perform both:

1. Machine Learning severity prediction
2. Featherless AI security analysis

The flow is:

Security Event
      ↓
Flask /analyze API
      ↓
Random Forest ML Model
      ↓
Predicted Severity
      ↓
Featherless AI
      ↓
Threat Level + Confidence + Indicators + Recommendation
      ↓
SQLite Database
      ↓
API Response


9. DATABASE INTEGRATION

The security events generated through the /analyze endpoint are saved into the SQLite database.

The following information is stored:

- User ID
- Security event
- AI analysis

The backend also contains incident-related database functionality.

I fixed the database issue where the security_events table was initially not being found because of a database connection/path mismatch.

The user_id relationship was also added to the relevant security event and incident records.


10. SECURITY EVENTS

The backend provides:

GET /events

This returns stored security events.

It also provides:

GET /users/<user_id>/events

This returns events associated with a specific user.

Example user:

U001


11. INCIDENT MANAGEMENT

The backend provides:

GET /incidents

This returns available security incidents.

GET /incidents/<incident_id>

This returns detailed information about a specific incident.

Incident information can include:

- Incident ID
- User information
- Risk level
- Risk score
- Severity
- Status
- Associated events
- AI analysis


12. STATISTICS API

The backend provides:

GET /stats

This returns security-event statistics including:

- Total events
- Low severity events
- Medium severity events
- High severity events
- Critical severity events


13. USERS

The backend provides:

GET /users

The current database contains users including:

U001 — arjun
U002 — rahul
U003 — priya
A001 — admin

The system also contains login functionality through:

POST /login


14. CHAT API

The backend provides:

POST /chat

This provides AI-powered cybersecurity chat functionality through the configured AI service.


15. BASIC BACKEND ENDPOINTS

The backend currently contains:

GET /
GET /test-ai
POST /chat
POST /analyze
GET /events
GET /users/<user_id>/events
GET /stats
GET /users
POST /login
POST /investigate/<user_id>
GET /incidents
GET /incidents/<incident_id>
GET /dataset/status
GET /dataset/sample
POST /ml/predict


16. BACKEND SERVER

The Flask backend runs on:

http://localhost:8000

The backend is started using:

python3 -m backend.app

The Flask application listens on:

0.0.0.0:8000


17. PYTHON ENVIRONMENT ISSUES FIXED

During development, there was a Python environment mismatch.

The system had different Python installations for python and python3.

The backend was running with python3, so the required packages were installed into the python3 environment.

The required packages were installed and verified, including:

- pandas
- joblib
- scikit-learn

The scikit-learn version mismatch with the previously trained model caused a SimpleImputer compatibility error.

The model was retrained using the same Python/scikit-learn environment used by the Flask backend.

After retraining, ML prediction and the integrated /analyze endpoint worked successfully.


18. SUCCESSFUL END-TO-END TEST

The integrated /analyze endpoint was successfully tested with:

Event:

"Suspicious network activity detected with unusual outbound traffic"

The response successfully returned:

AI analysis:

Threat Level: MEDIUM
Confidence: 0.65
Indicators: unusual outbound traffic patterns
Recommendation: Isolate affected system, analyze network logs for destination IPs and data volume, and update firewall rules to block suspicious destinations.

ML prediction:

Severity: medium
Model: RandomForestClassifier

The event was also successfully saved into the database.


19. INCIDENT VERIFICATION

The existing incident:

INC-F3FC40DB

was successfully retrieved through:

GET /incidents/INC-F3FC40DB

The incident contains:

- User U001
- Risk level MEDIUM
- Risk score 25
- Severity MEDIUM
- Status OPEN
- Associated security events
- AI analysis for the events

The newly analyzed security event was successfully associated with the user's investigation data.


20. GIT VERSION CONTROL

All major backend changes were committed to Git.

Commit:

fea7c7b

Commit message:

"cybersecurity dataset and ML severity prediction"

The commit contains:

- backend/app.py
- ml/train.py
- ml/severity_model.pkl
- dataset/cyber_investigation_master_10000.csv

The changes were successfully pushed to GitHub.

Repository:

https://github.com/srivalli-bleppp/Cyber-Nexus

The remote main branch was successfully updated.

The only remaining local modification shown by git status was:

.DS_Store

This is a macOS metadata file and does not need to be included in the project.


21. CURRENT FRONTEND HANDOFF

The backend is now ready for frontend integration.

The frontend should communicate with:

http://localhost:8000

The frontend should use the backend APIs instead of directly accessing the SQLite database or ML model.

Important APIs for the frontend are:

GET /users
POST /login
GET /events
GET /users/<user_id>/events
GET /stats
GET /incidents
GET /incidents/<incident_id>
POST /analyze
POST /ml/predict
POST /chat


22. FRONTEND + BACKEND FLOW

User
 ↓
Frontend
 ↓
Flask Backend
 ↓
Database / ML / AI
 ↓
JSON Response
 ↓
Frontend


23. CURRENT PROJECT STATUS

Backend development completed:

✓ Flask backend
✓ SQLite database integration
✓ User functionality
✓ Login API
✓ Security event storage
✓ Incident management
✓ Statistics API
✓ Cybersecurity dataset integration
✓ 10,000-row dataset
✓ Dataset status API
✓ Dataset sample API
✓ Random Forest ML model
✓ ML training pipeline
✓ Trained severity model
✓ ML prediction API
✓ ML + AI integration
✓ Featherless AI integration
✓ DeepSeek-V3.2 integration
✓ End-to-end testing
✓ Git commit
✓ GitHub push

The backend is ready to be consumed by the frontend application.

The frontend team can clone the latest GitHub repository and begin frontend development.
# CyberNexus Frontend

CyberNexus is a cybersecurity dashboard built using **React.js** and **Tailwind CSS**.

The frontend provides a simple interface for monitoring security investigations, users, ML status, and connected systems.

 Technologies Used

* React.js
* Tailwind CSS
* Vite
* Lucide React Icons
* JavaScript / JSX

 Main Features

1. Overview

Displays:

* Active threats
* Ongoing cases
* ML anomalies
* System health
* Recent investigations
* ML engine status

2. Investigations Database

Allows users to:

* View security investigations
* Search investigations
* View threat severity
* View investigation status
* Create a new investigation

3. MCP Engine

Allows users to view and add external AI models.

It contains:

* Model name
* Provider
* Connection status
* Resources
* Tools

 4. IAM Directory

Used for managing users.

Users can:

* View existing users
* Add new users
* Assign roles
* View email and login information

 5. Admin Portal

Provides an administrative dashboard containing:

* System status
* Security policies
* Quick actions
* Security audit logs
 6. User App

Provides an employee workspace with:

* Security checklist
* IT and security messages
* Messaging interface


How to Run
Step 1: Open the frontend folder

Open Command Prompt or VS Code terminal and go to the frontend folder.

 Step 2: Install dependencies
Step 3: Start the frontend



 Step 4: Open the website

Open the address shown in the terminal

Backend Connection

The frontend can communicate with the CyberNexus Flask backend through the `/api` routes.

The Vite configuration forwards these requests to:
Make sure the backend is running before using features that require backend data.

The frontend can still display its initial dashboard data if the backend is not available.
Author

CyberNexus Project
