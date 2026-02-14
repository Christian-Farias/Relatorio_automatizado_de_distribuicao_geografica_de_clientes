import pandas as pd
import matplotlib.pyplot as plt
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
import os
load_dotenv()

# Carregar base de dados
df = pd.read_csv("data/olist_customers_dataset.csv")
print("Base carregada com sucesso!")

# Metricas
total_clientes = df["customer_unique_id"].nunique()

clientes_por_estado = (
    df.groupby("customer_state")["customer_unique_id"]
    .nunique()
    .sort_values(ascending=False)
)

top5_estados = clientes_por_estado.head(5)
percentual_top5 = (top5_estados.sum() / total_clientes) * 100


estado_top = clientes_por_estado.idxmax()
clientes_estado_top = clientes_por_estado.max()
percentual_estado_top = (clientes_estado_top / total_clientes) * 100


# Exportar para Excel
arquivo_excel = "analise_clientes_olist.xlsx"
clientes_por_estado.to_excel(arquivo_excel)

print("Planilha exportada!")

# Gerar Gráfico
plt.style.use("seaborn-v0_8-whitegrid")
plt.figure(figsize=(10, 6))

top5_estados.plot(kind="bar")

plt.title("Top 5 Estados com Maior Número de Clientes", fontsize=14, fontweight="bold")
plt.ylabel("Número de Clientes")
plt.xlabel("Estado")

plt.xticks(rotation=0)

for i, value in enumerate(top5_estados):
    plt.text(i, value, f"{value:,}", ha='center', va='bottom')

plt.tight_layout()

grafico_png = "grafico_clientes_estado.png"
plt.savefig(grafico_png)
plt.close()

print("Gráfico gerado!")

# Criar mensagem do email 
from datetime import datetime
data_hoje = datetime.now().strftime("%Y-%m-%d")

top5_html = top5_estados.reset_index()
top5_html.columns = ["Estado", "Clientes"]
top5_html = top5_html.to_html(index=False)

Email_remetente = "christianfariasdc@gmail.com"
SENHA = os.getenv("EMAIL_PASSWORD")
Email_destinatario = "christianfariasdeoliveira@alu.ufc.br"

msg = EmailMessage()
msg["Subject"] = "Relatório da Distribuição Geográfica de Clientes"
msg["From"] = Email_remetente
msg["To"] = Email_destinatario
msg.set_content("Seu cliente de email não suporta HTML.")


msg.add_alternative(f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
    
    <div style="max-width: 600px; background: white; padding: 20px; border-radius: 8px;">
      
      <h2 style="color: #2c3e50;">📊 Relatório da Distribuição Geográfica – Clientes Olist Store</h2>
      <p style="color: #7f8c8d;">Data de geração: {data_hoje}</p>
      
      <hr>

      <h3 style="color: #34495e;">Visão Geral</h3>
      <p><strong>Total de Clientes Únicos:</strong> {total_clientes:,}</p>

      <h3 style="color: #34495e;">🏆 Estado Líder</h3>
      <p><strong>{estado_top}</strong> com {clientes_estado_top:,} clientes</p>

      <h3 style="color: #34495e;">📍 Top 5 Estados</h3>
      {top5_html}

      <p>Os 5 principais estados concentram aproximadamente <strong>{percentual_top5:.2f}%</strong> da base total de clientes, indicando forte concentração regional.</p>

      <p>O estado líder (<strong>{estado_top}</strong>) representa sozinho cerca de <strong>{percentual_estado_top:.2f}%</strong> da base total.</p>

      <p style="margin-top:20px;">
        📎 Em anexo: planilha detalhada e gráfico analítico.
      </p>

      <hr>

      <p style="font-size: 12px; color: #95a5a6;">
        Christian Farias de Oliveira - Analista de Dados<br>
        Bacharel em Ciências Econômicas - UFC Campus Sobral
      </p>

    </div>
    
  </body>
</html>
""", subtype="html")

# Anexar Excel
with open(arquivo_excel, "rb") as f:
    msg.add_attachment(
        f.read(),
        maintype="application",
        subtype="octet-stream",
        filename="analise_clientes_olist.xlsx",
    )

# Anexar Gráfico
with open(grafico_png, "rb") as f:
    msg.add_attachment(
        f.read(),
        maintype="image",
        subtype="png",
        filename=grafico_png,
    )

# Enviar email
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(Email_remetente, SENHA)
    smtp.send_message(msg)

print("Email enviado com sucesso!")
