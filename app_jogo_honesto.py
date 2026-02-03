import random
import pandas as pd
import streamlit as st
import time
import altair as alt  # ✅ Usaremos Altair para visualização

st.set_page_config(page_title="Simulação de Jogo com Dado 🐸🐋🐱🐮", layout="centered")

st.title("🐸🐋🎲 CassinoMAT 🎲🐱🐮")

# Entrada de quantidade de jogadores
quantidade_de_jogadores = st.number_input(
    "Quantos jogadores participarão?",
    min_value=5,
    max_value=20,
    value=5,
    step=1
)

# Inicialização de jogadores
jogadores = [f'Jogador {i}' for i in range(1, quantidade_de_jogadores + 1)]

# Configurações iniciais
pontuacao_inicial = 10
saldo_banca = 100
rodadas = 10

# Dado com emojis
dado_d4 = ['🐸', '🐋', '🐱', '🐮']

# Criando o DataFrame inicial
df_jogadores = pd.DataFrame({
    'Jogadores': jogadores,
    'Pontuação': pontuacao_inicial
})

# Botão para iniciar simulação
if st.button("🚀 Iniciar Simulação"):
    st.write("### 🎬 Iniciando a Simulação...")
    time.sleep(1)
    st.write("### Resultado das Rodadas")

    historico = []

    for k in range(1, rodadas + 1):
        st.markdown(f"## 🌀 Rodada {k}")
        escolhas_da_rodada = []

        # Cada jogador faz uma escolha aleatória
        for i in df_jogadores.index:
            escolha = random.choice(dado_d4)
            escolhas_da_rodada.append(escolha)
            st.write(f"{df_jogadores.loc[i, 'Jogadores']} escolheu {escolha}")

        # Espaço reservado para o dado rolando
        dice_box = st.empty()

        # Animação de rolagem do dado 🎲
        for _ in range(12):
            face = random.choice(dado_d4)
            dice_box.markdown(f"<h1 style='text-align:center; font-size:60px;'>{face}</h1>", unsafe_allow_html=True)
            time.sleep(0.6)

        # Rolagem real da rodada
        rolagem_aleatoria = random.choice(dado_d4)
        dice_box.markdown(f"<h1 style='text-align:center; font-size:70px;'>🎯 {rolagem_aleatoria}</h1>", unsafe_allow_html=True)
        time.sleep(1)

        # Resultado da rodada
        vencedores = []
        for index, escolha in enumerate(escolhas_da_rodada):
            if escolha == rolagem_aleatoria:
                df_jogadores.loc[index, 'Pontuação'] += 2
                saldo_banca -= 1
                vencedores.append(df_jogadores.loc[index, 'Jogadores'])
            else:
                df_jogadores.loc[index, 'Pontuação'] -= 1
                saldo_banca += 1

        # Mostra resultado da rodada
        if vencedores:
            st.success(f"🏆 Vencedores da rodada: {', '.join(vencedores)}")
        else:
            st.warning("😶 Nenhum jogador acertou a rolagem dessa rodada.")

        # Atualiza tabela e saldo
        st.dataframe(df_jogadores, use_container_width=True)
        st.info(f"💰 Saldo da banca: {saldo_banca}")
        st.divider()

        # Guarda resultados no histórico
        historico.append({
            "Rodada": k,
            "Face sorteada": rolagem_aleatoria,
            "Vencedores": ', '.join(vencedores) if vencedores else "Nenhum",
            "Saldo da banca": saldo_banca
        })

        # Delay suave antes da próxima rodada
        time.sleep(2)

    # Resumo final
    st.subheader("🏁 Resultado Final")
    st.dataframe(df_jogadores.sort_values(by="Pontuação", ascending=False), use_container_width=True)
    st.success(f"💰 Saldo final da banca: {saldo_banca}")

    # Histórico completo das rodadas
    st.markdown("### 📜 Histórico das Rodadas")
    df_historico = pd.DataFrame(historico)
    st.dataframe(df_historico, use_container_width=True)

    # 📊 Gráfico de evolução do saldo da banca
    st.markdown("### 📈 Evolução do Saldo da Banca ao Longo das Rodadas")

    # Determina o valor máximo do eixo Y de forma dinâmica
    max_saldo = df_historico["Saldo da banca"].max() + 1

    chart = (
        alt.Chart(df_historico)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Rodada:Q",
                title="Rodada",
                axis=alt.Axis(labelAngle=0)  # 👈 mantém os números na horizontal
            ),
            y=alt.Y(
                "Saldo da banca:Q",
                title="Saldo da Banca",
                scale=alt.Scale(domain=[100, max_saldo]),  # mínimo = 100
                axis=alt.Axis(tickMinStep=1)
            ),
            tooltip=["Rodada", "Saldo da banca"]
        )
        .properties(width=700, height=400)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)


else:
    st.info("🕹️ Configure o número de jogadores e clique em **Iniciar Simulação** para começar o jogo.")
    
