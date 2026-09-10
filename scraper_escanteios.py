import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import firebase_admin
from firebase_admin import credentials, firestore

# ==========================================
# 1. CONEXÃO COM O SEU FIREBASE
# ==========================================
# Certifique-se de que o arquivo .json está na mesma pasta deste script
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
colecao_radar = db.collection("jogos_do_dia")

# Função para limpar os jogos antigos antes de subir os novos
def limpar_jogos_antigos():
    docs = colecao_radar.stream()
    for doc in docs:
        doc.reference.delete()
    print("🗑️ Jogos antigos apagados do Firebase.")

# ==========================================
# 2. CONFIGURAÇÃO DO ROBÔ (SELENIUM)
# ==========================================
def iniciar_robo():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Roda invisível (sem abrir a janela)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico, options=chrome_options)
    return navegador

# ==========================================
# 3. LÓGICA DE RASPAGEM (SCRAPING)
# ==========================================
def raspar_dados():
    nav = iniciar_robo()
    print("🌐 Acessando o site de estatísticas...")
    
    # URL de exemplo (substitua pelo site de estatísticas de cantos da sua preferência)
    nav.get("https://www.flashscore.com.br/") 
    time.sleep(5) # Espera a página carregar

    jogos_filtrados = []

    # ⚠️ AQUI É ONDE A MÁGICA ACONTECE
    # Você precisará inspecionar a página do site escolhido para pegar as classes corretas.
    # Exemplo genérico de como o Selenium varre a tela:
    
    try:
        # Encontra todos os blocos de jogos na tela
        # elementos_jogos = nav.find_elements(By.CLASS_NAME, "event__match") 
        
        # Como não temos os seletores reais agora, vamos simular a captura 
        # de jogos que passaram pelo seu filtro mental/algoritmo de 0-10 min:
        print("🔍 Analisando jogos e probabilidades...")
        
        jogos_mockados_encontrados = [
            {"timeA": "Flamengo", "timeB": "Vasco", "probabilidade": 82, "odd_estimada": 1.55, "horario": "20:30"},
            {"timeA": "Palmeiras", "timeB": "São Paulo", "probabilidade": 75, "odd_estimada": 1.60, "horario": "21:00"},
            {"timeA": "Real Madrid", "timeB": "Man City", "probabilidade": 88, "odd_estimada": 1.45, "horario": "16:00"}
        ]
        
        jogos_filtrados = jogos_mockados_encontrados

    except Exception as e:
        print(f"Erro ao raspar dados: {e}")
    finally:
        nav.quit()
        
    return jogos_filtrados

# ==========================================
# 4. UPLOAD PARA O APLICATIVO
# ==========================================
def main():
    print("🚀 Iniciando motor do Radar 0-10 Minutos...")
    
    # 1. Puxa os dados da web
    jogos = raspar_dados()
    
    if len(jogos) > 0:
        # 2. Limpa o radar do dia anterior
        limpar_jogos_antigos()
        
        # 3. Sobe os jogos novos para o app
        for jogo in jogos:
            colecao_radar.add({
                "match": f"{jogo['timeA']} x {jogo['timeB']}",
                "probabilidade": jogo['probabilidade'],
                "odd": jogo['odd_estimada'],
                "horario": jogo['horario'],
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            print(f"✅ Adicionado ao Radar: {jogo['timeA']} x {jogo['timeB']} ({jogo['probabilidade']}%)")
            
        print("🎉 Atualização concluída com sucesso! Seu app já pode ler os dados.")
    else:
        print("⚠️ Nenhum jogo encontrado para hoje.")

if __name__ == "__main__":
    main()
