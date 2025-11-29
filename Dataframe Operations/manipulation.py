# Add new column
df['discount'] = df['price'] *0.75
df['age'] = 2025 - df['year']
display(df)

# Update a cell
df.at[0, 'status'] = 'sold'  # update by index label
display(df.loc[0])

# Rename columns
df.rename(columns={'manufacturer':'brand','discount':'new_price'}, inplace=True)
display(df)

# Delete column
df = df.drop(columns=['new_price'])
display(df)