# Handle class imbalance using SMOTE (Synthetic Minority Over-sampling Technique)
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import StandardScaler
from main import load_and_preprocess

def get_train_test_split(df):

    feature_cols = ['latitude', 'longitude', 'depth', 'mag', 'nst', 'gap', 'rms',
                    'close_event', 'largest_nearby_earthquake',
                    'year', 'month', 'day', 'dayofweek'] + \
                   [col for col in df.columns if col.startswith('magType_')]

    target_col = 'target'

    # Split the data into training and testing sets based on time
    # We'll use data before 2019 for training and data from 2019 onwards for testing
    cutoff_date = '2019-01-01'
    train_df = df[df['time'] < cutoff_date]
    test_df = df[df['time'] >= cutoff_date]

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]

    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    return X_train, y_train, X_test, y_test


def main():
    data = load_and_preprocess("resources/90_25_turkey.csv")  # Preprocess the data

    X_train, y_train, X_test, y_test = get_train_test_split(data)

    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_resampled)
    X_test_scaled = scaler.transform(X_test)

    # 1. Logistic Regression
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

    logreg = LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000)
    logreg.fit(X_train_scaled, y_train_resampled)

    y_pred_logreg = logreg.predict(X_test_scaled)
    y_pred_proba_logreg = logreg.predict_proba(X_test_scaled)[:, 1]

    print("Logistic Regression Evaluation:")
    print(confusion_matrix(y_test, y_pred_logreg))
    print(classification_report(y_test, y_pred_logreg))
    print('ROC AUC Score:', roc_auc_score(y_test, y_pred_proba_logreg))

    # 2. Random Forest Classifier
    from sklearn.ensemble import RandomForestClassifier

    rf = RandomForestClassifier(class_weight='balanced', random_state=42)
    rf.fit(X_train_resampled, y_train_resampled)

    y_pred_rf = rf.predict(X_test)
    y_pred_proba_rf = rf.predict_proba(X_test)[:, 1]

    print("Random Forest Evaluation:")
    print(confusion_matrix(y_test, y_pred_rf))
    print(classification_report(y_test, y_pred_rf))
    print('ROC AUC Score:', roc_auc_score(y_test, y_pred_proba_rf))

    # 3. XGBoost Classifier
    import xgboost as xgb

    xgb_clf = xgb.XGBClassifier(scale_pos_weight=len(y_train_resampled[y_train_resampled == 0]) / len(
        y_train_resampled[y_train_resampled == 1]),
                                random_state=42,
                                use_label_encoder=False,
                                eval_metric='logloss')
    xgb_clf.fit(X_train_resampled, y_train_resampled)

    y_pred_xgb = xgb_clf.predict(X_test)
    y_pred_proba_xgb = xgb_clf.predict_proba(X_test)[:, 1]

    print("XGBoost Evaluation:")
    print(confusion_matrix(y_test, y_pred_xgb))
    print(classification_report(y_test, y_pred_xgb))
    print('ROC AUC Score:', roc_auc_score(y_test, y_pred_proba_xgb))


if __name__ == "__main__":
    main()
