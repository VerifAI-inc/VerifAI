# VerifAI

**VerifAI** is a no-code platform for evaluating the **fairness**, **privacy**, and **accuracy** of machine learning models.  
It helps users analyze and improve their ML models across multiple dimensions — without needing to write code.

---

## 🌟 Features

- **Upload** your ML model and dataset easily.
- **Evaluate** model privacy (membership inference attacks), fairness (group fairness metrics), and utility (train/test accuracies).
- **View Results**:
  - Interactive graphs for Privacy Risks and Fairness Metrics.
  - Compare results **with** and **without Differential Privacy (DP)**.
- **Generate Reports** based on evaluation results.
- **Session Management**: Track evaluations tied to each session.

---

## 🏗️ Tech Stack

| Layer        | Technology                         |
| ------------ | ----------------------------------- |
| Backend      | Django, Django Rest Framework (DRF) |
| Frontend     | React.js                            |
| Database     | SQLite (for development)            |
| ML Evaluation| AIF360, Custom Modules              |
| Deployment   | Docker-ready setup (optional)       |

---

## 📂 Project Structure

```
verifai-backend/
  ├── verifai/
  │   ├── ml_modules/        # Machine Learning logic (training, attacks, etc.)
  │   └── webapp/             # Django app (models, views, commands)
  ├── manage.py
  └── requirements.txt

verifai-frontend/
  ├── public/
  ├── src/
      ├── assets/            # Images, icons
      ├── components/        # Reusable React components
      ├── pages/             # Main pages (Upload, Results, Reports, etc.)
      └── routes/            # App routing
  └── package.json
```

---

## 🚀 Getting Started

### Backend (Django)

```bash
# Go to backend folder
cd verifai-backend

# Create and activate a virtual environment
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start server
python manage.py runserver
```

### Frontend (React)

```bash
# Go to frontend folder
cd verifai-frontend

# Install dependencies
npm install

# Start React dev server
npm start
```

---

## 🔗 API Overview

- `POST /api/upload-model/` - Upload your ML model.
- `POST /api/upload-dataset/` - Upload your dataset.
- `GET /api/store-results/` - Fetch evaluation results (privacy, fairness, accuracy).

---

## 📊 Evaluation Metrics

- **Privacy**: Membership Inference Attack risks per subpopulation.
- **Fairness**:
  - Balanced Accuracy
  - Average Odds Difference
  - Disparate Impact
  - Statistical Parity Difference
  - Equal Opportunity Difference
  - Theil Index
- **Accuracy**: Train/Test overall and per subpopulation.

---

## 🛠️ Notes

- **Without DP** results are evaluated **once** and reused.
- **With DP** results are evaluated **for each** selected ε value (0.1, 1, 5, 10).
- Subpopulations are coded as:
  - UU = Unprivileged Unfavorable
  - UF = Unprivileged Favorable
  - PU = Privileged Unfavorable
  - PF = Privileged Favorable

---

## 🤝 Contributing

Coming soon!

---

## 📜 License

This project is currently private and intended for academic/educational purposes.

---