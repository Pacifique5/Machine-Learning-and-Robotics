from sklearn.preprocessing import LabelEncoder

data = ["small", "medium", "large", "small", "large"]

label_encoder = LabelEncoder()

encoded_data = label_encoder.fit_transform(data)

print(encoded_data)
