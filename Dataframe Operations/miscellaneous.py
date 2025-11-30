display(df.describe(include='all'))
display(df.corr(numeric_only=True))

# Apply example
df['price_discounted'] = df['price'].apply(lambda x: x * 0.9)
display(df[['price','price_discounted']])

# Time series: extract year from registration_date
df['reg_year'] = df['registration_date'].dt.year
display(df[['registration_date','reg_year']])