import pandas as pd
import gspread
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import textwrap
import re

import yagmail
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

gc = gspread.service_account('credentials.json')
spreadsheet = gc.open_by_key('143TTbbFw9SnAsX6L_8psrGMGzZIFIXrEdlYAlWlDc2o')
worksheet = spreadsheet.worksheet('Respostas ao formulário 1')
rows = worksheet.get_all_values()
header = rows[0]
data = rows[1:]
respostas = pd.DataFrame(data, columns=header)
for x in respostas.columns:
    try:
        respostas[x] = pd.to_numeric(respostas[x])
    except:
        pass
respostas.rename(columns={'Não costumo falar muito': 'Nao_costumo_falar_muito_2'}, inplace=True)
respostas = respostas.head(2)


# Definição das categorias para o gráfico de radar
categories = ['Extroversão', 'Agradabilidade', 'Conscienciosidade', 'Neuroticismo', 'Abertura a Experiências']

# Função para calcular os índices
def model_base(df):
    df['Extroversão'] = (
        20 + df.iloc[:, 13] - df.iloc[:, 19] +
        df.iloc[:, 24] - df.iloc[:, 29] +
        df.iloc[:, 45] - df.iloc[:, 39] +
        df.iloc[:, 44] - df.iloc[:, 48] +
        df.iloc[:, 53] - df.iloc[:, 58]
    )

    df['Agradabilidade'] = (
        14 - df.iloc[:, 15] +
        df.iloc[:, 20] - df.iloc[:, 25] +
        df.iloc[:, 30] - df.iloc[:, 35] +
        df.iloc[:, 40] - df.iloc[:, 14] +
        df.iloc[:, 49] + df.iloc[:, 54] + 
        df.iloc[:, 59]
    )

    df['Conscienciosidade'] = (
        14 + df.iloc[:, 15] -
        df.iloc[:, 21] + df.iloc[:, 26] - df.iloc[:, 31] +
        df.iloc[:, 36] - df.iloc[:, 41] +
        df.iloc[:, 45] - df.iloc[:, 50] +
        df.iloc[:, 55] + df.iloc[:, 60]
    )

    df['Neuroticismo'] = (
        38 - df.iloc[:, 17] + df.iloc[:, 22] -
        df.iloc[:, 27] + df.iloc[:, 32] -
        df.iloc[:, 37] - df.iloc[:, 42] -
        df.iloc[:, 46] - df.iloc[:, 51] -
        df.iloc[:, 56] - df.iloc[:, 61]
    )

    df['Abertura a Experiências'] = (
        8 + df.iloc[:, 18] -
        df.iloc[:, 23] + df.iloc[:, 28] -
        df.iloc[:, 33] + df.iloc[:, 38] -
        df.iloc[:, 43] + df.iloc[:, 47] +
        df.iloc[:, 52] + df.iloc[:, 57] +
        df.iloc[:, 62]
    )
    
    # Tratamento das datas
    df['Em qual ano você iniciou a atuar como corretor de imóveis? (Caso não se aplique, deixe em branco)'] = pd.to_datetime(df['Em qual ano você iniciou a atuar como corretor de imóveis? (Caso não se aplique, deixe em branco)'], errors='coerce', format='%Y')

    current_year = datetime.now().year
    df['Idade'] = (datetime.now() - pd.to_datetime(df['Qual sua data de nascimento?'], format="%d/%m/%Y")) // pd.Timedelta(days=365.25)

    df['Tempo de Carreira'] = current_year - df['Em qual ano você iniciou a atuar como corretor de imóveis? (Caso não se aplique, deixe em branco)'].dt.year
    df['Tempo de Carreira'] = df['Tempo de Carreira'].fillna('Não Informado')
    df['Tempo de Carreira'] = df['Tempo de Carreira'].apply(format_years)

    # Novo código para substituir valores NaN ou NaT por 'Não Informado'
    # df['Em qual ano você iniciou a atuar como corretor de imóveis? (Caso não se aplique, deixe em branco)'] = df['Em qual ano você iniciou a atuar como corretor de imóveis? (Caso não se aplique, deixe em branco)'].fillna('Não Informado')
    df['Em qual ano você iniciou a atuar como corretor de imóveis? (Caso não se aplique, deixe em branco)'] = df['Em qual ano você iniciou a atuar como corretor de imóveis? (Caso não se aplique, deixe em branco)'].apply(lambda x: x.year if pd.notnull(x) else 'Não Informado')
    return pd.DataFrame(df)

