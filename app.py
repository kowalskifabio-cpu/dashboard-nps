st.write("---")
    
    # Gráficos de Rosca (Indicadores) - CORRIGIDO COM KEY ÚNICA
    st.subheader("🎯 Desempenho por Indicador")
    cols = st.columns(5)
    labels = ["Clareza", "Prazos", "Comunicação", "Atendimento", "Custo"]
    keys = ['clareza', 'prazos', 'comunicacao', 'atendimento', 'custo']

    for i, col_name in enumerate(keys):
        with cols[i]:
            # Pega a média da coluna
            nota = df[col_name].mean()
            
            # Cria o gráfico de rosca
            fig = px.pie(
                values=[nota, 10-nota], 
                names=['Nota', ''],
                hole=0.7, 
                color_discrete_sequence=['#0E3A5D', '#E9ECEF']
            )
            fig.update_traces(textinfo='none')
            fig.update_layout(showlegend=False, height=180, margin=dict(l=10, r=10, t=10, b=10))
            
            # O SEGREDO ESTÁ AQUI: Adicionei 'key=f"chart_{col_name}"' para cada gráfico ser único
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{col_name}")
            
            # Texto abaixo do gráfico
            st.markdown(f"<center><b>{labels[i]}</b><br><span style='font-size:20px'>{nota:.1f}</span></center>", unsafe_allow_html=True)

    st.write("---")
