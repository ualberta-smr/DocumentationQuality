import pandas as pd
from sklearn.metrics import cohen_kappa_score

data = pd.read_csv("pandas.concat_kappa.csv")
y1 = list(data['has_api_sarah'])
y2 = list(data['has_api_afiya'])

has_api_kappa_score = cohen_kappa_score(y1=y1, y2=y2)

print(has_api_kappa_score)

y1 = list(data['discusses_api_sarah'])
y2 = list(data['discusses_api_afiya'])

discusses_api_kappa_score = cohen_kappa_score(y1=y1, y2=y2)

print(discusses_api_kappa_score)
