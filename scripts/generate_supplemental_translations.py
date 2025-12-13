
import json
import re
import os

INPUT_FILE = 'Data/ui_text_jp_filtered.json'
OUTPUT_FILE = 'Data/ui_text_pt_supplemental.json'

MANUAL_TRANSLATIONS = {
    "残念ながら私も持っていません": "Infelizmente, eu também não tenho.",
    "初版　画像なし": "Primeira Edição - Sem Imagem",
    "初版 画像なし": "Primeira Edição - Sem Imagem",
    "原本が手元にないため奥付不明": "Colofão desconhecido pois não tenho o original em mãos.",
    "再版のカバーです。": "Esta é a capa da reimpressão.",
    "切り取られたページ、第３篇です": "Página recortada, é o Volume 3.",
    "発行禁止処分のためか塗りつぶされた目次と著者名": "Índice e nome do autor rasurados, provavelmente devido à proibição da publicação.",
    "第三編は再々版出版後刊行されたので初版しかありません。なお赤い表紙のものもありましたが内容に違いはありません。製本上の違いのようです。": "O Volume 3 foi publicado após a segunda reimpressão, então existe apenas a primeira edição. Havia também uma versão com capa vermelha, mas não há diferença no conteúdo. Parece ser apenas uma diferença na encadernação.",
    "画像はありません": "Sem imagem.",
    "写真はありません": "Não há foto.",
    "発行所": "Editora",
    "発行者": "Editor",
    "印刷者": "Impressor",
    "印刷所": "Gráfica",
    "著者": "Autor",
    "非売品": "Venda Proibida",
    "定価": "Preço",
    "目次": "Índice",
    "備考": "Observações",
    "注": "Nota",
    "解説": "Comentário",
    "訳者": "Tradutor",
    "昭和": "Era Showa",
    "年": "Ano",
    "月": "Mês",
    "日": "Dia",
    "発行": "Publicado",
    "印刷": "Impresso",
    "編集": "Edição",
    "明日の医術": "Medicina do Amanhã",
    "明日の医術（初版）": "Medicina do Amanhã (Primeira Edição)",
    "明日の医術（再版）": "Medicina do Amanhã (Reimpressão)",
    "明日の医術（再々版）": "Medicina do Amanhã (Segunda Reimpressão)",
    "岡田茂吉": "Mokiti Okada",
    "岡田　茂吉": "Mokiti Okada",
    "岡田自観": "Jikan Okada",
    "自観": "Jikan",
     "発行誌別": "Por Publicação",
    "―――　岡\n田 自 観 師 の 論 文 集　――": "--- Coletânea de Ensaios do Mestre Jikan Okada ---",
    "―――　関　連　出　版　物": "--- Publicações Relacionadas",
    "―――　関　連　出　版　物　――": "--- Publicações Relacionadas ---",
    "再版のカバーです。": "Capa da reimpressão.",
    "切り取られたページ、第３篇です": "Página cortada, é a 3ª parte.",
    "発行禁止処分のためか塗りつぶされた目次と著者名": "Índice e nome do autor pintados, possivelmente devido à proibição de publicação.",
    "第三編は再々版出版後刊行されたので初版しかありません。なお赤い表紙のものもありましたが内容に違いはありません。製本上の違いのようです。": "A terceira parte foi publicada após a segunda reimpressão, então só existe a primeira edição. Havia também uma capa vermelha, mas o conteúdo é o mesmo. Parece ser uma diferença na encadernação.",
     "原本が手元にないため奥付不明": "Colofão desconhecido pois o original não está à mão",
     "戻る": "Voltar",
     "次へ": "Próximo",
     "前へ": "Anterior",
     "ホーム": "Início",
     "トップ": "Topo",
      "閉じる": "Fechar",
      "和綴じ天地238ミリ×左右167ミリ": "Encadernação Japonesa: 238mm altura x 167mm largura",
      "B６版": "Formato B6",
      "Ｂ５版変形": "Formato B5 Variado",
      "昭和19年2月発行禁止処分": "Disposição de proibição de publicação em fevereiro de 1944",
      "昭和18年10月・5日発行": "Publicado em 5 de outubro de 1943",
      "10　取次者の霊力の強弱について": "10 Sobre a força do poder espiritual do intermediário", 
      "10　慢心取違い――小乗信仰を戒む": "10 Orgulho e Mal-entendido -- Admoestação contra a fé Hinayana",
}

