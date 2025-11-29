# Introduction to adding some missing values and duplicate for demo
df_clean = df.copy()
df_clean.loc[1, 'color'] = None #(ask what does it mean)
df_clean.loc[2, 'vin'] = df_clean.loc[0, 'vin']  # make first and last VIN same to demo duplicate, ask What .loc[row, column] means?
display(df_clean)

# Fill missing
print("Fill missing")
display(df_clean.fillna({'color':'unknown'}))

# Drop missing
print('Drop missing')
display(df_clean.dropna())

# Drop duplicates
print("Drop duplicates")
display(df_clean.drop_duplicates(subset=['vin']))#ask what is .drop_duplicates(subset=['vin']) and what if you use inplace=True

# Display data type before conversion
print("Display data type before conversion")
display(df_clean.dtypes)

# Data type conversion
print("Data type conversion")
df_clean['year'] = df_clean['year'].astype(int)
df_clean['registration_date'] = pd.to_datetime(df_clean['registration_date'])
display(df_clean.dtypes)

# String operations
print("String operations")
df_clean['color_upper'] = df_clean['color'].astype(str).str.upper()
display(df_clean[['color','color_upper']])
