import streamlit as st
import pandas as pd
from io import BytesIO

uploaded_file = st.file_uploader("📁 Envie a base de dados em csv", type=["csv"])
if uploaded_file is None:
    st.warning("Por favor, envie o arquivo base para continuar.")
    st.stop()

df = pd.read_csv(uploaded_file)
st.write(df)

# Função para converter o DataFrame em Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(df)

# Botão de download
st.download_button(
    label="📥 Baixar como Excel",
    data=excel_data,
    file_name="tabela_bi_faturamento.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
