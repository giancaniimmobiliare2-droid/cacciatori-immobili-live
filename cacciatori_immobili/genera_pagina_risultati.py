#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
GENERATORE CONSOLE HTML (GITHUB PAGES + MOBILE 1-CLICK WHATSAPP/EMAIL + MEMORIA 30GG)
Progetto: "Cacciatori di Immobili"
Brand: Immobiliare Giancani • Antonio Giancani (+39 320 166 7156)
Assistente AI 24/7: DarIA (+39 350 590 2923)

Pagine Ordinate nella Console:
1. 📞 NUMERI PRIVATI & AZIONE 1-CLICK WHATSAPP/EMAIL (con Video YouTube e Memoria 30 Giorni)
2. 👤 PRIVATI VERIFICATI (7 Comuni Target)
3. 🕵️ SOSPETTI AGENZIE (Falsi Privati / Multi-Annuncio / Aste)
4. 🏢 AGENZIE IMMOBILIARI & MONITORAGGIO RIBASSI
5. 🧭 INDICE PORTALI MINORI (20+ Fonti)

Regole Mandatorie:
- Testi estratti rigorosamente dalla Colonna F.
- Superfici sempre riportate per esteso come "metri quadri".
- Personal Branding obbligatorio in chiusura: "— Immobiliare Giancani".
=============================================================================
"""

import os
import sys
import re
import csv
import json
import html
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bot_python", "cacciatore_db.json")
OUTPUT_HTML_DIR = os.path.join(BASE_DIR, "RISULTATI_IMMOBILI.html")
OUTPUT_HTML_ROOT = os.path.join(os.path.dirname(BASE_DIR), "RISULTATI_IMMOBILI.html")
OUTPUT_HTML_GITHUB = os.path.join(BASE_DIR, "cacciatori.html")
OUTPUT_CSV_PRIVATI = os.path.join(BASE_DIR, "ELENCO_PRIVATI_NOMI_TELEFONI.csv")

WEBHOOK_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbwEeH82YCSoOc-KRZx6pSQa_k3Kb5i252_Ajljlo20IOBinGiqA1E0ZE_2gKljHpLu3/exec"
DEFAULT_YOUTUBE_VIDEO = "https://www.youtube.com/watch?v=TsdEk3Y9ewc"


def normalizza_metri_quadri_testo(testo):
    if not testo:
        return ""
    ris = re.sub(r'(\d)\s*(?:mq\.?|m²|m2)\b', r'\1 metri quadri', str(testo), flags=re.IGNORECASE)
    ris = re.sub(r'\b(?:mq\.?|m2)\b|m²', 'metri quadri', ris, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', ris).strip()


def ottieni_nome_privato(item):
    nome = str(item.get("nome_privato") or item.get("nome_inserzionista") or item.get("email") or "").strip()
    if not nome or nome.lower() in ("privato", "none", "null"):
        return "Proprietario Privato"
    return nome


INDICE_PORTALI = [
    {
        "categoria": "1. Portali Verticali 'Solo Privati' (Zero Agenzie)",
        "portali": [
            {
                "nome": "CasaDaPrivato.it",
                "tipo": "Solo Privati 100%",
                "stato_bot": "Monitorato",
                "url": "https://www.casadaprivato.it/annunci-vendita/immobili/agrigento-provincia",
                "note": "Portale nazionale dedicato esclusivamente alla compravendita tra privati senza agenzia."
            },
            {
                "nome": "ClickCase.it",
                "tipo": "Specializzato Privati",
                "stato_bot": "Indicizzato",
                "url": "https://www.clickcase.it/vendita-case-agrigento.htm",
                "note": "Storico portale italiano per annunci immobiliari diretti da proprietari privati."
            },
            {
                "nome": "SenzaAgenzia.it / Privati",
                "tipo": "No Intermediari",
                "stato_bot": "Indicizzato",
                "url": "https://www.google.com/search?q=site:casadaprivato.it+OR+site:clickcase.it+Favara+OR+Agrigento",
                "note": "Ricerca mirata di annunci diretti pubblicati dai proprietari senza commissioni."
            }
        ]
    },
    {
        "categoria": "2. Portali Generalisti Gratuiti (Altissima presenza di Privati in Sicilia)",
        "portali": [
            {
                "nome": "Subito.it (7 Comuni Target — Solo Privati)",
                "tipo": "Leader Privati Sicilia",
                "stato_bot": "Attivo 24/7",
                "url": "https://www.subito.it/annunci-sicilia/vendita/immobili/agrigento/?order=datedesc&f=p",
                "note": "Il portale più usato dai privati a Favara, Agrigento, Aragona, Comitini, Porto Empedocle, Siculiana e Realmonte."
            },
            {
                "nome": "Bakeca.it Agrigento",
                "tipo": "Annunci Gratuiti",
                "stato_bot": "Attivo 24/7",
                "url": "https://agrigento.bakeca.it/annunci/vendita-case/",
                "note": "Bacheca gratuita molto utilizzata da proprietari privati per case, terreni e magazzini."
            },
            {
                "nome": "Cambiocasa.it",
                "tipo": "Annunci Gratuiti Case",
                "stato_bot": "Attivo 24/7",
                "url": "https://www.cambiocasa.it/vendita/case/agrigento/",
                "note": "Portale con inserimento gratuito per privati e agenzie in provincia di Agrigento."
            },
            {
                "nome": "Vivastreet.it Immobili",
                "tipo": "Classificati Gratuiti",
                "stato_bot": "Indicizzato",
                "url": "https://www.vivastreet.it/vendita-immobili/agrigento",
                "note": "Portale di annunci classificati gratuiti con sezione vendita immobili da privati."
            },
            {
                "nome": "AAAnnunci.it / TuttoAnnunci.org",
                "tipo": "Bacheca Storica Free",
                "stato_bot": "Indicizzato",
                "url": "https://www.tuttoannunci.org/agrigento/immobili-case_vendita.html",
                "note": "Bacheche gratuite dove pubblicano proprietari non presenti sui portali a pagamento."
            },
            {
                "nome": "Facebook Marketplace (Immobili)",
                "tipo": "Social Local",
                "stato_bot": "Link Diretto",
                "url": "https://www.facebook.com/marketplace/category/propertyforsale",
                "note": "Annunci social geolocalizzati su Favara e provincia di Agrigento."
            }
        ]
    },
    {
        "categoria": "3. Portali Immobiliari Minori, Aggregatori & Aste",
        "portali": [
            {
                "nome": "PCase.it Agrigento",
                "tipo": "Portale Verticale",
                "stato_bot": "Attivo 24/7",
                "url": "https://www.pcase.it/vendita/agrigento/",
                "note": "Portale immobiliare italiano con schede dettagliate per Favara e provincia di Agrigento."
            },
            {
                "nome": "Caasa.it (Motore AI Immobiliare)",
                "tipo": "Meta-Aggregatore",
                "stato_bot": "Consigliato",
                "url": "https://www.caasa.it/agrigento/favara/in-vendita.html",
                "note": "Indicizza decine di portali minori calcolando lo scostamento del prezzo al metro quadro."
            },
            {
                "nome": "Trovit Case & Mitula",
                "tipo": "Aggregatore Multi-Sito",
                "stato_bot": "Indicizzato",
                "url": "https://case.trovit.it/vendita-casa-favara",
                "note": "Raccoglie annunci da decine di siti immobiliari secondari in un'unica vista."
            },
            {
                "nome": "Immobiliare.it & Idealista.it",
                "tipo": "Big Portals",
                "stato_bot": "Incroci Agenzie",
                "url": "https://www.immobiliare.it/vendita-case/agrigento-provincia/?criterio=dataModifica&ordine=desc",
                "note": "Monitoraggio ribassi e scadenze incarichi di altre agenzie."
            },
            {
                "nome": "Astalegale.net / PVP Giustizia",
                "tipo": "Aste & Stralcio",
                "stato_bot": "Specialistico",
                "url": "https://www.astalegale.net/Immobili/Ricerca?provincia=AG",
                "note": "Esecuzioni immobiliari Tribunale di Agrigento per operazioni a saldo e stralcio."
            }
        ]
    }
]


def esporta_csv_privati(lista_privati):
    try:
        with open(OUTPUT_CSV_PRIVATI, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                "ID_ANNUNCIO", "CATEGORIA", "DATA_RILEVAZIONE", "NOME_COGNOME_PRIVATO",
                "TELEFONO", "EMAIL_CONTATTO", "COMUNE", "COL_F_TESTO_ORIGINALE",
                "VIA_ZONA", "TIPOLOGIA", "METRI_QUADRI", "PREZZO", "LINK_ANNUNCIO", "BRAND"
            ])
            for it in lista_privati:
                nome_p = ottieni_nome_privato(it)
                tel_p = it.get("telefono", "") or ""
                em_p = it.get("email_contatto", "") or ""
                col_f = normalizza_metri_quadri_testo(it.get("descrizione", it.get("titolo", "")))
                if "Immobiliare Giancani" not in col_f:
                    col_f += " — Immobiliare Giancani"
                writer.writerow([
                    it.get("id", ""),
                    it.get("categoria_classificazione", "privato"),
                    str(it.get("timestamp", ""))[:19].replace("T", " "),
                    nome_p,
                    tel_p,
                    em_p,
                    it.get("comune", ""),
                    col_f,
                    normalizza_metri_quadri_testo(it.get("via_zona", "")),
                    it.get("tipologia", ""),
                    normalizza_metri_quadri_testo(it.get("superficie", "")),
                    it.get("prezzo", ""),
                    it.get("url", ""),
                    "— Immobiliare Giancani"
                ])
    except Exception as e:
        print(f"[CSV Export] Errore salvataggio CSV privati: {e} — Immobiliare Giancani")


def genera_html_resoconto(highlight_item=None, output_path=None):
    """
    Genera la Console HTML completa (ottimizzata per Cellulare e ospitata su GitHub Pages)
    con le 5 sezioni ordinate, invio 1-click WhatsApp/Email con video YouTube e Memoria 30 Giorni.
    """
    db = {"immobili": {}, "memoria_invii_30gg": {}, "ultimo_aggiornamento": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception as e:
            print(f"[HTML Generator] Errore lettura DB: {e} — Immobiliare Giancani")

    # Assicura che la classificazione sospetti agenzie e ribassi sia applicata
    bot_dir = os.path.join(BASE_DIR, "bot_python")
    if bot_dir not in sys.path:
        sys.path.insert(0, bot_dir)
    try:
        import cacciatore_bot
        cacciatore_bot.classifica_sospetti_agenzie_e_ribassi(db.get("immobili", {}))
    except Exception:
        pass

    immobili_dict = db.get("immobili", {})
    memoria_30gg = db.get("memoria_invii_30gg", {})
    lista_immobili = list(immobili_dict.values())
    lista_immobili.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Smistamento nelle 3 liste principali + lista contatti diretti
    privati_puri = [x for x in lista_immobili if x.get("categoria_classificazione", "privato" if x.get("is_privato") else "agenzia") == "privato"]
    sospetti_agenzie = [x for x in lista_immobili if x.get("categoria_classificazione") == "sospetto_agenzia"]
    agenzie_immobiliari = [x for x in lista_immobili if x.get("categoria_classificazione") == "agenzia" or not x.get("is_privato", False)]

    esporta_csv_privati(privati_puri)

    # Prepara il JSON compatto per il motore JavaScript client-side (Azioni 1-Click, Memoria 30gg, Filtri)
    dataset_js = []
    for it in lista_immobili:
        col_f = normalizza_metri_quadri_testo(it.get("descrizione", it.get("titolo", "")))
        if "Immobiliare Giancani" not in col_f:
            col_f += " — Immobiliare Giancani"
        dataset_js.append({
            "id": it.get("id", ""),
            "cat": it.get("categoria_classificazione", "privato" if it.get("is_privato") else "agenzia"),
            "comune": it.get("comune", "Agrigento"),
            "titolo": normalizza_metri_quadri_testo(it.get("titolo", "Immobile")),
            "via_zona": normalizza_metri_quadri_testo(it.get("via_zona", it.get("titolo", ""))),
            "tipologia": it.get("tipologia", "Immobile"),
            "superficie": normalizza_metri_quadri_testo(it.get("superficie", "Non specificata")),
            "prezzo": it.get("prezzo", "Su richiesta"),
            "prezzo_iniziale": it.get("prezzo_iniziale", it.get("prezzo", "Su richiesta")),
            "ribasso_importo": it.get("ribasso_importo", 0),
            "ribasso_percentuale": it.get("ribasso_percentuale", 0),
            "ha_ribasso": bool(it.get("ha_ribasso", False)),
            "storico_prezzi": it.get("storico_prezzi", []),
            "nome_privato": ottieni_nome_privato(it),
            "nome_agenzia": it.get("nome_agenzia", "Agenzia"),
            "telefono": str(it.get("telefono", "") or "").strip(),
            "email_contatto": str(it.get("email_contatto", "") or "").strip(),
            "motivo_sospetto": it.get("motivo_sospetto", ""),
            "url": it.get("url", "#"),
            "foto_url": it.get("foto_url", "") or "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=500&auto=format&fit=crop&q=60",
            "descrizione": col_f,
            "timestamp": str(it.get("timestamp", ""))[:16].replace("T", " ")
        })

    # Costruzione HTML per la scheda Portali Minori
    indice_portali_html = ""
    for blocco in INDICE_PORTALI:
        rows_html = ""
        for p in blocco["portali"]:
            rows_html += f"""
            <div class="bg-slate-50 hover:bg-white p-4 rounded-xl border border-slate-200 transition flex flex-col justify-between gap-3">
              <div>
                <div class="flex justify-between items-start gap-2 mb-1">
                  <h4 class="font-black text-slate-900 text-sm">{html.escape(p['nome'])}</h4>
                  <span class="text-[10px] font-black px-2.5 py-0.5 rounded-full border bg-emerald-100 text-emerald-800 border-emerald-300">
                    {html.escape(p['stato_bot'])}
                  </span>
                </div>
                <div class="text-[11px] font-bold text-indigo-600 mb-1.5">{html.escape(p['tipo'])}</div>
                <p class="text-xs text-slate-600 leading-relaxed">{html.escape(p['note'])}</p>
              </div>
              <div class="pt-2 border-t border-slate-200/70 flex justify-between items-center">
                <a href="{html.escape(p['url'])}" target="_blank" class="text-xs font-black text-amber-600 hover:text-amber-700">
                  🌐 Apri Portale Agrigento/Favara ➔
                </a>
                <span class="text-[10px] text-slate-400 font-semibold">— Immobiliare Giancani</span>
              </div>
            </div>
            """
        indice_portali_html += f"""
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 mb-5">
          <h3 class="text-base font-black text-slate-900 mb-4 pb-2 border-b border-slate-100">
            {html.escape(blocco['categoria'])}
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {rows_html}
          </div>
        </div>
        """

    ora_generazione = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    json_dataset_str = json.dumps(dataset_js, ensure_ascii=False)
    json_memoria_str = json.dumps(memoria_30gg, ensure_ascii=False)

    full_html = f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Console Cacciatori di Immobili — Antonio Giancani • Immobiliare Giancani</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    .line-clamp-3 {{
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}
    .line-clamp-3:hover {{
      -webkit-line-clamp: unset;
    }}
    .tab-active {{
      background-color: #f59e0b !important;
      color: #0f172a !important;
      border-color: #f59e0b !important;
      box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
    }}
  </style>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen pb-16">

  <!-- TOP BAR BRANDING -->
  <div class="bg-slate-950 text-slate-200 px-3 py-2 text-[11px] border-b border-slate-800">
    <div class="max-w-7xl mx-auto flex flex-wrap justify-between items-center gap-2">
      <div class="font-black text-amber-400 flex items-center gap-1.5">
        <span>🎯 CACCIATORI DI IMMOBILI — CONSOLE MOBILE &amp; GITHUB CLOUD</span>
      </div>
      <div class="flex flex-wrap items-center gap-3 text-slate-300 font-semibold">
        <span>Titolare: <strong class="text-white">Antonio Giancani (+39 320 166 7156)</strong></span>
        <div class="flex items-center gap-1.5" title="Chi siamo sui Social — Immobiliare Giancani">
          <a href="https://www.facebook.com/immobiliaregiancani.it" target="_blank" aria-label="Facebook Immobiliare Giancani" class="w-6 h-6 rounded-full bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center transition shadow-sm">
            <i class="fa-brands fa-facebook-f text-[11px]"></i>
          </a>
          <a href="https://www.tiktok.com/@immobiliare_giancani" target="_blank" aria-label="TikTok Immobiliare Giancani" class="w-6 h-6 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white flex items-center justify-center transition shadow-sm">
            <i class="fa-brands fa-tiktok text-[11px]"></i>
          </a>
          <a href="https://youtube.com/@immobiliaregiancani" target="_blank" aria-label="YouTube Immobiliare Giancani" class="w-6 h-6 rounded-full bg-red-600 hover:bg-red-500 text-white flex items-center justify-center transition shadow-sm">
            <i class="fa-brands fa-youtube text-[11px]"></i>
          </a>
        </div>
        <span class="text-amber-400 font-bold">— Immobiliare Giancani</span>
      </div>
    </div>
  </div>

  <!-- HEADER & NAVIGAZIONE 5 PAGINE ORDINATE -->
  <header class="bg-slate-900 text-white shadow-xl sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-3 py-3">
      <div class="flex flex-wrap justify-between items-center gap-2 mb-3">
        <div>
          <h1 class="text-lg md:text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <span>Immobiliare Giancani — Acquisizione &amp; Intelligence</span>
            <span class="bg-emerald-500 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded-full">MEMORIA 30 GIORNI ATTIVA</span>
          </h1>
          <p class="text-[11px] text-amber-400 font-semibold">
            Favara • Agrigento • Aragona • Comitini • Porto Empedocle • Siculiana • Realmonte ({ora_generazione})
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="sincronizzaMemoriaCloud(true)" class="bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 text-xs font-bold px-3 py-2 rounded-xl flex items-center gap-1.5">
            <i class="fa-solid fa-cloud-arrow-down"></i> Sync Memoria Cloud
          </button>
        </div>
      </div>

      <!-- MENU 7 PAGINE ORDINATE (MOBILE-FRIENDLY) -->
      <div class="grid grid-cols-2 sm:grid-cols-7 gap-2">
        <button onclick="cambiaPagina('numeri')" id="nav-numeri" class="tab-active bg-slate-800 text-white font-black text-xs py-2.5 px-2 rounded-xl border border-slate-700 flex items-center justify-center gap-1 transition">
          <span>📲 1. Numeri Privati</span>
          <span id="badge-numeri" class="bg-slate-950 text-amber-400 px-1.5 py-0.5 rounded-full text-[10px]">0</span>
        </button>
        <button onclick="cambiaPagina('privati')" id="nav-privati" class="bg-slate-800 text-slate-200 hover:bg-slate-700 font-black text-xs py-2.5 px-2 rounded-xl border border-slate-700 flex items-center justify-center gap-1 transition">
          <span>👤 2. Privati</span>
          <span id="badge-privati" class="bg-emerald-900 text-emerald-300 px-1.5 py-0.5 rounded-full text-[10px]">0</span>
        </button>
        <button onclick="cambiaPagina('sospetti')" id="nav-sospetti" class="bg-slate-800 text-slate-200 hover:bg-slate-700 font-black text-xs py-2.5 px-2 rounded-xl border border-slate-700 flex items-center justify-center gap-1 transition">
          <span>🕵️ 3. Sospetti</span>
          <span id="badge-sospetti" class="bg-amber-900 text-amber-300 px-1.5 py-0.5 rounded-full text-[10px]">0</span>
        </button>
        <button onclick="cambiaPagina('agenzie')" id="nav-agenzie" class="bg-slate-800 text-slate-200 hover:bg-slate-700 font-black text-xs py-2.5 px-2 rounded-xl border border-slate-700 flex items-center justify-center gap-1 transition">
          <span>🏢 4. Agenzie</span>
          <span id="badge-agenzie" class="bg-indigo-900 text-indigo-300 px-1.5 py-0.5 rounded-full text-[10px]">0</span>
        </button>
        <button onclick="cambiaPagina('portali')" id="nav-portali" class="bg-slate-800 text-slate-200 hover:bg-slate-700 font-black text-xs py-2.5 px-2 rounded-xl border border-slate-700 flex items-center justify-center gap-1 transition">
          <span>🧭 5. Portali</span>
        </button>
        <button onclick="cambiaPagina('statistiche')" id="nav-statistiche" class="bg-slate-800 text-slate-200 hover:bg-slate-700 font-black text-xs py-2.5 px-2 rounded-xl border border-slate-700 flex items-center justify-center gap-1 transition">
          <span>📊 6. Statistiche</span>
        </button>
        <button onclick="cambiaPagina('visti')" id="nav-visti" class="bg-slate-800 text-slate-200 hover:bg-slate-700 font-black text-xs py-2.5 px-2 rounded-xl border border-slate-700 flex items-center justify-center gap-1 transition">
          <span>👁️ 7. Visti</span>
          <span id="badge-visti" class="bg-slate-700 text-slate-200 px-1.5 py-0.5 rounded-full text-[10px]">0</span>
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-3 py-5 space-y-6">

    <!-- FILTRO RAPIDO GLOBALE PER COMUNE -->
    <div class="bg-white p-3.5 rounded-2xl shadow-sm border border-slate-200 flex flex-wrap items-center justify-between gap-2">
      <div class="flex flex-wrap items-center gap-1.5">
        <span class="text-xs font-black text-slate-700 mr-1">📍 Comune:</span>
        <button onclick="setComuneGlobale('TUTTI')" id="btn-com-TUTTI" class="com-pill bg-slate-900 text-amber-400 text-xs font-black px-3 py-1.5 rounded-xl">Tutti</button>
        <button onclick="setComuneGlobale('Favara')" id="btn-com-Favara" class="com-pill bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-xl">Favara</button>
        <button onclick="setComuneGlobale('Agrigento')" id="btn-com-Agrigento" class="com-pill bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-xl">Agrigento</button>
        <button onclick="setComuneGlobale('Aragona')" id="btn-com-Aragona" class="com-pill bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-xl">Aragona</button>
        <button onclick="setComuneGlobale('Comitini')" id="btn-com-Comitini" class="com-pill bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-xl">Comitini</button>
        <button onclick="setComuneGlobale('Porto Empedocle')" id="btn-com-Porto Empedocle" class="com-pill bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-xl">Porto Empedocle</button>
        <button onclick="setComuneGlobale('Siculiana')" id="btn-com-Siculiana" class="com-pill bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-xl">Siculiana</button>
        <button onclick="setComuneGlobale('Realmonte')" id="btn-com-Realmonte" class="com-pill bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-xl">Realmonte</button>
      </div>
      <input type="text" id="ricerca-globale" oninput="renderTutto()" placeholder="🔍 Cerca nome, numero, via, testo Colonna F..."
             class="w-full sm:w-64 bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500">
    </div>

    <!-- ===================================================================== -->
    <!-- PAGINA 1: NUMERI PRIVATI & AZIONE 1-CLICK WHATSAPP / EMAIL (30 GIORNI) -->
    <!-- ===================================================================== -->
    <section id="page-numeri" class="space-y-6">

      <!-- PANNELLO CONFIGURAZIONE PRESENTAZIONE ANTONIO GIANCANI + LINK YOUTUBE -->
      <div class="bg-slate-900 text-white rounded-3xl p-5 md:p-6 shadow-xl border border-amber-500/40">
        <div class="flex flex-wrap justify-between items-center gap-2 mb-4 pb-3 border-b border-slate-800">
          <div>
            <h2 class="text-base md:text-lg font-black text-amber-400 flex items-center gap-2">
              <i class="fa-brands fa-youtube text-red-500 text-xl"></i>
              <span>Configurazione Messaggio di Presentazione &amp; Video YouTube</span>
            </h2>
            <p class="text-xs text-slate-300">
              Personalizza il link del tuo video di presentazione su YouTube e il messaggio con cui chiedi l'incarico di vendita. Resta salvato in memoria e dopo 30 giorni sblocca il cliente per un nuovo invio.
            </p>
          </div>
          <button onclick="toggleConfigBox()" class="bg-slate-800 hover:bg-slate-700 text-amber-400 text-xs font-bold px-3.5 py-2 rounded-xl border border-slate-700">
            ⚙️ Modifica Messaggio / Video YouTube
          </button>
        </div>

        <div id="box-config-messaggio" class="hidden space-y-4 mb-4 bg-slate-950 p-4 rounded-2xl border border-slate-800">
          <div>
            <label class="block text-xs font-black text-amber-400 mb-1">
              🎥 Link Video YouTube di Presentazione di Antonio Giancani:
            </label>
            <input type="url" id="cfg-youtube-url" oninput="salvaConfigPresentazione(false)"
                   class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-white font-mono focus:ring-2 focus:ring-amber-500"
                   placeholder="https://www.youtube.com/watch?v=...">
          </div>

          <div>
            <label class="block text-xs font-black text-amber-400 mb-1">
              💬 Messaggio di Presentazione WhatsApp &amp; Email (Variabili: {{NOME}}, {{COMUNE}}, {{VIA_ZONA}}, {{METRI_QUADRI}}, {{PREZZO}}, {{LINK_YOUTUBE}}):
            </label>
            <textarea id="cfg-messaggio-wa" rows="7" oninput="salvaConfigPresentazione(false)"
                      class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3.5 text-xs text-slate-100 font-mono focus:ring-2 focus:ring-amber-500"></textarea>
          </div>

          <div class="flex flex-wrap justify-between items-center gap-2">
            <button onclick="ripristinaMessaggioDefault()" class="text-xs text-slate-400 hover:text-white underline">
              Ripristina Testo Predefinito Giancani
            </button>
            <button onclick="salvaConfigPresentazione(true)" class="bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs px-5 py-2.5 rounded-xl shadow-lg">
              💾 Salva in Memoria Cloud &amp; Cellulare
            </button>
          </div>
        </div>

        <!-- CARD AZIONE RAPIDA SEQUENZIALE DAL CELLULARE (1-CLICK) -->
        <div id="card-coda-cellulare" class="bg-gradient-to-br from-emerald-950 to-slate-900 border-2 border-emerald-500/60 rounded-2xl p-5">
          <!-- Popolato via JS con il prossimo cliente da contattare -->
        </div>
      </div>

      <!-- STATISTICHE MEMORIA 30 GIORNI -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <button onclick="setFiltroStatoNumeri('DA_CONTATTARE')" id="flt-num-DA_CONTATTARE" class="bg-emerald-700 text-white p-4 rounded-2xl shadow text-left border-2 border-emerald-400">
          <div class="text-xs font-bold uppercase text-emerald-200">🟢 Pronti da Contattare Ora</div>
          <div id="kpi-da-contattare" class="text-2xl font-black mt-1">0</div>
          <div class="text-[11px] text-emerald-200">Nuovi numeri o scaduto 1 mese (30 gg)</div>
        </button>
        <button onclick="setFiltroStatoNumeri('IN_MEMORIA_30GG')" id="flt-num-IN_MEMORIA_30GG" class="bg-white text-slate-800 p-4 rounded-2xl shadow-sm text-left border border-slate-200">
          <div class="text-xs font-bold uppercase text-slate-500">⏳ Già Contattati (In Memoria 30gg)</div>
          <div id="kpi-in-memoria" class="text-2xl font-black text-amber-600 mt-1">0</div>
          <div class="text-[11px] text-slate-400">Si sbloccano automaticamente dopo 30 giorni</div>
        </button>
        <button onclick="setFiltroStatoNumeri('TUTTI')" id="flt-num-TUTTI" class="bg-white text-slate-800 p-4 rounded-2xl shadow-sm text-left border border-slate-200">
          <div class="text-xs font-bold uppercase text-slate-500">📋 Tutti i Contatti Privati</div>
          <div id="kpi-tutti-numeri" class="text-2xl font-black text-slate-900 mt-1">0</div>
          <div class="text-[11px] text-slate-400">Rubrica completa sincronizzata — Immobiliare Giancani</div>
        </button>
      </div>

      <!-- TABELLA / LISTA MOBILE NUMERI PRIVATI CON PULSANTE 1-CLICK WHATSAPP & EMAIL -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="p-4 border-b border-slate-100 flex flex-wrap justify-between items-center gap-3">
          <div>
            <h3 class="font-black text-slate-900 text-sm md:text-base">
              📞 Elenco Numeri &amp; Email Privati Verificati (1-Click App WhatsApp &amp; Email)
            </h3>
            <p class="text-xs text-slate-500">
              Pulsante <span class="text-emerald-700 font-bold">Verde = Recapito presente</span> • <span class="text-slate-400 font-bold">Spento = Recapito assente</span>. Ogni invio resta in memoria per 30 giorni.
            </p>
          </div>
          <button onclick="inviaEmailATutti1Click()" id="btn-invia-tutte-email" class="bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs px-4 py-3 rounded-xl shadow-md flex items-center gap-2 transition">
            <i class="fa-solid fa-paper-plane"></i>
            <span id="lbl-invia-tutte-email">✉️ INVIA EMAIL A TUTTI CON 1 CLICK (0)</span>
          </button>
        </div>
        <div id="lista-numeri-privati" class="divide-y divide-slate-100">
          <!-- Generato via JS -->
        </div>
      </div>

    </section>

    <!-- ===================================================================== -->
    <!-- PAGINA 2: PRIVATI VERIFICATI (SCHEDE COMPLETE + COLONNA F)            -->
    <!-- ===================================================================== -->
    <section id="page-privati" class="hidden space-y-4">
      <div class="bg-emerald-950 text-white p-5 rounded-2xl border border-emerald-700 flex flex-wrap justify-between items-center gap-3">
        <div>
          <h2 class="text-lg font-black text-emerald-400">👤 Annunci di Proprietari Privati Verificati</h2>
          <p class="text-xs text-emerald-200">
            Puliti automaticamente dai falsi privati e dalle aste. Testi completi dalla Colonna F e superfici in metri quadri. — Immobiliare Giancani
          </p>
        </div>
      </div>
      <div id="griglia-privati" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"></div>
    </section>

    <!-- ===================================================================== -->
    <!-- PAGINA 3: SOSPETTI AGENZIE (FALSI PRIVATI / MULTI-ANNUNCIO / ASTE)    -->
    <!-- ===================================================================== -->
    <section id="page-sospetti" class="hidden space-y-4">
      <div class="bg-amber-950 text-white p-5 rounded-2xl border border-amber-700">
        <h2 class="text-lg font-black text-amber-400">🕵️ Sospetti Agenzie / Falsi Privati / Aste Camuffate</h2>
        <p class="text-xs text-amber-200 mt-1">
          Questi annunci erano stati pubblicati come "Privato", ma il sistema ha rilevato più immobili con lo stesso account/numero oppure formule tipiche da agenzia o asta giudiziaria. Se verifichi che uno è un vero privato, puoi spostarlo nei Privati con 1 click. — Immobiliare Giancani
        </p>
      </div>
      <div id="griglia-sospetti" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"></div>
    </section>

    <!-- ===================================================================== -->
    <!-- PAGINA 4: AGENZIE IMMOBILIARI & MONITORAGGIO RIBASSI                  -->
    <!-- ===================================================================== -->
    <section id="page-agenzie" class="hidden space-y-4">
      <div class="bg-indigo-950 text-white p-5 rounded-2xl border border-indigo-700 flex flex-wrap justify-between items-center gap-3">
        <div>
          <h2 class="text-lg font-black text-indigo-300">🏢 Sezione Agenzie Immobiliari &amp; Monitoraggio Ribassi</h2>
          <p class="text-xs text-indigo-200">
            Tutti gli annunci delle agenzie concorrenti sono isolati qui per monitorare i loro ribassi di prezzo e intervenire quando l'incarico scade. — Immobiliare Giancani
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <button onclick="toggleSoloRibassiAgenzie()" id="btn-solo-ribassi-ag" class="bg-rose-600 hover:bg-rose-500 text-white text-xs font-black px-4 py-2.5 rounded-xl shadow">
            📉 Mostra Solo Immobili con Ribasso
          </button>
          <select id="select-nome-agenzia" onchange="renderAgenzie()" class="bg-slate-900 text-white border border-indigo-600 rounded-xl px-3 py-2.5 text-xs font-bold">
            <option value="TUTTE">🏢 Tutte le Agenzie</option>
          </select>
        </div>
      </div>
      <div id="griglia-agenzie" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"></div>
    </section>

    <!-- ===================================================================== -->
    <!-- PAGINA 5: INDICE PORTALI MINORI                                       -->
    <!-- ===================================================================== -->
    <section id="page-portali" class="hidden space-y-5">
      <div class="bg-amber-50 border border-amber-300 rounded-2xl p-5">
        <h2 class="text-lg font-black text-slate-900">
          🧭 Mappa Strategica dei Portali Immobiliari Minori, Gratuiti e "Solo Privati"
        </h2>
        <p class="text-xs text-slate-700 mt-1">
          Indice strutturato dei portali dove i proprietari privati di Favara e della provincia di Agrigento pubblicano annunci gratuiti fuori dai circuiti delle agenzie. — Immobiliare Giancani
        </p>
      </div>
      {indice_portali_html}
    </section>

    <!-- ===================================================================== -->
    <!-- PAGINA 6: STATISTICHE AVANZATE PER MESI, PORTALI, ZONE, PREZZI & AGENZIE -->
    <!-- ===================================================================== -->
    <section id="page-statistiche" class="hidden space-y-6">
      <div class="bg-slate-900 text-white p-5 rounded-2xl border border-amber-500/40">
        <h2 class="text-lg font-black text-amber-400">📊 Statistiche Immobiliari: Mesi, Portali, Zone, Prezzi &amp; Agenzie</h2>
        <p class="text-xs text-slate-300 mt-1">
          Analisi completa dell'andamento mensile degli annunci, distribuzione per portali, zone in crescita e comportamento delle agenzie immobiliari concorrenti. — Immobiliare Giancani
        </p>
      </div>
      <div id="contenuto-statistiche" class="space-y-6">
        <!-- Popolato dinamicamente via JS -->
      </div>
    </section>

    <!-- ===================================================================== -->
    <!-- PAGINA 7: IMMOBILI GIÀ VISTI                                          -->
    <!-- ===================================================================== -->
    <section id="page-visti" class="hidden space-y-4">
      <div class="bg-slate-800 text-white p-5 rounded-2xl border border-slate-600 flex flex-wrap justify-between items-center gap-3">
        <div>
          <h2 class="text-lg font-black text-amber-400">👁️ Immobili Già Visti</h2>
          <p class="text-xs text-slate-300">
            Qui finiscono gli annunci che hai già controllato o segnato come visti, così la pagina dei nuovi annunci resta sempre pulita. Puoi ripristinarli in qualsiasi momento. — Immobiliare Giancani
          </p>
        </div>
      </div>
      <div id="griglia-visti" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"></div>
    </section>

  </main>

  <!-- FOOTER PERSONAL BRANDING OBBLIGATORIO -->
  <footer class="bg-slate-950 text-slate-400 py-6 mt-12 border-t border-slate-800 text-center text-xs">
    <div class="max-w-7xl mx-auto px-4 space-y-2.5">
      <div class="flex justify-center items-center gap-2">
        <span class="text-[11px] font-bold text-slate-300">Chi siamo sui Social:</span>
        <a href="https://www.facebook.com/immobiliaregiancani.it" target="_blank" title="Facebook" class="w-7 h-7 rounded-full bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center transition">
          <i class="fa-brands fa-facebook-f text-xs"></i>
        </a>
        <a href="https://www.tiktok.com/@immobiliare_giancani" target="_blank" title="TikTok" class="w-7 h-7 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white flex items-center justify-center transition">
          <i class="fa-brands fa-tiktok text-xs"></i>
        </a>
        <a href="https://youtube.com/@immobiliaregiancani" target="_blank" title="YouTube" class="w-7 h-7 rounded-full bg-red-600 hover:bg-red-500 text-white flex items-center justify-center transition">
          <i class="fa-brands fa-youtube text-xs"></i>
        </a>
      </div>
      <div class="text-amber-400 font-black text-sm">
        — Immobiliare Giancani
      </div>
      <p>
        Console Mobile &amp; Cloud "Cacciatori di Immobili" • Antonio Giancani (+39 320 166 7156)
      </p>
    </div>
  </footer>

  <script>
    const WEBHOOK_URL = "{WEBHOOK_APPS_SCRIPT}";
    const DEFAULT_YT_URL = "{DEFAULT_YOUTUBE_VIDEO}";
    const GIORNI_SCADENZA = 30;
    const MS_30_GIORNI = GIORNI_SCADENZA * 24 * 60 * 60 * 1000;

    const DEFAULT_TEMPLATE_WA = `Gentile {{{{NOME}}}}, {{{{SALUTO_ORARIO}}}}!

👋 Sono Antonio Giancani, titolare dell'agenzia Immobiliare Giancani.
🏡 Ho visto con molto interesse il Suo annuncio per l'immobile in vendita a {{{{COMUNE}}}} ({{{{VIA_ZONA}}}}) di {{{{METRI_QUADRI}}}}, proposto a {{{{PREZZO}}}}.

🤝 Le scrivo perché vorrei lavorare per Lei per venderLe l'immobile al miglior prezzo di mercato, selezionando solo acquirenti già qualificati (zero perditempo) e curando tutta la conformità urbanistica e catastale fino al rogito notarile. 📋✅

🌐 Scopra chi siamo, i nostri immobili e le nostre recensioni sulla nostra Pagina Facebook ufficiale:
https://www.facebook.com/immobiliaregiancani.it

📺 Ci può seguire e contattare anche sul nostro Canale YouTube ufficiale:
https://youtube.com/@immobiliaregiancani

📱 Se Le fa piacere un colloquio conoscitivo senza alcun impegno, può rispondermi qui su WhatsApp o chiamarmi direttamente al +39 320 166 7156.

Un caro saluto ✨
Antonio Giancani
— Immobiliare Giancani`;

    let DATASET = {json_dataset_str};
    let MEMORIA_CLOUD_INIZIALE = {json_memoria_str};
    const ORDINE_COMUNI = ['Favara', 'Aragona', 'Agrigento', 'Comitini', 'Porto Empedocle', 'Siculiana', 'Realmonte'];
    let paginaCorrente = 'numeri';
    let comuneGlobale = 'TUTTI';
    let filtroStatoNumeri = 'DA_CONTATTARE';
    let soloRibassiAgenzie = false;
    let saltatiSessione = [];
    let comuniSaltatiSessione = [];

    // Gestione Memoria 30 Giorni (LocalStorage + Cloud Sync) e Sblocco Sospetti->Privati
    function caricaMemoria30Giorni() {{
      let mem = Object.assign({{}}, MEMORIA_CLOUD_INIZIALE);
      try {{
        const localRaw = localStorage.getItem('GIANCANI_MEMORIA_30GG');
        if (localRaw) {{
          const localObj = JSON.parse(localRaw);
          Object.assign(mem, localObj);
        }}
      }} catch (e) {{}}

      // Pulizia automatica contatti che hanno superato 1 mese (30 giorni)
      const nowMs = Date.now();
      let attiva = {{}};
      let cambiato = false;
      for (const k in mem) {{
        const rec = mem[k];
        const ts = rec.timestamp_ms || 0;
        if (ts && (nowMs - ts < MS_30_GIORNI)) {{
          const ggPassati = Math.floor((nowMs - ts) / (24 * 60 * 60 * 1000));
          rec.giorni_rimanenti = Math.max(1, GIORNI_SCADENZA - ggPassati);
          attiva[k] = rec;
        }} else {{
          cambiato = true;
        }}
      }}
      if (cambiato) {{
        try {{
          localStorage.setItem('GIANCANI_MEMORIA_30GG', JSON.stringify(attiva));
        }} catch (e) {{}}
      }}
      return attiva;
    }}

    function normalizzaTelefonoChiave(tel) {{
      let digits = (tel || '').replace(/\\D/g, '');
      if (digits.startsWith('0039') && digits.length > 12) {{
        digits = digits.slice(4);
      }} else if (digits.startsWith('39') && digits.length > 10) {{
        digits = digits.slice(2);
      }}
      return digits;
    }}

    function getStatoMemoriaItem(item, mem) {{
      const telRaw = (item.telefono || '').replace(/\\D/g, '');
      const telClean = normalizzaTelefonoChiave(telRaw);
      const emClean = (item.email_contatto || '').toLowerCase().trim();
      return mem[item.id]
        || (telClean.length >= 8 ? mem['TEL_' + telClean] : null)
        || (telRaw.length >= 8 ? mem['TEL_' + telRaw] : null)
        || (emClean ? mem['EMAIL_' + emClean] : null)
        || null;
    }}

    function registraInvioInMemoria30Giorni(item, canale) {{
      const mem = caricaMemoria30Giorni();
      const now = new Date();
      const dateStr = now.toLocaleDateString('it-IT') + ' ' + now.toLocaleTimeString('it-IT').slice(0, 5);
      const telRaw = (item.telefono || '').replace(/\\D/g, '');
      const telClean = normalizzaTelefonoChiave(telRaw);
      const emClean = (item.email_contatto || '').toLowerCase().trim();

      const rec = {{
        id: item.id,
        telefono: telClean,
        email_contatto: emClean,
        nome: item.nome_privato,
        comune: item.comune,
        canale: canale,
        data_invio: dateStr,
        timestamp_ms: now.getTime(),
        giorni_rimanenti: GIORNI_SCADENZA
      }};

      mem[item.id] = rec;
      if (telClean.length >= 8) mem['TEL_' + telClean] = rec;
      if (emClean) mem['EMAIL_' + emClean] = rec;

      try {{
        localStorage.setItem('GIANCANI_MEMORIA_30GG', JSON.stringify(mem));
      }} catch (e) {{}}

      // Invia in background anche al Cloud Google Sheet (Apps Script)
      try {{
        fetch(WEBHOOK_URL, {{
          method: 'POST',
          mode: 'no-cors',
          headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
          body: JSON.stringify(Object.assign({{ action: 'registra_invio_presentazione' }}, rec))
        }});
      }} catch (e) {{}}

      renderTutto();
    }}

    function segnaContattatoQualsiasiCanale(itemId, canale) {{
      const item = DATASET.find(x => x.id === itemId);
      if (!item) return;
      registraInvioInMemoria30Giorni(item, canale || 'CONTATTO_DIRETTO');
    }}

    function sbloccaContattoMemoria(itemId, telefono) {{
      const mem = caricaMemoria30Giorni();
      delete mem[itemId];
      const telRaw = (telefono || '').replace(/\\D/g, '');
      const telClean = normalizzaTelefonoChiave(telRaw);
      if (telClean) delete mem['TEL_' + telClean];
      if (telRaw) delete mem['TEL_' + telRaw];
      delete MEMORIA_CLOUD_INIZIALE[itemId];
      if (telClean) delete MEMORIA_CLOUD_INIZIALE['TEL_' + telClean];
      if (telRaw) delete MEMORIA_CLOUD_INIZIALE['TEL_' + telRaw];
      try {{
        localStorage.setItem('GIANCANI_MEMORIA_30GG', JSON.stringify(mem));
      }} catch (e) {{}}
      renderTutto();
    }}

    function promuoviSospettoAVeroPrivato(itemId) {{
      let promossi = [];
      try {{
        promossi = JSON.parse(localStorage.getItem('GIANCANI_PROMOSSI_PRIVATI') || '[]');
      }} catch (e) {{}}
      if (!promossi.includes(itemId)) promossi.push(itemId);
      try {{
        localStorage.setItem('GIANCANI_PROMOSSI_PRIVATI', JSON.stringify(promossi));
      }} catch (e) {{}}
      DATASET.forEach(it => {{
        if (it.id === itemId) it.cat = 'privato';
      }});
      renderTutto();
    }}

    function segnaComeAgenzia(itemId, telefono) {{
      let segnalateId = [];
      let segnalateTel = [];
      try {{
        segnalateId = JSON.parse(localStorage.getItem('GIANCANI_AGENZIE_SEGNALATE_ID') || '[]');
        segnalateTel = JSON.parse(localStorage.getItem('GIANCANI_AGENZIE_SEGNALATE_TEL') || '[]');
      }} catch (e) {{}}

      if (!segnalateId.includes(itemId)) segnalateId.push(itemId);
      const telClean = (telefono || '').replace(/\\D/g, '').replace(/^39/, '');
      if (telClean.length >= 8 && !segnalateTel.includes(telClean)) {{
        segnalateTel.push(telClean);
      }}

      try {{
        localStorage.setItem('GIANCANI_AGENZIE_SEGNALATE_ID', JSON.stringify(segnalateId));
        localStorage.setItem('GIANCANI_AGENZIE_SEGNALATE_TEL', JSON.stringify(segnalateTel));
      }} catch (e) {{}}

      applicaSegnalazioniAgenzieLocali();
      renderTutto();
    }}

    function applicaSegnalazioniAgenzieLocali() {{
      let segnalateId = [];
      let segnalateTel = ['3284670316'];
      try {{
        segnalateId = JSON.parse(localStorage.getItem('GIANCANI_AGENZIE_SEGNALATE_ID') || '[]');
        const extraTel = JSON.parse(localStorage.getItem('GIANCANI_AGENZIE_SEGNALATE_TEL') || '[]');
        segnalateTel = Array.from(new Set(segnalateTel.concat(extraTel)));
      }} catch (e) {{}}

      DATASET.forEach(it => {{
        const telClean = (it.telefono || '').replace(/\\D/g, '').replace(/^39/, '');
        if (segnalateId.includes(it.id) || (telClean.length >= 8 && segnalateTel.includes(telClean))) {{
          it.cat = 'agenzia';
          if (!it.nome_agenzia || it.nome_agenzia === 'Privato') {{
            it.nome_agenzia = telClean ? ('Agenzia (' + telClean + ')') : 'Agenzia Segnalata';
          }}
        }}
      }});
    }}

    function applicaPromossiLocali() {{
      try {{
        const promossi = JSON.parse(localStorage.getItem('GIANCANI_PROMOSSI_PRIVATI') || '[]');
        if (promossi.length) {{
          DATASET.forEach(it => {{
            if (promossi.includes(it.id)) it.cat = 'privato';
          }});
        }}
      }} catch (e) {{}}
      applicaSegnalazioniAgenzieLocali();
    }}

    const _memFallback = {{}};
    function safeStorageGet(k) {{
      try {{ return localStorage.getItem(k); }} catch (e) {{ return _memFallback[k] || null; }}
    }}
    function safeStorageSet(k, v) {{
      _memFallback[k] = v;
      try {{ localStorage.setItem(k, v); }} catch (e) {{}}
    }}

    function getYoutubeUrlConfig() {{
      return safeStorageGet('GIANCANI_YT_URL') || DEFAULT_YT_URL;
    }}

    function getTemplateMessaggioConfig() {{
      return safeStorageGet('GIANCANI_MSG_PRESENTAZIONE') || DEFAULT_TEMPLATE_WA;
    }}

    function toggleConfigBox() {{
      const el = document.getElementById('box-config-messaggio');
      el.classList.toggle('hidden');
    }}

    function salvaConfigPresentazione(mostraAlert) {{
      const yt = document.getElementById('cfg-youtube-url').value.trim() || DEFAULT_YT_URL;
      let msg = document.getElementById('cfg-messaggio-wa').value.trim() || DEFAULT_TEMPLATE_WA;
      if (!msg.includes('Immobiliare Giancani')) {{
        msg += '\\n— Immobiliare Giancani';
      }}
      try {{
        localStorage.setItem('GIANCANI_YT_URL', yt);
        localStorage.setItem('GIANCANI_MSG_PRESENTAZIONE', msg);
      }} catch (e) {{}}

      if (mostraAlert) {{
        try {{
          fetch(WEBHOOK_URL, {{
            method: 'POST',
            mode: 'no-cors',
            headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
            body: JSON.stringify({{
              action: 'salva_config_presentazione',
              youtube_url: yt,
              messaggio_wa: msg
            }})
          }});
        }} catch (e) {{}}
        alert('✅ Messaggio di presentazione e link video YouTube salvati in memoria!\\n\\n— Immobiliare Giancani');
        document.getElementById('box-config-messaggio').classList.add('hidden');
      }}
      renderTutto();
    }}

    function ripristinaMessaggioDefault() {{
      document.getElementById('cfg-youtube-url').value = DEFAULT_YT_URL;
      document.getElementById('cfg-messaggio-wa').value = DEFAULT_TEMPLATE_WA;
      salvaConfigPresentazione(true);
    }}

    function getSalutoOrario() {{
      const ora = new Date().getHours();
      if (ora < 13) return 'buongiorno ☀️';
      if (ora < 18) return 'buon pomeriggio 👋';
      return 'buonasera 🌙';
    }}

    function compilaMessaggioPerCliente(item) {{
      const ytUrl = getYoutubeUrlConfig();
      const tpl = getTemplateMessaggioConfig();
      const nome = (item.nome_privato && item.nome_privato !== 'Proprietario Privato') ? item.nome_privato : 'proprietario';
      const salutoOrario = getSalutoOrario();
      let msg = tpl
        .replace(/{{{{SALUTO_ORARIO}}}}/g, salutoOrario)
        .replace(/\\bbuongiorno\\b/i, salutoOrario)
        .replace(/{{{{NOME}}}}/g, nome)
        .replace(/{{{{COMUNE}}}}/g, item.comune || 'Agrigento')
        .replace(/{{{{VIA_ZONA}}}}/g, item.via_zona || item.titolo || '')
        .replace(/{{{{METRI_QUADRI}}}}/g, item.superficie || 'Non specificata')
        .replace(/{{{{PREZZO}}}}/g, item.prezzo || 'Su richiesta')
        .replace(/{{{{LINK_YOUTUBE}}}}/g, ytUrl);
      if (!msg.includes('Immobiliare Giancani')) {{
        msg += '\\n— Immobiliare Giancani';
      }}
      return msg;
    }}

    function azionaInvioWhatsApp1Click(itemId) {{
      const item = DATASET.find(x => x.id === itemId);
      if (!item) return;

      let telClean = (item.telefono || '').replace(/\\D/g, '');
      if (!telClean || telClean.length < 8) {{
        const inserito = prompt('Inserisci il numero di cellulare del proprietario visto sull\\'annuncio Subito.it:', '');
        if (!inserito) return;
        telClean = inserito.replace(/\\D/g, '');
        if (telClean.length < 8) return;
        item.telefono = telClean;
      }}
      if (telClean.startsWith('0')) telClean = '39' + telClean;
      else if (!telClean.startsWith('39')) telClean = '39' + telClean;

      const msg = compilaMessaggioPerCliente(item);
      const waUrl = `https://api.whatsapp.com/send?phone=${{telClean}}&text=${{encodeURIComponent(msg)}}`;

      // Registra subito in memoria per 30 giorni (1 mese)
      registraInvioInMemoria30Giorni(item, 'WHATSAPP');

      // Apre direttamente l'app WhatsApp sul cellulare o WhatsApp Desktop
      window.open(waUrl, '_blank');
    }}

    function azionaInvioEmail1Click(itemId) {{
      const item = DATASET.find(x => x.id === itemId);
      if (!item) return;

      let emailDest = (item.email_contatto || '').trim();
      if (!emailDest || !emailDest.includes('@')) {{
        const inserita = prompt('Inserisci l\\'indirizzo email del proprietario:', '');
        if (!inserita || !inserita.includes('@')) return;
        emailDest = inserita.trim();
        item.email_contatto = emailDest;
      }}

      const msg = compilaMessaggioPerCliente(item);
      const oggetto = `Proposta di collaborazione per la vendita del Suo immobile a ${{item.comune}} — Immobiliare Giancani`;

      // Invia anche tramite server Google Apps Script in background
      try {{
        fetch(WEBHOOK_URL, {{
          method: 'POST',
          mode: 'no-cors',
          headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
          body: JSON.stringify({{
            action: 'invia_email_presentazione',
            id: item.id,
            telefono: item.telefono,
            email_contatto: emailDest,
            nome: item.nome_privato,
            comune: item.comune,
            oggetto: oggetto,
            messaggio: msg
          }})
        }});
      }} catch (e) {{}}

      registraInvioInMemoria30Giorni(item, 'EMAIL');

      const mailtoUrl = `mailto:${{encodeURIComponent(emailDest)}}?subject=${{encodeURIComponent(oggetto)}}&body=${{encodeURIComponent(msg)}}`;
      window.location.href = mailtoUrl;
    }}

    function inviaEmailATutti1Click() {{
      const mem = caricaMemoria30Giorni();
      const tuttiPrivati = filtraPerComuneERicerca(DATASET.filter(x => x.cat === 'privato'));
      const daInviare = tuttiPrivati.filter(x => (x.email_contatto && x.email_contatto.includes('@')) && !getStatoMemoriaItem(x, mem));

      if (daInviare.length === 0) {{
        alert('ℹ️ Nessuna email da inviare al momento (o sono già tutte in memoria per 30 giorni).\\n\\n— Immobiliare Giancani');
        return;
      }}

      if (!confirm(`Vuoi inviare la presentazione con 1 click a tutti i ${{daInviare.length}} proprietari con email disponibile?\\n(Ogni contatto verrà memorizzato per 30 giorni)`)) {{
        return;
      }}

      daInviare.forEach(item => {{
        const msg = compilaMessaggioPerCliente(item);
        const oggetto = `Proposta di collaborazione per la vendita del Suo immobile a ${{item.comune}} — Immobiliare Giancani`;
        try {{
          fetch(WEBHOOK_URL, {{
            method: 'POST',
            mode: 'no-cors',
            headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
            body: JSON.stringify({{
              action: 'invia_email_presentazione',
              id: item.id,
              telefono: item.telefono,
              email_contatto: item.email_contatto,
              nome: item.nome_privato,
              comune: item.comune,
              oggetto: oggetto,
              messaggio: msg
            }})
          }});
        }} catch (e) {{}}
        registraInvioInMemoria30Giorni(item, 'EMAIL');
      }});

      alert(`✅ Inviate ${{daInviare.length}} email di presentazione e memorizzate per 30 giorni!\\n\\n— Immobiliare Giancani`);
    }}

    async function sincronizzaMemoriaCloud(mostraNotifica) {{
      try {{
        const r = await fetch(WEBHOOK_URL + '?action=get_memoria_contatti');
        if (r.ok) {{
          const data = await r.json();
          if (data && data.memoria) {{
            const localMem = caricaMemoria30Giorni();
            Object.assign(localMem, data.memoria);
            localStorage.setItem('GIANCANI_MEMORIA_30GG', JSON.stringify(localMem));
            renderTutto();
            if (mostraNotifica) alert('✅ Memoria contatti 30 giorni sincronizzata con il Cloud Google Sheet!\\n\\n— Immobiliare Giancani');
          }}
        }}
      }} catch (e) {{
        if (mostraNotifica) alert('ℹ️ Memoria locale sul cellulare già attiva e sincronizzata.\\n\\n— Immobiliare Giancani');
      }}
    }}

    function caricaVisti() {{
      try {{
        return JSON.parse(localStorage.getItem('GIANCANI_IMMOBILI_VISTI') || '[]');
      }} catch (e) {{
        return [];
      }}
    }}

    function segnaComeVisto(itemId) {{
      const visti = caricaVisti();
      if (!visti.includes(itemId)) visti.push(itemId);
      try {{
        localStorage.setItem('GIANCANI_IMMOBILI_VISTI', JSON.stringify(visti));
      }} catch (e) {{}}
      renderTutto();
    }}

    function rimuoviDaVisti(itemId) {{
      const visti = caricaVisti().filter(id => id !== itemId);
      try {{
        localStorage.setItem('GIANCANI_IMMOBILI_VISTI', JSON.stringify(visti));
      }} catch (e) {{}}
      renderTutto();
    }}

    function cambiaPagina(p) {{
      paginaCorrente = p;
      ['numeri', 'privati', 'sospetti', 'agenzie', 'portali', 'statistiche', 'visti'].forEach(k => {{
        document.getElementById('page-' + k).classList.toggle('hidden', k !== p);
        document.getElementById('nav-' + k).classList.toggle('tab-active', k === p);
      }});
      renderTutto();
    }}

    function setComuneGlobale(com) {{
      comuneGlobale = com;
      document.querySelectorAll('.com-pill').forEach(btn => {{
        btn.className = 'com-pill bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-3 py-1.5 rounded-xl';
      }});
      const target = document.getElementById('btn-com-' + com);
      if (target) target.className = 'com-pill bg-slate-900 text-amber-400 text-xs font-black px-3 py-1.5 rounded-xl';
      renderTutto();
    }}

    function setFiltroStatoNumeri(st) {{
      filtroStatoNumeri = st;
      renderNumeriPrivati();
    }}

    function toggleSoloRibassiAgenzie() {{
      soloRibassiAgenzie = !soloRibassiAgenzie;
      const btn = document.getElementById('btn-solo-ribassi-ag');
      if (soloRibassiAgenzie) {{
        btn.className = 'bg-amber-400 text-slate-950 text-xs font-black px-4 py-2.5 rounded-xl shadow ring-2 ring-white';
        btn.innerText = '✅ Filtro Attivo: Solo Agenzie con Ribasso';
      }} else {{
        btn.className = 'bg-rose-600 hover:bg-rose-500 text-white text-xs font-black px-4 py-2.5 rounded-xl shadow';
        btn.innerText = '📉 Mostra Solo Immobili con Ribasso';
      }}
      renderAgenzie();
    }}

    function filtraPerComuneERicerca(lista) {{
      const q = (document.getElementById('ricerca-globale').value || '').toLowerCase().trim();
      return lista.filter(it => {{
        const matchCom = (comuneGlobale === 'TUTTI') || (it.comune || '').toLowerCase().includes(comuneGlobale.toLowerCase());
        if (!matchCom) return false;
        if (!q) return true;
        const blob = `${{it.comune}} ${{it.titolo}} ${{it.via_zona}} ${{it.nome_privato}} ${{it.nome_agenzia}} ${{it.telefono}} ${{it.email_contatto}} ${{it.descrizione}} ${{it.prezzo}}`.toLowerCase();
        return blob.includes(q);
      }});
    }}

    function getIndiceOrdineComune(comune) {{
      const cLow = (comune || '').toLowerCase();
      for (let i = 0; i < ORDINE_COMUNI.length; i++) {{
        if (cLow.includes(ORDINE_COMUNI[i].toLowerCase())) return i;
      }}
      return 99;
    }}

    function saltaContattoCorrente(itemId) {{
      if (!saltatiSessione.includes(itemId)) saltatiSessione.push(itemId);
      renderNumeriPrivati();
    }}

    function saltaComuneCorrente(comuneNome) {{
      const cLow = (comuneNome || '').toLowerCase();
      if (!comuniSaltatiSessione.includes(cLow)) comuniSaltatiSessione.push(cLow);
      renderNumeriPrivati();
    }}

    function resetSaltatiSessione() {{
      saltatiSessione = [];
      comuniSaltatiSessione = [];
      renderNumeriPrivati();
    }}

    function renderNumeriPrivati() {{
      const mem = caricaMemoria30Giorni();
      const vistiIds = caricaVisti();
      const tuttiPrivati = filtraPerComuneERicerca(DATASET.filter(x => x.cat === 'privato' && !vistiIds.includes(x.id)));

      // Ordina rigorosamente:
      // 1) Prima quelli con WhatsApp attivo (telefono presente)
      // 2) Subito dopo quelli con Email (email_contatto presente)
      // 3) Poi per Paese (Favara -> Aragona -> Agrigento -> Comitini -> Porto Empedocle -> Siculiana -> Realmonte)
      tuttiPrivati.sort((a, b) => {{
        const aWa = (a.telefono && a.telefono.trim().length >= 8) ? 1 : 0;
        const bWa = (b.telefono && b.telefono.trim().length >= 8) ? 1 : 0;
        if (bWa !== aWa) return bWa - aWa;
        const aEm = (a.email_contatto && a.email_contatto.includes('@')) ? 1 : 0;
        const bEm = (b.email_contatto && b.email_contatto.includes('@')) ? 1 : 0;
        if (bEm !== aEm) return bEm - aEm;
        const ordA = getIndiceOrdineComune(a.comune);
        const ordB = getIndiceOrdineComune(b.comune);
        if (ordA !== ordB) return ordA - ordB;
        return (b.timestamp || '').localeCompare(a.timestamp || '');
      }});

      const daContattareConRecapito = tuttiPrivati.filter(x => (x.telefono || x.email_contatto) && !getStatoMemoriaItem(x, mem));
      const codaAttiva = daContattareConRecapito.filter(x =>
        !saltatiSessione.includes(x.id) &&
        !comuniSaltatiSessione.some(cs => (x.comune || '').toLowerCase().includes(cs))
      );
      const emailPronteList = tuttiPrivati.filter(x => (x.email_contatto && x.email_contatto.includes('@')) && !getStatoMemoriaItem(x, mem));
      const inMemoriaList = tuttiPrivati.filter(x => !!getStatoMemoriaItem(x, mem));

      const btnAllEmail = document.getElementById('btn-invia-tutte-email');
      const lblAllEmail = document.getElementById('lbl-invia-tutte-email');
      if (btnAllEmail && lblAllEmail) {{
        lblAllEmail.innerText = `✉️ INVIA EMAIL A TUTTI CON 1 CLICK (${{emailPronteList.length}})`;
        if (emailPronteList.length > 0) {{
          btnAllEmail.className = 'bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs px-4 py-3 rounded-xl shadow-md flex items-center gap-2 transition';
        }} else {{
          btnAllEmail.className = 'bg-slate-200 text-slate-400 font-bold text-xs px-4 py-3 rounded-xl flex items-center gap-2 cursor-not-allowed';
        }}
      }}

      document.getElementById('kpi-da-contattare').innerText = daContattareConRecapito.length;
      document.getElementById('kpi-in-memoria').innerText = inMemoriaList.length;
      document.getElementById('kpi-tutti-numeri').innerText = tuttiPrivati.length;
      document.getElementById('badge-numeri').innerText = daContattareConRecapito.length;

      // Render Card Coda Sequenziale 1-Click per Cellulare (Favara -> Aragona -> Agrigento -> ...)
      const boxCoda = document.getElementById('card-coda-cellulare');
      if (codaAttiva.length > 0) {{
        const curr = codaAttiva[0];
        const rimanentiNelPaese = codaAttiva.filter(x => (x.comune || '').toLowerCase() === (curr.comune || '').toLowerCase()).length;
        const msgPreview = compilaMessaggioPerCliente(curr);
        boxCoda.innerHTML = `
          <div class="flex flex-wrap justify-between items-center gap-2 mb-3">
            <div class="flex flex-wrap items-center gap-2">
              <span class="bg-amber-400 text-slate-950 text-xs font-black px-3 py-1 rounded-full">
                📍 PAESE ATTUALE: ${{(curr.comune || '').toUpperCase()}} (${{rimanentiNelPaese}} rimasti)
              </span>
              <span class="bg-emerald-500 text-slate-950 text-xs font-black px-3 py-1 rounded-full animate-pulse">
                🚀 Coda Totale: ${{codaAttiva.length}}
              </span>
            </div>
            <span class="text-xs text-emerald-300 font-bold">${{curr.superficie}} — ${{curr.prezzo}}</span>
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 items-center">
            <div class="lg:col-span-2 space-y-2">
              <div class="text-lg font-black text-white">
                👤 ${{curr.nome_privato}} • <span class="text-amber-400">📞 ${{curr.telefono || 'Email: ' + curr.email_contatto}}</span>
              </div>
              <div class="text-xs text-slate-300 font-semibold">🏠 ${{curr.titolo}} (${{curr.via_zona}})</div>
              <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800 text-[11px] text-slate-300 font-mono whitespace-pre-line max-h-36 overflow-y-auto">${{msgPreview}}</div>
            </div>
            <div class="flex flex-col gap-2">
              ${{curr.telefono ? `
              <button onclick="azionaInvioWhatsApp1Click('${{curr.id}}')" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-sm py-3.5 px-4 rounded-2xl shadow-xl flex items-center justify-center gap-2 transition transform active:scale-95">
                <i class="fa-brands fa-whatsapp text-xl"></i>
                <span>INVIA SU APP WHATSAPP (1-CLICK)</span>
              </button>
              ` : ''}}
              ${{curr.email_contatto ? `
              <button onclick="azionaInvioEmail1Click('${{curr.id}}')" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-black text-xs py-3 px-4 rounded-2xl shadow flex items-center justify-center gap-2">
                <i class="fa-solid fa-envelope"></i>
                <span>INVIA PRESENTAZIONE VIA EMAIL (${{curr.email_contatto}})</span>
              </button>
              ` : ''}}
              <button onclick="segnaContattatoQualsiasiCanale('${{curr.id}}', 'CONTATTO_DIRETTO')" class="w-full bg-teal-600 hover:bg-teal-500 text-white font-black text-xs py-2.5 px-4 rounded-xl shadow flex items-center justify-center gap-2">
                <span>✅ Già Contattato (Qualsiasi Canale • Nascondi 30gg)</span>
              </button>
              <div class="grid grid-cols-2 gap-2">
                <button onclick="saltaContattoCorrente('${{curr.id}}')" class="bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs py-2.5 px-3 rounded-xl border border-slate-700">
                  ⏭️ Salta Cliente
                </button>
                <button onclick="saltaComuneCorrente('${{curr.comune}}')" class="bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs py-2.5 px-3 rounded-xl">
                  ⏭️ Salta Paese
                </button>
              </div>
              <a href="${{curr.url}}" target="_blank" class="w-full text-center bg-slate-800 hover:bg-slate-700 text-amber-400 font-bold text-xs py-2 px-4 rounded-xl border border-slate-700">
                🌐 Vedi Scheda Annuncio Originale
              </a>
            </div>
          </div>
        `;
      }} else {{
        boxCoda.innerHTML = `
          <div class="text-center py-4 space-y-2">
            <div class="text-emerald-400 font-black text-base">✅ Coda completata per i paesi selezionati!</div>
            <p class="text-xs text-slate-300">I contatti inviati restano bloccati in memoria per 30 giorni. ${{(saltatiSessione.length > 0 || comuniSaltatiSessione.length > 0) ? '<button onclick="resetSaltatiSessione()" class="underline text-amber-400 font-bold ml-1">Ripristina contatti/paesi saltati</button>' : ''}}</p>
          </div>
        `;
      }}

      // Filtra lista secondo lo stato selezionato
      let listaFiltrata = tuttiPrivati;
      if (filtroStatoNumeri === 'DA_CONTATTARE') {{
        listaFiltrata = tuttiPrivati.filter(x => !getStatoMemoriaItem(x, mem));
      }} else if (filtroStatoNumeri === 'IN_MEMORIA_30GG') {{
        listaFiltrata = inMemoriaList;
      }}

      const container = document.getElementById('lista-numeri-privati');
      if (listaFiltrata.length === 0) {{
        container.innerHTML = `<div class="p-8 text-center text-xs text-slate-500 font-bold">Nessun contatto in questa vista per il filtro selezionato. — Immobiliare Giancani</div>`;
        return;
      }}

      container.innerHTML = listaFiltrata.map((it, idx) => {{
        const statoMem = getStatoMemoriaItem(it, mem);
        const badgeStato = statoMem
          ? `<span class="bg-amber-100 text-amber-800 border border-amber-300 text-[10px] font-black px-2.5 py-1 rounded-full">
               ✅ Inviato (${{statoMem.canale}}) il ${{statoMem.data_invio}} • Si sblocca tra ${{statoMem.giorni_rimanenti}} gg
             </span>`
          : `<span class="bg-emerald-100 text-emerald-800 border border-emerald-300 text-[10px] font-black px-2.5 py-1 rounded-full">
               🟢 Da Contattare
             </span>`;

        const hasWa = !!(it.telefono && it.telefono.trim().length >= 8);
        const hasEmail = !!(it.email_contatto && it.email_contatto.includes('@'));

        const btnWaCls = hasWa
          ? 'flex-1 md:flex-none bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs px-4 py-3 rounded-xl shadow flex items-center justify-center gap-1.5 transition'
          : 'flex-1 md:flex-none bg-slate-200 hover:bg-slate-300 text-slate-500 font-bold text-xs px-4 py-3 rounded-xl flex items-center justify-center gap-1.5 transition';

        const btnEmailCls = hasEmail
          ? 'bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs px-3.5 py-3 rounded-xl shadow flex items-center gap-1 transition'
          : 'bg-slate-200 hover:bg-slate-300 text-slate-500 font-bold text-xs px-3.5 py-3 rounded-xl flex items-center gap-1 transition';

        const btnWaLabel = hasWa
          ? `📲 WhatsApp (${{it.telefono}})`
          : `📲 WhatsApp (Assente)`;

        return `
        <div class="p-4 hover:bg-slate-50 transition flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div class="space-y-1 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-black text-slate-400">#${{idx + 1}}</span>
              <span class="text-sm font-black text-slate-900">👤 ${{it.nome_privato}}</span>
              <span class="text-xs font-black text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-lg">📍 ${{it.comune}}</span>
              ${{badgeStato}}
            </div>
            <div class="text-xs font-bold text-slate-800">${{it.titolo}} — <span class="text-emerald-700">${{it.prezzo}}</span> (<span class="text-slate-600">${{it.superficie}}</span>)</div>
            <div class="text-[11px] text-slate-500 line-clamp-3">📄 Colonna F: ${{it.descrizione}}</div>
          </div>

          <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
            <button onclick="azionaInvioWhatsApp1Click('${{it.id}}')" class="${{btnWaCls}}">
              <i class="fa-brands fa-whatsapp text-base"></i>
              <span>${{btnWaLabel}}</span>
            </button>
            <button onclick="azionaInvioEmail1Click('${{it.id}}')" class="${{btnEmailCls}}">
              <i class="fa-solid fa-envelope"></i>
              <span>${{hasEmail ? 'Email (' + it.email_contatto + ')' : 'Email (Assente)'}}</span>
            </button>
            ${{it.telefono ? `
            <a href="tel:+39${{it.telefono.replace(/\\D/g, '')}}" class="bg-amber-100 hover:bg-amber-200 text-amber-900 font-black text-xs px-3.5 py-3 rounded-xl">
              📞 Chiama
            </a>` : ''}}
            <a href="${{it.url}}" target="_blank" class="bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs px-3.5 py-3 rounded-xl">
              🌐 Annuncio
            </a>
            <button onclick="segnaComeVisto('${{it.id}}')" class="bg-sky-100 hover:bg-sky-200 text-sky-900 font-bold text-[11px] px-3 py-2.5 rounded-xl border border-sky-300">
              👁️ Visto
            </button>
            ${{!statoMem ? `
            <button onclick="segnaContattatoQualsiasiCanale('${{it.id}}', 'CONTATTO_DIRETTO')" class="bg-teal-100 hover:bg-teal-200 text-teal-900 font-black text-[11px] px-3 py-2.5 rounded-xl border border-teal-300">
              ✅ Già Contattato (30gg)
            </button>` : ''}}
            <label class="inline-flex items-center gap-1.5 bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-800 font-bold text-[11px] px-2.5 py-2.5 rounded-xl cursor-pointer">
              <input type="checkbox" onchange="if(this.checked) segnaComeAgenzia('${{it.id}}', '${{it.telefono}}')" class="accent-rose-600 w-4 h-4">
              <span>È Agenzia</span>
            </label>
            ${{statoMem ? `
            <button onclick="sbloccaContattoMemoria('${{it.id}}', '${{it.telefono}}')" title="Azzera subito il blocco di 30 giorni" class="text-[11px] text-red-600 hover:underline font-bold px-2 py-1">
              🔄 Sblocca
            </button>` : ''}}
          </div>
        </div>
        `;
      }}).join('');
    }}

    function cardImmobileHTML(it, tipoCard, mem) {{
      const statoMem = getStatoMemoriaItem(it, mem);
      const isSospetto = (tipoCard === 'sospetto');
      const isAgenzia = (tipoCard === 'agenzia');

      let badgeTop = `<span class="bg-emerald-600 text-white text-[11px] font-black px-2.5 py-1 rounded-full shadow">👤 ${{it.nome_privato}} (PRIVATO)</span>`;
      if (isSospetto) {{
        badgeTop = `<span class="bg-amber-500 text-slate-950 text-[11px] font-black px-2.5 py-1 rounded-full shadow">🕵️ SOSPETTO AGENZIA (${{it.nome_privato}})</span>`;
      }} else if (isAgenzia) {{
        badgeTop = `<span class="bg-indigo-700 text-white text-[11px] font-black px-2.5 py-1 rounded-full shadow">🏢 ${{it.nome_agenzia.slice(0, 26)}}</span>`;
      }}

      let ribassoBox = '';
      if (it.ha_ribasso || it.ribasso_importo < 0) {{
        ribassoBox = `
        <div class="bg-rose-50 border border-rose-300 text-rose-800 p-2.5 rounded-xl text-xs font-black flex justify-between items-center">
          <span>📉 RIBASSO RILEVATO: ${{it.ribasso_importo}} € (${{it.ribasso_percentuale}}%)</span>
          <span class="line-through text-slate-400 text-[11px]">Prima: ${{it.prezzo_iniziale}}</span>
        </div>`;
      }}

      let sospettoBox = '';
      if (isSospetto) {{
        sospettoBox = `
        <div class="bg-amber-50 border border-amber-300 text-amber-900 p-2.5 rounded-xl text-[11px] space-y-1.5">
          <div><strong>⚠️ Motivo Sospetto:</strong> ${{it.motivo_sospetto}}</div>
          <button onclick="promuoviSospettoAVeroPrivato('${{it.id}}')" class="bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-[11px] px-3 py-1 rounded-lg">
            ✅ È un Vero Privato (Sposta nei Privati)
          </button>
        </div>`;
      }}

      return `
      <article class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden flex flex-col justify-between">
        <div>
          <div class="relative h-48 bg-slate-900">
            <img src="${{it.foto_url}}" alt="${{it.titolo}}" loading="lazy" class="w-full h-full object-cover" onerror="this.src='https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=500&auto=format&fit=crop&q=60'">
            <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">${{badgeTop}}</div>
            <div class="absolute bottom-2.5 right-2.5 bg-slate-950/90 text-white font-black text-sm px-3 py-1 rounded-xl border border-amber-400/40">
              ${{it.prezzo}}
            </div>
          </div>

          <div class="p-4 space-y-2.5">
            <div class="flex justify-between items-center text-[11px] text-slate-500 font-semibold">
              <span class="text-indigo-700 font-black uppercase">📍 ${{it.comune}}</span>
              <span>🕒 ${{it.timestamp}}</span>
            </div>

            <h3 class="font-black text-slate-900 text-base leading-snug">${{it.titolo}}</h3>
            <p class="text-xs text-slate-600 font-semibold">🛣️ ${{it.via_zona}}</p>

            ${{ribassoBox}}
            ${{sospettoBox}}

            <div class="flex flex-wrap gap-2 text-xs">
              <span class="bg-slate-100 text-slate-800 font-bold px-2.5 py-1 rounded-lg">📐 ${{it.superficie}}</span>
              <span class="bg-slate-100 text-slate-700 font-semibold px-2.5 py-1 rounded-lg">🏠 ${{it.tipologia}}</span>
              ${{it.telefono ? `<span class="bg-emerald-100 text-emerald-900 font-black px-2.5 py-1 rounded-lg">📞 ${{it.telefono}}</span>` : ''}}
            </div>

            <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-xs text-slate-700">
              <div class="font-bold text-slate-900 text-[11px] mb-1">📄 Testo Colonna F:</div>
              <p class="line-clamp-3 whitespace-pre-line">${{it.descrizione}}</p>
            </div>
          </div>
        </div>

        <div class="p-4 pt-0 space-y-2">
          ${{statoMem ? `
          <div class="text-[11px] bg-amber-50 text-amber-800 border border-amber-200 px-3 py-1.5 rounded-xl font-bold text-center">
            ✅ Presentazione inviata il ${{statoMem.data_invio}} (Rinvio tra ${{statoMem.giorni_rimanenti}} gg)
          </div>` : ''}}
          <div class="flex flex-wrap gap-2">
            ${{!isAgenzia ? `
            <button onclick="azionaInvioWhatsApp1Click('${{it.id}}')" class="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs py-2.5 px-3 rounded-xl transition">
              📲 WhatsApp + Video YT
            </button>
            <button onclick="azionaInvioEmail1Click('${{it.id}}')" class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-2.5 px-3 rounded-xl transition">
              ✉️ Email
            </button>
            ${{!statoMem ? `
            <button onclick="segnaContattatoQualsiasiCanale('${{it.id}}', 'CONTATTO_DIRETTO')" class="bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs py-2.5 px-3 rounded-xl transition">
              ✅ Contattato (30gg)
            </button>` : ''}}` : ''}}
            <a href="${{it.url}}" target="_blank" class="flex-1 text-center bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs py-2.5 px-3 rounded-xl transition">
              🌐 Annuncio
            </a>
          </div>
          <div class="text-[10px] text-right text-slate-400 font-bold">
            ID: ${{it.id}} • — Immobiliare Giancani
          </div>
        </div>
      </article>`;
    }}

    function renderPrivati() {{
      const mem = caricaMemoria30Giorni();
      const lista = filtraPerComuneERicerca(DATASET.filter(x => x.cat === 'privato' && !getStatoMemoriaItem(x, mem)));
      document.getElementById('badge-privati').innerText = lista.length;
      document.getElementById('griglia-privati').innerHTML = lista.map(it => cardImmobileHTML(it, 'privato', mem)).join('');
    }}

    function renderSospetti() {{
      const mem = caricaMemoria30Giorni();
      const lista = filtraPerComuneERicerca(DATASET.filter(x => x.cat === 'sospetto_agenzia' && !getStatoMemoriaItem(x, mem)));
      document.getElementById('badge-sospetti').innerText = lista.length;
      document.getElementById('griglia-sospetti').innerHTML = lista.map(it => cardImmobileHTML(it, 'sospetto', mem)).join('');
    }}

    function renderAgenzie() {{
      const mem = caricaMemoria30Giorni();
      let lista = filtraPerComuneERicerca(DATASET.filter(x => x.cat === 'agenzia'));

      // Popola menu a tendina dei nomi agenzie
      const selAg = document.getElementById('select-nome-agenzia');
      const agAttuale = selAg.value || 'TUTTE';
      const nomiAg = Array.from(new Set(DATASET.filter(x => x.cat === 'agenzia').map(x => x.nome_agenzia))).sort();
      if (selAg.options.length <= 1) {{
        nomiAg.forEach(n => {{
          const opt = document.createElement('option');
          opt.value = n;
          opt.innerText = n;
          selAg.appendChild(opt);
        }});
      }}

      if (agAttuale !== 'TUTTE') {{
        lista = lista.filter(x => x.nome_agenzia === agAttuale);
      }}
      if (soloRibassiAgenzie) {{
        lista = lista.filter(x => x.ha_ribasso || x.ribasso_importo < 0);
      }}

      document.getElementById('badge-agenzie').innerText = lista.length;
      if (lista.length === 0) {{
        document.getElementById('griglia-agenzie').innerHTML = `
          <div class="col-span-3 bg-white p-8 rounded-2xl text-center text-xs text-slate-500 font-bold border border-slate-200">
            ${{soloRibassiAgenzie ? 'Nessun ribasso di prezzo rilevato al momento per questo filtro. Il bot monitora i prezzi ogni ora e segnalerà qui ogni variazione al ribasso delle agenzie.' : 'Nessun annuncio agenzia per questo filtro.'}} — Immobiliare Giancani
          </div>`;
        return;
      }}
      document.getElementById('griglia-agenzie').innerHTML = lista.map(it => cardImmobileHTML(it, 'agenzia', mem)).join('');
    }}

    function parsePrezzoNumJS(str) {{
      const num = parseInt(String(str || '').replace(/[^0-9]/g, ''), 10);
      return (!isNaN(num) && num >= 1000) ? num : 0;
    }}

    function renderStatistiche() {{
      const box = document.getElementById('contenuto-statistiche');
      if (!box) return;
      const lista = filtraPerComuneERicerca(DATASET);

      // 1. Statistiche per Mesi
      const perMese = {{}};
      // 2. Statistiche per Portali
      const perPortale = {{}};
      // 3. Statistiche per Zone/Comuni e Prezzo Medio + Crescita
      const perZona = {{}};
      // 4. Statistiche per Fasce di Prezzo
      const fascePrezzo = {{ 'Fino a 50.000 €': 0, '50.000 - 100.000 €': 0, '100.000 - 200.000 €': 0, 'Oltre 200.000 €': 0, 'Su richiesta': 0 }};
      // 5. Statistiche Agenzie Immobiliari
      const statsAgenzie = {{}};

      lista.forEach(it => {{
        const mese = (it.timestamp || '').slice(0, 7) || 'N/D';
        perMese[mese] = (perMese[mese] || 0) + 1;

        const fonte = it.fonte || 'Subito.it';
        perPortale[fonte] = (perPortale[fonte] || 0) + 1;

        const pNum = parsePrezzoNumJS(it.prezzo);
        if (pNum === 0) fascePrezzo['Su richiesta']++;
        else if (pNum <= 50000) fascePrezzo['Fino a 50.000 €']++;
        else if (pNum <= 100000) fascePrezzo['50.000 - 100.000 €']++;
        else if (pNum <= 200000) fascePrezzo['100.000 - 200.000 €']++;
        else fascePrezzo['Oltre 200.000 €']++;

        const z = it.comune || 'Altro';
        if (!perZona[z]) perZona[z] = {{ tot: 0, privati: 0, agenzie: 0, sommaPrezzi: 0, cntPrezzi: 0 }};
        perZona[z].tot++;
        if (it.cat === 'privato') perZona[z].privati++;
        if (it.cat === 'agenzia') perZona[z].agenzie++;
        if (pNum > 0) {{ perZona[z].sommaPrezzi += pNum; perZona[z].cntPrezzi++; }}

        if (it.cat === 'agenzia') {{
          const ag = it.nome_agenzia || 'Agenzia';
          if (!statsAgenzie[ag]) statsAgenzie[ag] = {{ tot: 0, ribassi: 0, sommaPrezzi: 0, cntPrezzi: 0, zone: new Set() }};
          statsAgenzie[ag].tot++;
          if (it.ha_ribasso || it.ribasso_importo < 0) statsAgenzie[ag].ribassi++;
          if (pNum > 0) {{ statsAgenzie[ag].sommaPrezzi += pNum; statsAgenzie[ag].cntPrezzi++; }}
          statsAgenzie[ag].zone.add(z);
        }}
      }});

      const mesiOrdinati = Object.keys(perMese).sort().reverse();
      const maxMese = Math.max(1, ...Object.values(perMese));

      const righeMesi = mesiOrdinati.map(m => {{
        const perc = Math.round((perMese[m] / maxMese) * 100);
        return `
        <div class="space-y-1">
          <div class="flex justify-between text-xs font-bold">
            <span>📅 ${{m}}</span>
            <span class="text-amber-600">${{perMese[m]}} annunci</span>
          </div>
          <div class="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
            <div class="bg-amber-500 h-3 rounded-full" style="width:${{perc}}%"></div>
          </div>
        </div>`;
      }}).join('');

      const righePortali = Object.entries(perPortale).map(([k, v]) => `
        <div class="flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs font-bold">
          <span>🌐 ${{k}}</span>
          <span class="bg-slate-900 text-amber-400 px-3 py-1 rounded-full">${{v}} annunci</span>
        </div>`).join('');

      const righeFasce = Object.entries(fascePrezzo).map(([k, v]) => `
        <div class="flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs font-bold">
          <span>💰 ${{k}}</span>
          <span class="bg-emerald-700 text-white px-3 py-1 rounded-full">${{v}}</span>
        </div>`).join('');

      const zoneOrdinate = Object.entries(perZona).sort((a, b) => b[1].tot - a[1].tot);
      const righeZone = zoneOrdinate.map(([z, st]) => {{
        const pMedio = st.cntPrezzi > 0 ? Math.round(st.sommaPrezzi / st.cntPrezzi).toLocaleString('it-IT') + ' €' : 'N/D';
        const trend = st.tot >= 50 ? '🔥 In Forte Crescita' : (st.tot >= 20 ? '📈 Attiva' : '🟢 Stabile');
        return `
        <tr class="border-b border-slate-100 text-xs">
          <td class="py-2.5 px-3 font-black text-slate-900">📍 ${{z}}</td>
          <td class="py-2.5 px-3 font-bold">${{st.tot}}</td>
          <td class="py-2.5 px-3 text-emerald-700 font-bold">${{st.privati}}</td>
          <td class="py-2.5 px-3 text-indigo-700 font-bold">${{st.agenzie}}</td>
          <td class="py-2.5 px-3 font-black">${{pMedio}}</td>
          <td class="py-2.5 px-3 font-bold">${{trend}}</td>
        </tr>`;
      }}).join('');

      const agenzieOrdinate = Object.entries(statsAgenzie).sort((a, b) => b[1].tot - a[1].tot).slice(0, 20);
      const righeAgenzie = agenzieOrdinate.map(([ag, st]) => {{
        const pMedio = st.cntPrezzi > 0 ? Math.round(st.sommaPrezzi / st.cntPrezzi).toLocaleString('it-IT') + ' €' : 'N/D';
        return `
        <tr class="border-b border-slate-100 text-xs">
          <td class="py-2.5 px-3 font-black text-slate-900">🏢 ${{ag}}</td>
          <td class="py-2.5 px-3 font-bold">${{st.tot}}</td>
          <td class="py-2.5 px-3 text-rose-600 font-black">${{st.ribassi}}</td>
          <td class="py-2.5 px-3 font-bold">${{pMedio}}</td>
          <td class="py-2.5 px-3 text-slate-600">${{Array.from(st.zone).join(', ')}}</td>
        </tr>`;
      }}).join('');

      box.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-3">
            <h3 class="font-black text-slate-900 text-sm">📅 Pubblicazioni per Mese</h3>
            ${{righeMesi}}
          </div>
          <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-3">
            <h3 class="font-black text-slate-900 text-sm">🌐 Distribuzione per Portali</h3>
            ${{righePortali}}
          </div>
          <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-3">
            <h3 class="font-black text-slate-900 text-sm">💰 Distribuzione per Fasce di Prezzo</h3>
            ${{righeFasce}}
          </div>
        </div>

        <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 overflow-x-auto">
          <h3 class="font-black text-slate-900 text-sm mb-3">📈 Zone in Crescita, Prezzi Medi &amp; Immobili</h3>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-slate-900 text-white text-[11px] uppercase">
                <th class="py-2.5 px-3 rounded-tl-xl">Zona / Comune</th>
                <th class="py-2.5 px-3">Totale Annunci</th>
                <th class="py-2.5 px-3">Privati</th>
                <th class="py-2.5 px-3">Agenzie</th>
                <th class="py-2.5 px-3">Prezzo Medio</th>
                <th class="py-2.5 px-3 rounded-tr-xl">Andamento</th>
              </tr>
            </thead>
            <tbody>${{righeZone}}</tbody>
          </table>
        </div>

        <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 overflow-x-auto">
          <h3 class="font-black text-slate-900 text-sm mb-3">🏢 Statistiche Agenzie Immobiliari (Come Pubblicano, Zone &amp; Prezzi)</h3>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-indigo-950 text-white text-[11px] uppercase">
                <th class="py-2.5 px-3 rounded-tl-xl">Agenzia Immobiliare</th>
                <th class="py-2.5 px-3">Annunci</th>
                <th class="py-2.5 px-3">Ribassi</th>
                <th class="py-2.5 px-3">Prezzo Medio</th>
                <th class="py-2.5 px-3 rounded-tr-xl">Zone Coperte</th>
              </tr>
            </thead>
            <tbody>${{righeAgenzie}}</tbody>
          </table>
        </div>
      `;
    }}

    function renderVisti() {{
      const mem = caricaMemoria30Giorni();
      const vistiIds = caricaVisti();
      const lista = filtraPerComuneERicerca(DATASET.filter(x => vistiIds.includes(x.id)));
      document.getElementById('badge-visti').innerText = lista.length;
      const box = document.getElementById('griglia-visti');
      if (!box) return;
      if (lista.length === 0) {{
        box.innerHTML = `<div class="col-span-3 bg-white p-8 rounded-2xl text-center text-xs text-slate-500 font-bold border border-slate-200">Nessun immobile segnato come visto. Clicca su "👁️ Visto" su qualsiasi annuncio per spostarlo qui. — Immobiliare Giancani</div>`;
        return;
      }}
      box.innerHTML = lista.map(it => {{
        const card = cardImmobileHTML(it, it.cat === 'agenzia' ? 'agenzia' : 'privato', mem);
        return card.replace('ID: ' + it.id, `<button onclick="rimuoviDaVisti('${{it.id}}')" class="text-sky-700 hover:underline font-bold mr-2">↩️ Ripristina nei Nuovi</button> ID: ` + it.id);
      }}).join('');
    }}

    function renderTutto() {{
      applicaPromossiLocali();
      renderNumeriPrivati();
      renderPrivati();
      renderSospetti();
      renderAgenzie();
      renderStatistiche();
      renderVisti();
    }}

    window.onload = function() {{
      document.getElementById('cfg-youtube-url').value = getYoutubeUrlConfig();
      document.getElementById('cfg-messaggio-wa').value = getTemplateMessaggioConfig();
      renderTutto();
      sincronizzaMemoriaCloud(false);
    }};
  </script>
</body>
</html>
"""

    target_paths = [OUTPUT_HTML_DIR, OUTPUT_HTML_ROOT, OUTPUT_HTML_GITHUB]
    if output_path and output_path not in target_paths:
        target_paths.append(output_path)

    for p in target_paths:
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(full_html)
        except Exception as e:
            print(f"[HTML Generator] Errore scrittura {p}: {e} — Immobiliare Giancani")

    print(
        f"[HTML Generator] Console generata: {len(privati_puri)} Privati Verificati | "
        f"{len(sospetti_agenzie)} Sospetti Agenzie | {len(agenzie_immobiliari)} Agenzie. — Immobiliare Giancani"
    )
    return OUTPUT_HTML_DIR


if __name__ == "__main__":
    genera_html_resoconto()
