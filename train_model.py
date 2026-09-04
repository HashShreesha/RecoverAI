import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score


# Load dataset
data = pd.read_csv("data/transactions.csv")

# Features used by the model
features = [
    "amount",
    "payment_method",
    "failure_reason",
    "previous_attempts",
    "customer_successful_payments",
    "customer_failed_payments",
    "hours_since_failure"
]

X = data[features]
y = data["recovered"]


# Categorical and numerical features
categorical_features = [
    "payment_method",
    "failure_reason"
]

numerical_features = [
    "amount",
    "previous_attempts",
    "customer_successful_payments",
    "customer_failed_payments",
    "hours_since_failure"
]


# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# Random Forest model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)


# Complete ML pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# Train
pipeline.fit(X_train, y_train)


# Predictions
predictions = pipeline.predict(X_test)
probabilities = pipeline.predict_proba(X_test)[:, 1]


# Evaluation
accuracy = accuracy_score(y_test, predictions)
auc = roc_auc_score(y_test, probabilities)

print("\n========== RecoverAI ML Model ==========")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")
print(f"Accuracy:         {accuracy:.4f}")
print(f"ROC-AUC:          {auc:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, predictions))


# Save model
joblib.dump(
    pipeline,
    "models/recovery_model.pkl"
)

print("========================================")
print("Model saved to: models/recovery_model.pkl")