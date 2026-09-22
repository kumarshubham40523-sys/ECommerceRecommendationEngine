# 🛒 E-Commerce Recommendation Engine

A personalized **E-Commerce Recommendation Engine** built using **PySpark, Spark MLlib ALS, Python, and Streamlit**. The system processes user-product interaction data, trains a collaborative filtering model, generates personalized product recommendations, and presents the results through an interactive web interface.

---

## 📌 Table of Contents

* [Overview](#-overview)
* [Objectives](#-objectives)
* [Key Features](#-key-features)
* [Technology Stack](#-technology-stack)
* [System Architecture](#-system-architecture)
* [Project Structure](#-project-structure)
* [Dataset](#-dataset)
* [Data Processing](#-data-processing)
* [Recommendation Model](#-recommendation-model)
* [Model Workflow](#-model-workflow)
* [Streamlit Dashboard](#-streamlit-dashboard)
* [Product Description Generation](#-product-description-generation)
* [Security Considerations](#-security-considerations)
* [Installation](#-installation)
* [Configuration](#-configuration)
* [How to Run](#-how-to-run)
* [Example Output](#-example-output)
* [Model Evaluation](#-model-evaluation)
* [Results](#-results)
* [Known Issues](#-known-issues)
* [Future Enhancements](#-future-enhancements)
* [Use Cases](#-use-cases)
* [Conclusion](#-conclusion)
* [Authors](#-authors)

---

# 📖 Overview

The **E-Commerce Recommendation Engine** is a machine-learning-based recommendation system designed to provide personalized product suggestions to users.

Modern e-commerce platforms generate large amounts of interaction data such as:

* Product views
* Clicks
* Purchases
* Ratings
* User-product interactions

The system processes this interaction data using **Apache Spark / PySpark** and applies **Collaborative Filtering with the Alternating Least Squares (ALS)** algorithm to discover relationships between users and products.

The trained model generates personalized recommendations for users based on their historical interaction patterns.

An interactive **Streamlit dashboard** is used to visualize recommendations and present product information in a user-friendly interface.

---

# 🎯 Objectives

The main objectives of this project are:

1. Process large-scale e-commerce interaction data using **PySpark**.
2. Prepare user-product interaction data for machine learning.
3. Implement a collaborative filtering recommendation system using **Spark MLlib ALS**.
4. Generate personalized product recommendations.
5. Display recommendations through an interactive **Streamlit** interface.
6. Generate or display product descriptions for recommended products.
7. Identify potential security threats using the **OWASP Top 10**.
8. Build a scalable recommendation architecture suitable for real-world e-commerce applications.

---

# 🚀 Key Features

### 🔹 Data Processing

* Reads raw e-commerce interaction data.
* Cleans and preprocesses the dataset.
* Converts interaction information into ALS-compatible format.
* Handles user and product identifiers.

### 🔹 Machine Learning

* Uses **Collaborative Filtering**.
* Implements **Alternating Least Squares (ALS)** using Spark MLlib.
* Splits data into training and testing datasets.
* Generates Top-N personalized recommendations.

### 🔹 Recommendation System

* Generates product recommendations for individual users.
* Produces ranked recommendations based on predicted interaction scores.
* Supports multiple recommended products per user.

### 🔹 Interactive Dashboard

The Streamlit interface provides:

* User selection
* Personalized recommendations
* Product information
* Recommendation scores
* Product cards
* Interactive UI

### 🔹 AI-Generated Product Descriptions

The project can generate or display AI-assisted descriptions for recommended products.

### 🔹 Security Analysis

The project includes an analysis of potential web application threats based on the **OWASP Top 10**, including:

* Injection
* Broken Access Control
* Authentication failures
* Security misconfiguration
* Data exposure
* Cross-site scripting

---

# 🛠️ Technology Stack

| Technology   | Purpose                         |
| ------------ | ------------------------------- |
| Python       | Core programming language       |
| PySpark      | Large-scale data processing     |
| Apache Spark | Distributed computing           |
| Spark MLlib  | Machine learning                |
| ALS          | Collaborative filtering         |
| Pandas       | Data analysis and preprocessing |
| Streamlit    | Web dashboard                   |
| Matplotlib   | Data visualization              |
| CSV          | Data storage/input format       |
| Git/GitHub   | Version control                 |

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │   E-Commerce Data    │
                    │ User/Product Events  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Data Preprocessing   │
                    │ Cleaning & Formatting │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   PySpark Processing │
                    │ User-Product Pairs   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Train/Test Split     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Spark MLlib ALS    │
                    │ Collaborative Filter │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Recommendation Model │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Top-N Recommendations│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Streamlit Dashboard  │
                    └──────────────────────┘
```

---

# 📂 Project Structure

```text
ECommerceRecommendationEngine/
│
├── .venv/
│
├── data/
│   ├── interactions.csv
│   ├── products.csv
│   └── users.csv
│
├── src/
│   ├── data_preprocessing.py
│   ├── recommendation_model.py
│   ├── generate_recommendations.py
│   └── app.py
│
├── outputs/
│   ├── recommendations/
│   ├── plots/
│   └── results/
│
├── README.md
├── requirements.txt
└── .gitignore
```

> The exact filenames may vary depending on the final project implementation.

---

# 📊 Dataset

The recommendation system uses user-product interaction data.

A typical interaction record contains information such as:

| Column        | Description                      |
| ------------- | -------------------------------- |
| `user_id`     | Unique identifier of the user    |
| `product_id`  | Unique identifier of the product |
| `interaction` | Interaction/rating value         |
| `timestamp`   | Time of interaction              |

Example:

```text
user_id,product_id,interaction
101,501,5
101,502,3
102,501,4
102,503,5
103,504,2
```

The interaction value represents the strength of the relationship between a user and a product.

---

# 🧹 Data Processing

The raw dataset is processed before training the recommendation model.

### Step 1 — Load Data

The interaction dataset is loaded using PySpark.

### Step 2 — Data Cleaning

The system checks for:

* Missing values
* Invalid user IDs
* Invalid product IDs
* Duplicate records
* Incorrect data types

### Step 3 — Feature Preparation

The dataset is converted into the format required by Spark ALS:

```text
user
item
rating
```

### Step 4 — Train/Test Split

The dataset is divided into training and testing data.

In the current implementation:

```text
Total user-product pairs : 44,311
Training records         : 35,440
Testing records          : 8,871
```

This corresponds approximately to an **80:20 train-test split**.

---

# 🤖 Recommendation Model

The project uses **Collaborative Filtering** with the **Alternating Least Squares (ALS)** algorithm.

ALS is available through Spark MLlib and is commonly used for recommendation systems.

The basic idea is:

```text
Users ──────── Interactions ──────── Products
  │                                      │
  └──────────── ALS Model ──────────────┘
                     │
                     ▼
             Predicted Ratings
                     │
                     ▼
              Top Recommendations
```

The model learns hidden/latent representations of users and products.

---

# 🔬 Collaborative Filtering

Collaborative filtering recommends products based on patterns in user behavior.

For example:

```text
User A → Product 1
User A → Product 2

User B → Product 1
User B → Product 2
User B → Product 3
```

Since User A and User B have similar interaction patterns, Product 3 may be recommended to User A.

The system does not necessarily need detailed product attributes to discover these relationships.

---

# ⚙️ ALS Model

The ALS model attempts to approximate the user-item interaction matrix.

Conceptually:

```text
Interaction Matrix

             Product
             P1 P2 P3 P4
User U1      5  4  ?  ?
User U2      4  ?  5  ?
User U3      ?  3  4  5
```

ALS decomposes the matrix into latent user and product factors.

```text
User Factors × Product Factors ≈ Interaction Matrix
```

The model then uses these learned factors to predict unknown interactions.

---

# 🔄 Model Workflow

The complete machine-learning workflow is:

```text
Raw Dataset
     │
     ▼
Data Cleaning
     │
     ▼
Data Transformation
     │
     ▼
User/Product Encoding
     │
     ▼
Train/Test Split
     │
     ▼
ALS Model Training
     │
     ▼
Model Prediction
     │
     ▼
Recommendation Ranking
     │
     ▼
Top-N Products
```

---

# 📈 Recommendation Generation

After training, the model generates product recommendations for users.

For example:

```text
User ID: 101

Recommended Products:

1. Product 245
   Score: 4.82

2. Product 731
   Score: 4.65

3. Product 119
   Score: 4.51

4. Product 552
   Score: 4.37

5. Product 904
   Score: 4.21
```

The exact recommendation scores depend on the trained ALS model and dataset.

---

# 🖥️ Streamlit Dashboard

The project includes a Streamlit-based user interface.

The dashboard is designed to make the recommendation system easier to interact with.

### Main components

```text
┌───────────────────────────────────────────┐
│       🛒 E-Commerce Recommendation        │
├───────────────────────────────────────────┤
│                                           │
│ Select User: [ User 101 ▼ ]              │
│                                           │
│       Personalized Recommendations        │
│                                           │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ │ Product  │ │ Product  │ │ Product  │   │
│ │    1     │ │    2     │ │    3     │   │
│ │          │ │          │ │          │   │
│ │ Score    │ │ Score    │ │ Score    │   │
│ └──────────┘ └──────────┘ └──────────┘   │
│                                           │
└───────────────────────────────────────────┘
```

---

# 📝 Product Description Generation

The application can associate recommended products with descriptive content.

Example:

```text
Product:
Wireless Headphones

Description:
Experience clear audio and comfortable listening with
these wireless headphones, designed for everyday use.
```

### Character Encoding

Special characters such as:

```text
₹
é
™
©
```

must be handled using proper **UTF-8 encoding**.

The application should avoid displaying malformed/control-character artifacts such as:

```text
â‚¹
Ã©
```

when rendering product descriptions.

Recommended practices include:

```python
encoding="utf-8"
```

when reading/writing text-based files and ensuring that the Streamlit application consistently handles UTF-8 content.

---

# 🔐 Security Considerations

The project also considers common web application security threats.

## OWASP Threat Analysis

| Threat                    | Possible Risk                          | Mitigation                       |
| ------------------------- | -------------------------------------- | -------------------------------- |
| Injection                 | Malicious input may manipulate queries | Parameterized queries            |
| Broken Access Control     | Unauthorized access                    | Role-based authorization         |
| Authentication Failures   | Account compromise                     | Secure authentication            |
| Cryptographic Failures    | Sensitive data exposure                | Encryption                       |
| Security Misconfiguration | Exposed services/settings              | Secure configuration             |
| XSS                       | Malicious scripts in user input        | Input validation/output encoding |
| Insecure Design           | Weak application architecture          | Threat modeling                  |
| Vulnerable Components     | Exploitable dependencies               | Regular updates                  |
| Logging Failures          | Difficult incident detection           | Centralized logging              |
| SSRF                      | Unauthorized server-side requests      | URL validation                   |

---

# 💻 Installation

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Navigate to the project directory:

```bash
cd ECommerceRecommendationEngine
```

---

## 2. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

If PowerShell blocks activation, you can use:

```bash
.venv\Scripts\activate.bat
```

or activate the environment through the VS Code terminal using the appropriate shell.

---

# 📦 Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Example dependencies:

```text
pyspark
pandas
numpy
scikit-learn
matplotlib
streamlit
```

The exact versions should match the versions used in the project environment.

---

# ⚙️ Configuration

Before running the project, verify:

* Python is installed.
* Java is installed.
* PySpark is installed.
* Required datasets are inside the `data/` directory.
* Output directories exist.
* Required environment variables are configured.

Check Python:

```bash
python --version
```

Check Java:

```bash
java -version
```

Check PySpark:

```bash
pyspark --version
```

---

# ▶️ How to Run

## Step 1 — Activate Virtual Environment

```bash
.venv\Scripts\activate
```

---

## Step 2 — Run the Recommendation Pipeline

Depending on the project structure:

```bash
python src/recommendation_model.py
```

This performs the following operations:

```text
Load Data
    ↓
Preprocess Data
    ↓
Create Training/Test Sets
    ↓
Train ALS
    ↓
Generate Recommendations
    ↓
Save Results
```

---

## Step 3 — Run Streamlit

Start the web application:

```bash
streamlit run src/app.py
```

Streamlit will start a local development server.

Open the displayed local URL in your browser.

---

# 📊 Example Output

The system produces personalized recommendations similar to:

```text
=========================================
      PERSONALIZED RECOMMENDATIONS
=========================================

User ID: 101

Rank    Product ID       Prediction
-----------------------------------------
1       245              4.82
2       731              4.65
3       119              4.51
4       552              4.37
5       904              4.21
```

These values are generated by the trained ALS model and can vary depending on model parameters and the dataset.

---

# 📐 Model Evaluation

The recommendation model can be evaluated using prediction error metrics.

One commonly used metric is **Root Mean Square Error (RMSE)**.

### RMSE Formula

$$
RMSE =
\sqrt{
\frac{1}{n}
\sum_{i=1}^{n}
(y_i-\hat{y_i})^2
}
$$

Where:

* \(y_i\) = Actual rating
* \(\hat{y_i}\) = Predicted rating
* \(n\) = Number of observations

Lower RMSE indicates smaller prediction error.

For recommendation systems, ranking-based metrics such as **Precision@K**, **Recall@K**, and **MAP@K** can also be considered.

---

# 📊 Project Results

The implemented pipeline successfully processes the e-commerce interaction dataset and trains an ALS recommendation model.

### Dataset Processing

```text
Total user-product pairs : 44,311
Training records         : 35,440
Testing records          : 8,871
```

### Model

```text
Algorithm:
Collaborative Filtering

Model:
Alternating Least Squares (ALS)

Framework:
Apache Spark MLlib
```

### Output

The trained model successfully generates **Top-N product recommendations** for users.

The recommendations can then be displayed through the Streamlit dashboard.

---

# ⚠️ Known Issues

## 1. Windows Hadoop / winutils Issue

When running PySpark on Windows, file-writing operations may produce an error similar to:

```text
HADOOP_HOME and hadoop.home.dir are unset
```

or:

```text
winutils.exe is missing
```

This is related to the Hadoop environment used by Spark on Windows.

---

## 2. BLAS / Native Library Warning

Spark may also display messages related to:

```text
netlib-blas
libopenblas.dll
```

These messages may affect native numerical acceleration but do not necessarily indicate that the recommendation algorithm itself has failed.

---

## 3. Pandas Compatibility

Some Spark versions may have compatibility issues with very recent Pandas versions.

If a warning indicates that the installed Pandas version is unsupported, use a compatible version, for example:

```bash
pip install "pandas<3.0"
```

The exact compatible version should depend on the Spark/PySpark version being used.

---

# 🔮 Future Enhancements

The project can be extended with several features.

### 1. Real-Time Recommendations

Update recommendations immediately based on new user interactions.

### 2. Hybrid Recommendation System

Combine:

```text
Collaborative Filtering
        +
Content-Based Filtering
```

to improve recommendations.

### 3. Deep Learning

Explore neural recommendation models such as:

* Neural Collaborative Filtering
* Autoencoders
* Deep & Cross Networks

### 4. Cloud Deployment

Deploy the recommendation system using:

* AWS
* Microsoft Azure
* Google Cloud

### 5. Database Integration

Replace CSV-based storage with a production database such as:

* MySQL
* PostgreSQL
* MongoDB

### 6. User Authentication

Add:

* Login
* Registration
* User profiles
* Role-based access

### 7. Advanced Analytics

Add dashboards for:

* Popular products
* User engagement
* Click-through rate
* Conversion rate
* Recommendation performance

### 8. Model Monitoring

Monitor:

* Prediction quality
* Recommendation diversity
* Data drift
* Model performance

---

# 🌐 Real-World Use Cases

The recommendation engine can be applied to:

### 🛍️ E-Commerce

Recommend products based on previous purchases and browsing behavior.

### 🎬 Entertainment

Recommend:

* Movies
* TV shows
* Music

### 📚 Education

Recommend:

* Courses
* Books
* Learning resources

### 📰 Content Platforms

Recommend:

* Articles
* Videos
* News

### 🏦 Financial Services

Potentially recommend relevant:

* Financial products
* Services
* Personalized offers

---

# 📚 Learning Outcomes

Through this project, the following concepts were explored:

* Big Data Processing
* PySpark
* Apache Spark
* Spark MLlib
* Collaborative Filtering
* ALS Algorithm
* Recommendation Systems
* Train/Test Splitting
* Machine Learning Pipelines
* Data Visualization
* Streamlit
* AI-generated Content
* OWASP Security
* Software Architecture
* Model Evaluation

---

# 🧠 Key Concepts

### PySpark

Python API for Apache Spark used for distributed data processing.

### Apache Spark

A distributed computing framework designed for processing large datasets efficiently.

### Spark MLlib

Spark's machine-learning library containing algorithms for classification, regression, clustering, recommendation, and more.

### Collaborative Filtering

A recommendation approach that uses user-item interaction patterns to make recommendations.

### ALS

Alternating Least Squares is a matrix-factorization algorithm used by Spark MLlib for collaborative filtering.

### Streamlit

A Python framework for building interactive data and machine-learning web applications.

---

# 📁 Output Files

The project may generate output files such as:

```text
outputs/
│
├── recommendations/
│   └── recommendations.csv
│
├── plots/
│   ├── recommendation_plot.png
│   └── interaction_analysis.png
│
└── results/
    └── model_results.csv
```

The exact output structure depends on the final implementation.

---

# 🧪 Example End-to-End Execution

```text
                  START
                    │
                    ▼
             Load Dataset
                    │
                    ▼
            Clean Interaction Data
                    │
                    ▼
          Prepare ALS Input Format
                    │
                    ▼
             Train/Test Split
                    │
                    ▼
             Train ALS Model
                    │
                    ▼
          Generate Predictions
                    │
                    ▼
          Generate Top-N Products
                    │
                    ▼
            Save Recommendations
                    │
                    ▼
           Launch Streamlit App
                    │
                    ▼
       Display Personalized Products
                    │
                    ▼
                   END
```

---

# 🎓 Academic Project

This project demonstrates the practical application of:

```text
Big Data
     +
Machine Learning
     +
Recommendation Systems
     +
Web Application Development
     +
Cybersecurity
```

It provides an end-to-end implementation starting from raw interaction data and ending with personalized product recommendations displayed through an interactive interface.

---

# 👨‍💻 Authors

**E-Commerce Recommendation Engine Project**

Developed as an academic/project implementation focusing on:

* Big Data Analytics
* Machine Learning
* Recommendation Systems
* PySpark
* Streamlit

---

# 📜 License

This project is intended for **educational and academic purposes**.

If you plan to distribute or deploy the project commercially, add an appropriate open-source or proprietary license based on your requirements.

---

# ⭐ Acknowledgements

* Apache Spark / PySpark
* Spark MLlib
* Python
* Streamlit
* Pandas
* NumPy
* Matplotlib
* OWASP

---

# 🔗 Project Summary

**E-Commerce Recommendation Engine** is an end-to-end recommendation system that uses **PySpark and Spark MLlib's ALS collaborative filtering algorithm** to process user-product interaction data and generate personalized product recommendations.

The system combines **Big Data processing, Machine Learning, AI-generated product descriptions, visualization, and security analysis** into a single application.

```text
       USER DATA
           │
           ▼
    ┌──────────────┐
    │   PySpark    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │     ALS      │
    │ Recommendation│
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Top-N Items  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Streamlit   │
    │  Dashboard   │
    └──────────────┘
```

**Built with Python + PySpark + Spark MLlib + Streamlit 🚀**
