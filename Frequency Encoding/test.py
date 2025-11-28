import pandas as pd

data = {'color': ['red', 'green', 'blue', 'red', 'green']}
df = pd.DataFrame(data)

freq = df['color'].value_counts(normalize=True)

df['color_freq'] = df['color'].map(freq)

df = df.drop('color', axis=1)

print(df)