def format_years(years):
    if years == 'Não Informado':
        return years
    
    years = int(years)
    if years == 1:
        return f"{years} ano"
    elif years == 0:
        return "Menos de 1 ano"
    else:
        return f"{years} anos"

respostas = model_base(respostas)

# Função para criar o gráfico de radar
def radar_chart(categories, values, title):
    
    # Number of variables
    num_vars = len(categories)

    # Create a radar chart with num_vars axes
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False).tolist()

    # Rotate plot so that the first axis is at the top
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels
    plt.xticks(theta, categories)

    # Draw ylabels with multiple circles
    ax.set_rscale('log')
    circles = [5, 10, 20, 40]#, 60, 100]  # Define os valores dos círculos
    plt.yticks(circles, [str(val) for val in circles], color="grey", size=7)
    plt.ylim(0, 100)

    # Plot data
    values += values[:1]  # Adiciona o primeiro valor ao final para fechar o polígono
    ax.plot(theta + theta[:1], values, color='blue', linestyle='solid', linewidth=1, label=title)
    ax.fill(theta + theta[:1], values, color='blue', alpha=0.25)

    # Add a title
    plt.title(title, size=12, color='black', y=1.1)

    # Annotate values on the chart with larger font size
    for i in range(num_vars):
        plt.text(theta[i], values[i], str(values[i]), color='blue', fontsize=12)  # Ajuste o tamanho da fonte aqui

    # Show legend with values and their classifications
    legend_labels = ["""Baixo = 0 a 10\nModerado = 11 a 29\nAlto = 30 a 40"""]
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=5)]
    plt.legend(handles, legend_labels, loc='lower center', bbox_to_anchor=(1.1, 0.1), fontsize='small')#, bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize='small')

    filename = "radar_chart.png"
    plt.savefig(filename, format='png', bbox_inches='tight')
    plt.close()

    return filename

max_width = 500
max_height = 150
margem_abnt = 2.54 * 2  # 2.54 cm para cada lado, para cima e para baixo

def add_header(c, logo_path):
    logo_width, logo_height = ImageReader(logo_path).getSize()  # Obtém a largura e altura da imagem

    # Limites máximos para a largura e altura da logo
    max_width = 150
    max_height = 60
    margem_abnt = 2.54 * 2  # 2.54 cm para cada lado, para cima e para baixo

    # Calcula a proporção para redimensionar a imagem
    width_ratio = max_width / logo_width
    height_ratio = max_height / logo_height
    ratio = min(width_ratio, height_ratio)

    # Redimensiona a imagem mantendo a proporção original
    new_width = logo_width * ratio
    new_height = logo_height * ratio

    # Posicionamento horizontal centralizado
    x = (letter[0] - new_width) / 2

    # Posição vertical mantendo margem ABNT
    y = letter[1] - margem_abnt - new_height - 20

    # Adiciona a imagem redimensionada ao PDF centralizada horizontalmente
    c.drawImage(logo_path, x, y, width=new_width, height=new_height, mask='auto')
    

