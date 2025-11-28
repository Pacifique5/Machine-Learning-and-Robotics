import pandas as pd

data = {
    'color':["red","red", "red", "blue", "green"],
    'size':["Small","Medium","Large", "Large", "Large"]
}

df = pd.DataFrame(data)

one_hot_encoded_df = pd.get_dummies(df, columns=['color', 'size'])


# one_hot_encoded_df = one_hot_encoded_df.astype(int)

print(one_hot_encoded_df)