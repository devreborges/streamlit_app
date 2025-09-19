import streamlit as st
import pandas as pd
from io import BytesIO
import os

# Upload do arquivo CSV
uploaded_file = st.file_uploader("📁 Envie a base de dados em CSV", type=["csv"])
if uploaded_file is None:
    st.warning("Por favor, envie o arquivo base para continuar.")
    st.stop()

# Leitura do CSV
df = pd.read_csv(uploaded_file)
st.write(df)

# Função para converter o DataFrame em Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    output.seek(0)
    return output

# Gerar dados Excel
excel_data = to_excel(df)

# Extrair nome do arquivo sem extensão
file_name_without_ext = os.path.splitext(uploaded_file.name)[0]

# Botão de download
st.download_button(
    label="📥 Baixar como Excel",
    data=excel_data,
    file_name=f"{file_name_without_ext}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