# Função para criar a tabela com informações do corretor
def add_information_table(c, respondent):
    x_offset = 100
    y_offset = 700
    line_height = 20

    title = "Assessment Comportamental"
    c.setFont("Helvetica-Bold", 14)
    title_width = c.stringWidth(title, "Helvetica-Bold", 14)
    title_position_x = (letter[0] - title_width) / 2  # Posição horizontal centralizada
    c.drawString(title_position_x, y_offset, title)
    
    
    # c.setFont("Helvetica-Bold", 14)
    # c.drawString(x_offset, y_offset, "Assessment Comportamental")

    # Nome centralizado na linha, em negrito e com fonte maior
    name = respondent['Qual o seu nome completo?']
    c.setFont("Helvetica-Bold", 13)
    name_width = c.stringWidth(name, "Helvetica-Bold", 14)
    name_position_x = (letter[0] - name_width) / 2  # Posição horizontal centralizada
    c.drawString(name_position_x, y_offset - 30, name)

    # Ajuste do y_offset para começar abaixo do nome
    y_offset -= 80

    # Títulos e respectivos valores para a tabela
    titles = [
        'Gênero:',
        'Data de Nascimento:',
        'Idade:',
        'Localidade:',
        'Já atua como Corretor?:',
        'Possui TTI?:',
        # 'Ano que iniciou como Corretor:',
        'Tempo de Carreira como Corretor:',
        'Em busca de Oportunidades?:'
    ]

    values = [
        respondent['Com qual gênero você se identifica?'],
        respondent['Qual sua data de nascimento?'],
        respondent['Idade'],
        respondent['Onde você mora/atua? (Cidade/Estado)'],
        respondent['Você já é corretor de imóveis?'],
        respondent['Você já tem o certificado de "Técnico em Transações Imobiliárias (TTI)"?'],
        # respondent['Em qual ano você iniciou a atuar como corretor de imóveis? (Caso não se aplique, deixe em branco)'],
        respondent['Tempo de Carreira'],
        respondent['Você está buscando oportunidades em imobiliárias?']
    ]

    # Desenhando a tabela com os títulos e valores
    for title, value in zip(titles, values):
        if title != 'Qual o seu nome completo?':  # Evita estilizar o nome
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x_offset, y_offset, title)

            c.setFont("Helvetica", 10)
            c.drawString(x_offset + 200, y_offset, str(value))

            y_offset -= line_height + 5  # Aumenta o espaçamento entre título e valor

        else:  # Mantém o nome sem formatação
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x_offset, y_offset, title)

            c.setFont("Helvetica", 10)
            c.drawString(x_offset + 200, y_offset, str(value))

            y_offset -= line_height
            
