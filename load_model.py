import pandas as pd
from joblib import load
model1_data = load('model1.joblib')
model2_data = load('model2.joblib')
descriptors_df = pd.read_csv('Descriptors.csv')
best_model1 = model1_data['model']
scaler_model1 = model1_data['scaler']
selected_features_model1 = model1_data['selected_features']
best_model2 = model2_data['model']
scaler_model2 = model2_data['scaler']
selected_features_model2 = model2_data['selected_features']
X_model1 = descriptors_df[selected_features_model1]
X_model2 = descriptors_df[selected_features_model2]
X_model1_scaled = scaler_model1.transform(X_model1)
X_model1_scaled_df = pd.DataFrame(X_model1_scaled, columns=selected_features_model1)
X_model2_scaled = scaler_model2.transform(X_model2)
X_model2_scaled_df = pd.DataFrame(X_model2_scaled, columns=selected_features_model2)
predictions_model1 = best_model1.predict(X_model1_scaled_df)
predictions_model2 = best_model2.predict(X_model2_scaled_df)
print("Predictions using Model1:")
print(predictions_model1)
print("Predictions using Model2:")
print(predictions_model2)