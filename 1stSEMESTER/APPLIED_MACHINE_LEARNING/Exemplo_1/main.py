import pandas as pd
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from slearn.metrics import *
import matplotlib.pyplot as plt

df = pd.read_csv(
    "SMSSpamCollection",
    sep="\t",
    header=None,
    names=["label", "message"]
)

print(df.head())
print()
print(df.shape)
print()
print(df["label"].value_counts())

df["label"] = df["label"].map({
    "ham": 0,
    "spam": 1
})

print(df.head())

x = df["message"]
y = df["label"]

x_train, X_test, y_train, y_test = train_test_split(
    x,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

print("Training messages: ", len(X_train))
print("Test messages: ", len(X_test))

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english"
)

X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

print("Training matrix shape: ", X_train_vectorized.shape)
print("Test matrix shape: ", X_test_vectorized.shape)

def evaluate_model(model_name, y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)

    tn, fp, fn, tp = cm.ravel()

    accuracy = accuracy_score(y_true, y_pred)

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    specify = tn / (tn + fp)

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    print(f"\n{model_name}")
    print("-" * len(model_name))
    print(f"Accuracy:       {accuracy:.3f}")
    print(f"Precision:      {precision:.3f}")
    print(f"Recall:         {recall:.3f}")
    print(f"Specificity:    {specify:.3f}")
    print(f"F1-score:       {f1:.3f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            target_names=["Not Spam", "Spam"],
            zero_division=0
        )
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Not Spam", "Spam"]
    )

    display.plot(cmap="Blues")
    plt.title(f"{model_name} - Confusion Matrix")
    plt.show()

    return {
        "model": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "specificity": specify,
        "f1": f1
    }