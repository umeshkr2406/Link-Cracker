import pandas as pd, joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from features import extract

df = pd.read_csv("data/urls.csv").dropna().drop_duplicates("url")
X, y = [extract(u) for u in df["url"]], df["label"].values
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
best, best_acc = None, -1
for name, m in {"LogisticRegression": LogisticRegression(max_iter=3000),
                "RandomForest": RandomForestClassifier(n_estimators=200, random_state=42)}.items():
    m.fit(Xtr, ytr); pred = m.predict(Xte); acc = (pred == yte).mean()
    print(f"\n=== {name} | accuracy {acc:.4f} ===")
    print(classification_report(yte, pred, target_names=["legit","phishing"]))
    print("Confusion matrix:\n", confusion_matrix(yte, pred))
    if acc > best_acc: best, best_acc = (name, m), acc
joblib.dump(best[1], "model.joblib"); print("\nSaved best model:", best[0])