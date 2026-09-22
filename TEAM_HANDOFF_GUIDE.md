# Team Handoff Guide
## E-Commerce Recommendation Engine

## 1. Project Overview

This project is an E-Commerce Recommendation Engine that combines:

- PySpark for large-scale data processing
- SparkML ALS for collaborative filtering
- Real-time user behavior for hybrid recommendations
- Local LLM (Llama 3.2 via Ollama) for product descriptions
- Streamlit for the web interface
- AWS S3 for cloud storage
- OWASP security analysis for e-commerce threats

---

## 2. Project Structure

```text
ECommerceRecommendationEngine/
│
├── app/
│   ├── app.py
│   ├── pages/
│   └── assets/
│
├── data/
│   ├── products.csv
│   ├── ecommerce_interactions.csv
│   └── user_searches.csv
│
├── outputs/
│   ├── recommendations.csv
│   ├── gpt_product_descriptions_clean.csv
│   ├── time_based_evaluation_results.csv
│   └── graphs/
│
├── src/
│   ├── process_data.py
│   ├── recommendation_model.py
│   ├── visualize_recommendations.py
│   ├── generate_product_descriptions.py
│   └── clean_ai_descriptions.py
│
├── prompts/
│
├── security/
│   └── owasp_threats.md
│
├── requirements.txt
├── .gitignore
└── TEAM_HANDOFF_GUIDE.md