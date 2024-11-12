import streamlit as st
import pandas as pd
import numpy as np

# Criando um DataFrame com Pandas
df = pd.DataFrame({
    'A': np.random.randn(100),
    'B': np.random.randn(100)
})

# Exibindo o DataFrame no Streamlit
st.write("Dados aleatórios:")
st.dataframe(df)

# Visualizando gráficos
st.line_chart(df)