import random
import time
from collections import Counter

import pandas as pd
import streamlit as st
import altair as alt

# ----------------------------------
# Configuração da página
# ----------------------------------
st.set_page_config(
    page_title="CassinoMAT FRAUDADO 🎲🧠",
    layout="centered"
)

st.title("🎲 CassinoMAT – Modo FRAUDADO 🧠🐍🐒🦁🦒")
st.caption("Simulação com dado viciado: a banca sempre tenta ganhar")

# ----------------------------------
# Entradas do usuário
# ----------------------------------
quantidade_de_jogadores = st.number_input(
    "Quantidade de jogadores",
    min_value=3,
    max_value=20,
    value=5,
    step=1
)

rodadas = st.slider(
    "Quantidade de rodadas",
    min_value=5,
    max_value=50,
    value=20,
    step=5
)

# ----------------------------------
# Inicialização
# ----------------------------------
nomes_jogadores = [f"Jogador {i}" for i in range(1, quantidade_de_jogadores + 1)]

pontuacao_inicial = 20
saldo_banca = 100

dado_d4 = ['🐍', '🐒', '🦁', '🦒']

# DataFrame de jogadores

df_jogadores = pd.DataFrame({
    'Jogadores': nomes_jogadores,
    'Pontuação': [pontuacao_inicial] * quantidade_de_jogadores
})

# ----------------------------------
# Botão de início
# ----------------------------------
if st.button("🚀 Iniciar Simulação FRAUDADA"):

    st.markdown("## 🎬 Iniciando o jogo...")
    time.sleep(1)

    historico = []

    for k in range(1, rodadas + 1):
        st.markdown(f"## 🌀 Rodada {k}")

        escolhas_da_rodada = []

        # Jogadores escolhem
        for i in df_jogadores.index:
            escolha = random.choice(dado_d4)
            escolhas_da_rodada.append(escolha)
            st.write(f"{df_jogadores.loc[i, 'Jogadores']} escolheu {escolha}")

        # Caixa da animação do dado
        dice_box = st.empty()

        # Animação
        for _ in range(10):
            face = random.choice(dado_d4)
            dice_box.markdown(
                f"<h1 style='text-align:center; font-size:60px;'>{face}</h1>",
                unsafe_allow_html=True
            )
            time.sleep(0.4)

        # -------------------------------
        # LÓGICA FRAUDADA
        # -------------------------------
        cont = Counter(escolhas_da_rodada)
        ausentes = [val for val in dado_d4 if val not in cont]

        if ausentes:
            rolagem_aleatoria = random.choice(ausentes)
            st.warning(f"⚠️ Valores ausentes: {ausentes}")
            st.info(f"🧠 A banca escolheu {rolagem_aleatoria} (ninguém escolheu)")
        else:
            menor_freq = min(cont.values())
            candidatos = [val for val, freq in cont.items() if freq == menor_freq]
            rolagem_aleatoria = random.choice(candidatos)
            st.info(f"📊 Frequências: {dict(cont)}")
            st.warning(f"🧠 A banca escolheu {rolagem_aleatoria} (menor frequência)")

        # Resultado final da rolagem
        dice_box.markdown(
            f"<h1 style='text-align:center; font-size:70px;'>🎯 {rolagem_aleatoria}</h1>",
            unsafe_allow_html=True
        )
        time.sleep(1)

        # Atualiza pontuação
        vencedores = []

        for index, escolha in enumerate(escolhas_da_rodada):
            if escolha == rolagem_aleatoria:
                df_jogadores.loc[index, 'Pontuação'] += 3
                saldo_banca -= 4
                vencedores.append(df_jogadores.loc[index, 'Jogadores'])
            else:
                df_jogadores.loc[index, 'Pontuação'] -= 1
                saldo_banca += 1

        # Feedback
        if vencedores:
            st.success(f"🏆 Vencedores: {', '.join(vencedores)}")
        else:
            st.error("💀 Ninguém venceu — banca perfeita!")

        st.dataframe(df_jogadores, use_container_width=True)
        st.info(f"💰 Saldo da banca: {saldo_banca}")
        st.divider()

        historico.append({
            'Rodada': k,
            'Face escolhida pela banca': rolagem_aleatoria,
            'Saldo da banca': saldo_banca
        })

        time.sleep(1.5)

    # ----------------------------------
    # Resultado final
    # ----------------------------------
    st.subheader("🏁 Resultado Final")
    st.dataframe(
        df_jogadores.sort_values(by='Pontuação', ascending=False),
        use_container_width=True
    )

    st.success(f"💰 Saldo final da banca: {saldo_banca}")

    # ----------------------------------
    # Gráfico do saldo da banca
    # ----------------------------------
    df_hist = pd.DataFrame(historico)

    st.markdown("### 📈 Evolução do Saldo da Banca")

    chart = (
        alt.Chart(df_hist)
        .mark_line(point=True)
        .encode(
            x=alt.X('Rodada:Q', title='Rodada'),
            y=alt.Y('Saldo da banca:Q', title='Saldo da Banca'),
            tooltip=['Rodada', 'Saldo da banca']
        )
        .properties(height=400)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

else:
    st.info("Configure os parâmetros e clique em **Iniciar Simulação FRAUDADA**")
