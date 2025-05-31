# Product Requirements Document (PRD)
## Project: ArchAngel AML Screening System
## Author: [Luminous Labs]
## Date: [2025-05-15]
---

## 1. Purpose
The purpose of this document is to define the product requirements for an Anti-Money Laundering (AML) screening system to identify and flag potentially suspicious financial activities in accordance with global compliance standards (FATF, OFAC, EU AML directives, etc.).

## 2. Background
Regulatory bodies require financial institutions to implement systems that monitor transactions and customer profiles to detect and prevent money laundering, terrorism financing, and sanctions violations.

## 3. Goals
- Screen customers and transactions against global watchlists.
- Real-time alert generation for matches and suspicious behavior.
- Provide an audit trail for compliance reporting.
- Enable investigators to review and manage alerts.

## 4. Scope
- Customer name screening (e.g., against OFAC, UN, PEP lists).
- Transaction monitoring rules (threshold, velocity, pattern detection).
- Risk scoring and alert prioritization.
- Alert management dashboard for compliance analysts.

## 5. Features
### 5.1. Sidebar Menus
- Dashboard
- Services
- Customers
- Reports
- Billing
- Settings

### 5.1. Dashboard Information
- Total verifications count and completion rate - /api/verifications/
- Status-wise breakdown (e.g., passed, failed, pending)

- Service-wise verification statistics

- Latest reports summary

### 5.2. Services 
Country Wise with option Manual Review
A service settings table for each type service /api/service-settings/ *
- AML Screening
- IDV - Identity Verification
- KYB - Know Your Business
- Investor Verification

### 5.2.1 AML Screening
- Screening Individuals/ Organizations info in models like Sanctions, Person, Organization etc.
- Store information in Customers table
- Store result in reports table

- Support for Batch AML Screening via CSV upload
- Provide downloadable sample CSV template
- Batch upload stat table /api/batch-screening/ *

### 5.2.2 IDV - Identity Verification
- e-IDV Pro
- Document verification
  NID, Passport, Driving license, Utility bill, Bank statement
- Address verification
- Consent verification
  Match uploaded document and consent data
- Facial Biometrics
- Video KYC

### 5.2.3 KYB - Know Your Business
- Info based by Company name/ Registration number
- Document based trade license/ tin / vat certificate

### 5.2.4 Investor Verification - * /api/investor-templates/
- Users can design and download a CSV form template
- Customers complete the template and upload for verification

### 5.3 Customers - /api/customers/
- Table with customer records
- Show total verification attempts and decline counts
- Ability to search, filter, and view customer history

### 5.4. Reports with manual review - /api/verifications/
- Table view of all reports with filters (date, status, type)
- Report Details include:
  Browser and device information
  Screening timeline
  Uploaded documents
- Export and download reports

### 5.5 Billing

### 5.6 Settings

### 5.7 Notification & Email
