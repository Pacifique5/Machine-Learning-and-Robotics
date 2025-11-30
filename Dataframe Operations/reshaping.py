melted = pd.melt(df, id_vars=['vin','brand'], value_vars=['color','engine_type'], var_name='attribute', value_name='value')
display(melted)

pivoted = df.pivot_table(values='price', index='brand')
display(pivoted)

stacked = df[['brand','price']].stack()
display(stacked)
unstacked = stacked.unstack()
display(unstacked)