# Função para criar o PDF
def create_pdf_and_send_email(logo_path, data_frame, output_folder):
    current_year = datetime.now().year  # Obtendo o ano atual
    yag = yagmail.SMTP('assessment@meit.com.br', 'AsE!@#2023')  

    for index, row in data_frame.iterrows():
        c = canvas.Canvas(f"{output_folder}/assessment_{row['Qual o seu nome completo?']}.pdf", pagesize=letter)

        add_header(c, logo_path)
        add_information_table(c, row)  # Passa apenas a linha dos dados do respondente

        radar_path = radar_chart(categories, [row['Extroversão'], row['Agradabilidade'], row['Conscienciosidade'], row['Neuroticismo'], row['Abertura a Experiências']], 'Índices de Personalidade')
        c.drawImage(radar_path, 100, 70, width=400, height=310)

        c.showPage()  # Adiciona uma nova página

         # Adicionando os textos explicativos na nova página
        y_text = 700  # Posição inicial do texto

        text0 = "O que esse teste significa?;"
        text1 = "Extroversão:;A extroversão pode ser relevante para corretores de imóveis, uma vez que envolve a capacidade de se comunicar efetivamente com os clientes, colegas e outros profissionais do setor. Corretores mais extrovertidos podem ser mais propensos a estabelecer relacionamentos e redes de contatos, o que é importante para o sucesso nessa profissão."
        text2 = "Agradabilidade:;A Agradabilidade pode ser valiosa para corretores de imóveis no que diz respeito à capacidade de construir relacionamentos duradouros com os clientes, se compassivo e compreensivo com suas necessidades e ser cooperativo na negociação de transações imobiliárias."
        text3 = "Conscienciosidade:;A Conscienciosidade é fundamental para garantir que todos os detalhes das transações imobiliárias sejam tratados com precisão e responsabilidade. Corretores de imóveis precisam ser organizados, responsáveis e disciplinados para cumprir prazos e garantir que tudo ocorra sem problemas."
        text4 = "Neuroticismo (ou Estabilidade Emocional):;Ter estabilidade emocional é importante para lidar com as pressões e desafios que podem surgir na indústria imobiliária. Corretores emocionalmente estáveis são mais capazes de lidar com o estresse e manter a calma em situações complexas."
        text5 = "Abertura à Experiências:;A abertura à experiências pode ser benéfica para corretores de imóveis, pois eles podem precisar ser criativos ao apresentar imóveis de forma atraente, bem como se adaptar a novas tendências e mudanças no mercado imobiliário."

        for text in [text0, text1, text2, text3, text4, text5]:
            text_split = text.split(';', 1)
            title = text_split[0].strip()
            content = text_split[1].strip()

            c.setFont("Helvetica-Bold", 10)
            c.drawString(100, y_text, title)  # Título no início do parágrafo
            y_text -= 15  # Espaçamento entre os títulos e o conteúdo

            wrapped_text = textwrap.fill(content, width=80)
            lines = wrapped_text.split('\n')
            for line in lines:
                c.setFont("Helvetica", 10)
                c.drawString(120, y_text, line.strip())
                y_text -= 15  # Espaçamento entre as linhas

            y_text -= 15  # Espaçamento entre os parágrafos

        c.save()

        # Envio de e-mail com mensagem personalizada
        email_corretor = "allansoares@id.uff.br"#row['Endereço de e-mail']  # Substitua com o nome da coluna que contém os e-mails dos corretores
        #mensagem_corretor = f"Olá, <b>{row['Qual o seu nome completo?'].split()[0]}</b>.\n\nObrigado por participar do nosso Assessment Comportamental!\n Segue anexo o seu relatório.\n\nAtenciosamente,\n<b>Meit</b>"
        mensagem_corretor = f"Olá, <b>{row['Qual o seu nome completo?'].split()[0]}</b>.\n\nEsperamos que esteja tudo bem!\n\nÉ com grande prazer que compartilhamos o resultado da sua avaliação de personalidade conforme o teste realizado. 🥳\n\nAnexamos um arquivo PDF contendo informações detalhadas sobre seus traços de personalidade, pontos fortes e possíveis áreas de aprimoramento. \n\nRecomendamos que reserve um momento tranquilo para revisar seu perfil com atenção.\n\nFique à vontade para compartilhar suas impressões ou dúvidas após a análise do seu perfil.\n\n\nAtenciosamente,\n<b>Equipe Meit</b>"
        anexo = f"{output_folder}/assessment_{row['Qual o seu nome completo?']}.pdf"
        
        email_terraz = "andrelima@terraz.com.br"
        mensagem_terraz = f"Olá, André. \n\nO Corretor <b>{row['Qual o seu nome completo?']}</b> acaba de  participar do nosso Assessment Comportamental!\n Segue o seu relatório, anexo.\n\nAtenciosamente,\n<b>Meit</b>"
        # Enviar e-mail com anexo e mensagem personalizada
        yag.send(email_corretor, 'Resultado do seu teste de perfil Big Five', mensagem_corretor, attachments=anexo)
        yag.send(email_terraz, 'Resultado do seu teste de perfil Big Five', mensagem_terraz, attachments=anexo)
    yag.close()

# Chamada da função para criar os PDFs individuais e enviar por e-mail
logo_file_path = 'logo\\logo.png'  # Caminho para o arquivo de imagem da logo
output_folder = 'reports'  # Pasta de saída para os PDFs
create_pdf_and_send_email(logo_file_path, respostas, output_folder)
