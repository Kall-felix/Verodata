## 📖 About the Project

**VeroData** was created to solve one of the biggest pain points in the tech industry and for Small and Medium-sized Businesses (SMBs): the massive amount of time spent cleaning raw data. 

This MVP (Minimum Viable Product) simulates a SaaS platform that democratizes data engineering. Without needing to write a single line of code, the user uploads a corrupted database, and our **CleanFlow Tool** applies statistical and algorithmic rules to deliver a pristine dataset, ready to be consumed by BI tools and Machine Learning models.

## 🚀 Key Features (How it works)

The platform executes a 5-step pipeline in real-time:

🗑️ **Duplicate Removal:** Automatic identification and discarding of 100% identical records.
🧮 **Null Imputation:** Filling in missing gaps (NaN/None) using statistical calculations (Mean for prices, Median for sales).
🧹 **Critical Cleaning:** Dropping unrecoverable rows (e.g., missing primary keys or store identifiers).
⚡ **Lambda Engine (Signs):** Lambda functions that scan numeric columns, converting anomalous negative values into absolute ones.
📅 **Regex Standardization:** Using Regular Expressions to clean textual noise and standardize dates from multiple formats into a single, unified output (`YYYY-MM-DD`).

### 📊 Data Health Score
An exclusive feature of our engine, the system dynamically calculates the initial "health" of the dataset. The algorithm cross-references the total size of the original matrix with the volume of interventions performed by the engine. This generates a product metric (from 0 to 100%) that instantly proves the value of the service provided.

## 💻 Come try it out, click the link below

https://verodata.streamlit.app