# Explicit overrides for names found in specific files
NAME_OVERRIDES = {
    "熊谷印刷所": "Kumagai Printing Office",
    "志保澤　武": "Takeshi Shihozawa",
    "原　　清作": "Seisaku Hara",
    "松僑　可吉": "Kakichi Matsuhashi", # Guessing reading
    "熱海商事株式会社": "Atami Shoji Co., Ltd.",
    "一巽印刷株式会社": "Ichison Printing Co., Ltd.",
    "太陽印刷株式会社": "Taiyo Printing Co., Ltd.",
    "小山印刷工業株式会社": "Koyama Printing Industry Co., Ltd.",
    "廿世紀出版合資会社": "20th Century Publishing G.K.",
    "日本厚生観光通信社": "Japan Welfare Tourism News Agency",
    "玉友印刷合資会社": "Tamatomo Printing G.K."
}

def translate_date(text):
    # Normalize spaces
    text_norm = re.sub(r'[\u3000\s]+', ' ', text)
    
    # Regex for Showa date: 昭和18年10月5日 (with optional Showa)
    # Group 1: Optional Showa
    # Group 2: Year
    # Group 3: Month
    # Group 4: Day
    match = re.search(r'(昭和)?\s*(\d+)年\s*(\d+)月\s*(\d+)日', text_norm)
    if match:
        year_val = int(match.group(2))
        month = int(match.group(3))
        day = int(match.group(4))
        
        # Assume Showa if not specified or if year < 100
        # Showa 1 = 1926.
        # Year 18 = 1943.
        year_western = 1925 + year_val
        
        return f"{day} de {get_month_name(month)} de {year_western}"
    
    # Simple S date: S28.10.28 or S28. 10. 28
    match_s = re.search(r'S(\d+)\.\s*(\d+)\.\s*(\d+)', text_norm)
    if match_s:
         year_showa = int(match_s.group(1))
         month = int(match_s.group(2))
         day = int(match_s.group(3))
         year_western = 1925 + year_showa
         return f"{day}/{month}/{year_western}"

    return None

def get_month_name(month_num):
    months = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", 
              "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    if 1 <= month_num <= 12:
        return months[month_num - 1]
    return str(month_num)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        candidates = json.load(f)

    translations = {}

    for text in candidates:
        text_clean = text.strip()
        
        # Check manual dictionary
        if text_clean in MANUAL_TRANSLATIONS:
            translations[text_clean] = MANUAL_TRANSLATIONS[text_clean]
            continue

        # Check Name Overrides
        found_override = False
        for jp_name, en_name in NAME_OVERRIDES.items():
            if jp_name in text_clean:
                # Replace the name, but keep context like "Editor:" if present
                # But tricky if "Editor" is also Japanese "発行者"
                # Better to replace the whole string if it's just keys like "Editor: Name"
                pass 
                
        # Date handling first (as it might be embedded)
        date_trans = translate_date(text_clean)
        
        # Contextual replacements
        current_trans = text_clean
        
        if "発行者" in current_trans:
             current_trans = current_trans.replace("発行者", "Editor: ")
        if "印刷者" in current_trans:
             current_trans = current_trans.replace("印刷者", "Impressor: ")
        if "印刷所" in current_trans:
             current_trans = current_trans.replace("印刷所", "Gráfica: ")
        if "著者" in current_trans and "岡田" in current_trans:
             current_trans = "Autor: Mokiti Okada" # Override for author lines
        if "非売品" in current_trans:
             current_trans = current_trans.replace("非売品", "Venda Proibida")

        # Apply name overrides to the potentially partially translated string
        for jp_name, en_name in NAME_OVERRIDES.items():
            if jp_name in current_trans:
                current_trans = current_trans.replace(jp_name, en_name)
        
        # If we found a date, replace the date part or the whole string if it looks like a date line
        if date_trans:
            # If the text is MAINLY date + Publish/Print
            if "発行" in text_clean and "禁止" not in text_clean: # Exclude "Ban" line
                 current_trans = f"Publicado em {date_trans}"
            elif "印刷" in text_clean and "所" not in text_clean and "者" not in text_clean: # Exclude Place/Person
                 current_trans = f"Impresso em {date_trans}"
            elif current_trans == text_clean: # If no other changes made
                 current_trans = date_trans
            else:
                 # Replace the Japanese date string in the text with the Portuguese one?
                 # Hard to find exact substring match due to normalization.
                 # If we have a robust date, maybe just use it?
                 pass

        if current_trans != text_clean:
             translations[text_clean] = current_trans.strip()
                 
    # Sort and save
    print(f"Generated {len(translations)} supplemental translations.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(translations, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
