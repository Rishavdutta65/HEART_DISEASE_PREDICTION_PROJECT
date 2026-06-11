import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

base_dir = os.path.dirname(__file__)
# Use relative path from backend/ to the root directory
csv_path = os.path.join(base_dir, "..", "Heart_disease_cleveland_new.csv")
data = pd.read_csv(csv_path)
data = data.dropna()

X = data.drop(["target"], axis=1)
y = data["target"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)

def predict(data_input):
    df_input = pd.DataFrame([data_input], columns=X.columns)
    data_scaled = scaler.transform(df_input)
    result = model.predict(data_scaled)[0]
    prob = model.predict_proba(data_scaled)[0][1]
    importances = dict(zip(X.columns, model.feature_importances_))
    return int(result), float(accuracy), float(prob), {k: float(v) for k, v in importances.items()}