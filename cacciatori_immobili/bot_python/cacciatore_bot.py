#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
PROGETTO: "Cacciatori di Immobili" — Bot di Intelligence, Smistamento & Acquisizione
Brand: Immobiliare Giancani
Referente: Antonio Giancani (+39 320 166 7156)
Assistente AI 24/7: DarIA (+39 350 590 2923)

Funzionalità Principali:
1. Smistamento in 4 categorie:
   - NUMERI & EMAIL PRIVATI (Coda d'azione 1-Click WhatsApp/Email dal cellulare)
   - PRIVATI VERIFICATI
   - SOSPETTI AGENZIE (Falsi privati, intermediari multi-annuncio, aste camuffate)
   - AGENZIE IMMOBILIARI (Con monitoraggio continuo dei RIBASSI DI PREZZO)
2. Memoria Persistente 30 Giorni (1 Mese):
   - Ricorda ogni cliente già contattato e dopo 30 giorni azzera il blocco per un nuovo invio.
3. Report Giornaliero Telegram:
   - Comunica quanti nuovi numeri sono da contattare via WhatsApp o via Email e quanti
     hanno superato i 30 giorni, allegando link GitHub Pages e pagina HTML.
4. Regole Mandatorie:
   - Testi estratti e preservati dalla Colonna F.
   - Superfici sempre per esteso in "metri quadri".
   - Chiusura obbligatoria con "— Immobiliare Giancani".
=============================================================================
"""

import os
import sys
import json
import time
import re
import base64
import hashlib
import urllib.parse
from datetime import datetime, timedelta
import requests
import urllib3
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SESSION = requests.Session()
SESSION.verify = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DB_PATH = os.path.join(BASE_DIR, "cacciatore_db.json")

GITHUB_REPO_PAGES = os.getenv("GITHUB_REPO_PAGES", "giancaniimmobiliare2-droid/cacciatori-immobili-live")
GITHUB_PAGES_URL = f"https://giancaniimmobiliare2-droid.github.io/cacciatori-immobili-live/cacciatori.html"
GITHUB_API_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Caricamento configurazione
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
else:
    CONFIG = {}

CONFIG.setdefault("comuni_target", [
    "Favara", "Agrigento", "Aragona", "Comitini", "Porto Empedocle", "Siculiana", "Realmonte"
])
CONFIG.setdefault("telegram", {})
CONFIG["telegram"]["bot_token"] = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    CONFIG["telegram"].get("bot_token", "9268358897:AAE2OeJTfU5d05pQVWLe1EeJQPwLo470GVw")
)
CONFIG["telegram"]["chat_id"] = os.getenv(
    "TELEGRAM_CHAT_ID",
    CONFIG["telegram"].get("chat_id", "1723292483")
)
CONFIG.setdefault("google_apps_script", {})
CONFIG["google_apps_script"]["webhook_url"] = os.getenv(
    "APPS_SCRIPT_WEBHOOK_URL",
    CONFIG["google_apps_script"].get(
        "webhook_url",
        "https://script.google.com/macros/s/AKfycbwEeH82YCSoOc-KRZx6pSQa_k3Kb5i252_Ajljlo20IOBinGiqA1E0ZE_2gKljHpLu3/exec"
    )
)
CONFIG.setdefault("presentazione", {
    "youtube_url": "https://www.youtube.com/watch?v=TsdEk3Y9ewc",
    "giorni_memoria": 30
})

TARGET_COMUNI = [c.lower().strip() for c in CONFIG.get("comuni_target", [
    "Favara", "Agrigento", "Aragona", "Comitini", "Porto Empedocle", "Siculiana", "Realmonte"
])]

COMUNI_SUBITO_SLUGS = [
    ("Favara", "favara"),
    ("Agrigento", "agrigento"),
    ("Aragona", "aragona"),
    ("Comitini", "comitini"),
    ("Porto Empedocle", "porto-empedocle"),
    ("Siculiana", "siculiana"),
    ("Realmonte", "realmonte"),
]


def converti_abbreviazioni_metri_quadri(testo):
    """
    REGOLA MANDATORIA: Nelle descrizioni e nei testi, ogni abbreviazione
    (mq, mq., m², m2, MQ) viene convertita per esteso in 'metri quadri'.
    """
    if not testo:
        return ""
    risultato = re.sub(r'(\d)\s*(?:mq\.?|m²|m2)\b', r'\1 metri quadri', str(testo), flags=re.IGNORECASE)
    risultato = re.sub(r'\b(?:mq\.?|m2)\b|m²', 'metri quadri', risultato, flags=re.IGNORECASE)
    risultato = re.sub(r'\s+', ' ', risultato).strip()
    return risultato


def normalizza_metri_quadri(testo_mq):
    """
    REGOLA MANDATORIA: Converte qualsiasi indicazione di superficie rigorosamente in 'metri quadri'.
    """
    if not testo_mq:
        return "Non specificata"
    pulito = re.sub(r'(?i)mq\.?|m²|m2|MQ|metri\s+quadri', '', str(testo_mq)).strip()
    match = re.search(r'\d+', pulito)
    if match:
        return f"{match.group(0)} metri quadri"
    return f"{converti_abbreviazioni_metri_quadri(testo_mq)} metri quadri"


def sanitizza_testo_anti_pirata(testo):
    if not testo:
        return ""
    pulito = converti_abbreviazioni_metri_quadri(testo)
    pulito = str(pulito).replace(".", " ")
    pulito = re.sub(r'[^a-zA-Z0-9àèéìòùÀÈÉÌÒÙ\s-]', ' ', pulito)
    pulito = re.sub(r'\s+', ' ', pulito).strip()
    return pulito


def formatta_testo_colonna_f(descrizione_raw, titolo_fallback=""):
    """
    Prepara il testo integrale dell'annuncio destinato alla Colonna F (COL_F_TESTO_ORIGINALE),
    convertendo le superfici in 'metri quadri' e apponendo la firma obbligatoria '— Immobiliare Giancani'.
    """
    base = descrizione_raw.strip() if descrizione_raw else titolo_fallback.strip()
    if not base:
        base = "Immobile rilevato sul territorio"
    base = converti_abbreviazioni_metri_quadri(base)
    if "Immobiliare Giancani" not in base:
        base = f"{base} — Immobiliare Giancani"
    return base


def parse_prezzo_numerico(prezzo_str):
    if not prezzo_str:
        return 0
    cifre = re.sub(r'[^\d]', '', str(prezzo_str))
    try:
        val = int(cifre)
        return val if val >= 1000 else 0
    except Exception:
        return 0


def estrai_id_univoco_subito(ad_url, urn="", fallback_id=""):
    if ad_url:
        match_url = re.search(r'-(\d+)\.htm', str(ad_url))
        if match_url:
            return f"SUB-{match_url.group(1)}"
    if urn:
        match_urn = re.search(r':list:(\d+)', str(urn))
        if match_urn:
            return f"SUB-{match_urn.group(1)}"
        match_ad = re.search(r'id:ad:(\d+)', str(urn))
        if match_ad:
            return f"SUB-{match_ad.group(1)}"
    if ad_url:
        digest = hashlib.md5(str(ad_url).encode("utf-8")).hexdigest()[:12]
        return f"SUB-{digest}"
    return str(fallback_id or "SUB-UNKNOWN")


def estrai_via_zona(subject, body, comune):
    testo_ricerca = f"{subject or ''} {body or ''}"
    pattern_indirizzo = re.compile(
        r'\b((?:Via|Viale|Piazza|Piazzale|Corso|Contrada|C\.?da|C/da|Cortile|Vicolo|Largo|Discesa|Salita|Zona|Villaggio|Quartiere)\s+'
        r'[A-ZÀ-Úa-zà-ú0-9\'\.\s]{2,35})',
        re.IGNORECASE
    )
    match = pattern_indirizzo.search(testo_ricerca)
    if match:
        trovato = match.group(1).strip()
        trovato = re.split(r'[\n\r,;(\-\–]|(?:\s+a\s+)|(?:\s+in\s+)|(?:\s+proponiamo\s+)|(?:\s+vendesi\s+)', trovato, maxsplit=1)[0].strip()
        if len(trovato) >= 5:
            return converti_abbreviazioni_metri_quadri(trovato)
    return converti_abbreviazioni_metri_quadri(subject or f"Zona {comune}")


def estrai_telefono_da_testo(body):
    if not body:
        return ""
    pulito = re.sub(r'\(\d{8,}\)', '', str(body))
    pulito = re.sub(r'(?i)rif\.?\s*:?\s*\d+', '', pulito)
    match_cell = re.search(r'(?<!\d)((?:\+39[\s\.\-]?)?3\d{2}[\s\.\-/]?\d{3}[\s\.\-/]?\d{4})(?!\d)', pulito)
    if match_cell:
        return re.sub(r'[^\d\+]', '', match_cell.group(1))
    match_cell2 = re.search(r'(?<!\d)((?:\+39[\s\.\-]?)?3\d{1,2}[\s\.\-/]?\d{6,8})(?!\d)', pulito)
    if match_cell2:
        num = re.sub(r'[^\d\+]', '', match_cell2.group(1))
        if 9 <= len(num.replace("+39", "")) <= 10:
            return num
    match_fisso = re.search(r'(?<!\d)(0922[\s\.\-/]?\d{5,7})(?!\d)', pulito)
    if match_fisso:
        return re.sub(r'[^\d]', '', match_fisso.group(1))
    return ""


def estrai_email_da_testo(body):
    """
    Cerca un eventuale indirizzo email inserito nel testo dell'annuncio (Colonna F).
    """
    if not body:
        return ""
    match_email = re.search(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', str(body))
    if match_email:
        em = match_email.group(0).lower().strip()
        if not any(bad in em for bad in ["subito.it", "example.com", "sentry.io"]):
            return em
    return ""


def estrai_nome_cognome_privato(adv_name, body=""):
    nome_base = str(adv_name or "").strip()
    if nome_base.lower() in ("privato", "utente", "inserzionista", "subito", "none", "null"):
        nome_base = ""

    if body:
        match_nome = re.search(
            r'(?:contattare|chiamare|chiedere\s+di|sig\.?\s*|signor\s+|proprietario\s*:?\s*|referente\s*:?\s*)'
            r'([A-ZÀ-Ú][a-zà-ú]{2,15}(?:\s+[A-ZÀ-Ú][a-zà-ú]{2,18})?)',
            str(body)
        )
        if match_nome:
            candidato = match_nome.group(1).strip()
            stop = {"Per", "Info", "Informazioni", "Solo", "Ore", "Pomeriggio", "Mattina", "Numero", "WhatsApp", "Telefono", "Agenzia"}
            parole_cand = [w for w in candidato.split() if w not in stop]
            if parole_cand:
                nome_testo = " ".join(parole_cand)
                if len(nome_testo) > len(nome_base):
                    return nome_testo

    return nome_base or "Proprietario Privato"


def classifica_sospetti_agenzie_e_ribassi(immobili_dict):
    """
    Analizza tutti gli immobili del database e li smista rigorosamente in:
    - 'privato' (Vero Proprietario Privato)
    - 'sospetto_agenzia' (Falso privato: stesso utente/telefono con più immobili, aste, sigle agenzia/rif.)
    - 'agenzia' (Agenzia immobiliare dichiarata, con calcolo automatico dei ribassi di prezzo)
    """
    # 1. Conta quanti immobili distinti ha ogni user_id, telefono o nome inserzionista
    conteggio_userid = {}
    conteggio_telefono = {}
    conteggio_nome_specifico = {}

    for item_id, it in immobili_dict.items():
        if not it.get("is_privato", False):
            continue
        uid = str(it.get("user_id", "") or "").strip()
        if uid and uid not in ("0", "None"):
            conteggio_userid[uid] = conteggio_userid.get(uid, 0) + 1

        tel = re.sub(r'\D', '', str(it.get("telefono", "") or ""))
        if len(tel) >= 9:
            conteggio_telefono[tel] = conteggio_telefono.get(tel, 0) + 1

        nome = str(it.get("nome_privato", "") or "").strip()
        # Considera sospetto per nome se è un nome composto/specifico (non generico)
        if nome and nome != "Proprietario Privato" and (" " in nome or "utente" in nome.lower() or len(nome) > 10):
            conteggio_nome_specifico[nome.lower()] = conteggio_nome_specifico.get(nome.lower(), 0) + 1

    # Pattern tipici di agenzie immobiliari, studi d'asta o intermediari camuffati da privati
    pattern_testo_agenzia = re.compile(
        r'(?i)\b(?:rif\s*[\.:]\s*[a-z0-9]+|cod\.?\s*annuncio|immobile\s+in\s+asta|asta\s+giudiziaria|'
        r'tribunale\s+di|offerta\s+minima|vendita\s+senza\s+incanto|studio\s+di\s+consulenza|'
        r'agenzia\s+immobiliare|nostra\s+esclusiva|proponiamo\s+in\s+vendita|per\s+info\s+e\s+visite\s+in\s+ufficio|'
        r'incarico\s+di\s+mediazione|provvigione)\b'
    )
    pattern_nome_agenzia = re.compile(
        r'(?i)\b(?:immobiliare|agenzia|studio|srl|srls|spa|group|case|aste|remax|re/max|tecnocasa|'
        r'gabetti|frimm|tempocasa|engel| Toscano|capitalhouse|mediazioni|servizi|consulting)\b'
    )

    # Blacklist numeri di telefono di agenzie immobiliari segnalati dal titolare
    TELEFONI_AGENZIE_SEGNALATE = {"3284670316"}

    for item_id, it in immobili_dict.items():
        # Calcolo storico prezzi e ribassi (sia per Agenzie che per Privati)
        p_attuale = parse_prezzo_numerico(it.get("prezzo", ""))
        p_iniziale = parse_prezzo_numerico(it.get("prezzo_iniziale", "")) or p_attuale
        if p_iniziale > 0 and not it.get("prezzo_iniziale"):
            it["prezzo_iniziale"] = f"{p_iniziale} €"

        if p_iniziale > 0 and p_attuale > 0 and p_attuale < p_iniziale:
            diff = p_attuale - p_iniziale
            perc = round((diff / p_iniziale) * 100, 1)
            it["ribasso_importo"] = diff
            it["ribasso_percentuale"] = perc
            it["ha_ribasso"] = True
        else:
            it.setdefault("ribasso_importo", 0)
            it.setdefault("ribasso_percentuale", 0.0)
            it.setdefault("ha_ribasso", False)

        tel_clean_chk = re.sub(r'\D', '', str(it.get("telefono", "") or ""))
        if tel_clean_chk.startswith("39") and len(tel_clean_chk) > 10:
            tel_clean_chk = tel_clean_chk[2:]
        if tel_clean_chk in TELEFONI_AGENZIE_SEGNALATE:
            it["is_privato"] = False
            it["is_sospetto_agenzia"] = False
            it["categoria_classificazione"] = "agenzia"
            it["nome_agenzia"] = it.get("nome_agenzia") if it.get("nome_agenzia") not in ("", "Privato") else f"Agenzia ({tel_clean_chk})"
            it["motivo_sospetto"] = ""
            continue

        # Se è già un'agenzia dichiarata
        if not it.get("is_privato", False):
            it["is_sospetto_agenzia"] = False
            it["categoria_classificazione"] = "agenzia"
            it["motivo_sospetto"] = ""
            continue

        # Verifica se il "Privato" è in realtà un SOSPETTO AGENZIA
        motivi = []
        uid = str(it.get("user_id", "") or "").strip()
        tel = re.sub(r'\D', '', str(it.get("telefono", "") or ""))
        nome = str(it.get("nome_privato", "") or "").strip()
        testo_completo = f"{it.get('titolo', '')} {it.get('descrizione', '')}"

        if uid and conteggio_userid.get(uid, 0) >= 2:
            motivi.append(f"Stesso account con {conteggio_userid[uid]} immobili in vendita")
        if len(tel) >= 9 and conteggio_telefono.get(tel, 0) >= 2:
            motivi.append(f"Stesso numero ({tel}) presente su {conteggio_telefono[tel]} annunci diversi")
        if nome and conteggio_nome_specifico.get(nome.lower(), 0) >= 2:
            motivi.append(f"Inserzionista '{nome}' con {conteggio_nome_specifico[nome.lower()]} immobili pubblicati")
        if pattern_nome_agenzia.search(nome):
            motivi.append(f"Nome inserzionista aziendale/professionale ('{nome}')")

        match_kw = pattern_testo_agenzia.search(testo_completo)
        if match_kw:
            motivi.append(f"Formula da agenzia/asta nel testo ('{match_kw.group(0)}')")

        if motivi:
            it["is_sospetto_agenzia"] = True
            it["categoria_classificazione"] = "sospetto_agenzia"
            it["motivo_sospetto"] = " • ".join(motivi)
        else:
            it["is_sospetto_agenzia"] = False
            it["categoria_classificazione"] = "privato"
            it["motivo_sospetto"] = ""


def normalizza_telefono_chiave(tel):
    digits = re.sub(r'\D', '', str(tel or ""))
    if digits.startswith("0039") and len(digits) > 12:
        digits = digits[4:]
    elif digits.startswith("39") and len(digits) > 10:
        digits = digits[2:]
    return digits


def is_item_in_memoria_30gg(item, db):
    memoria_attiva = db.get("memoria_invii_30gg", {})
    item_id = item.get("id", "")
    tel_raw = re.sub(r'\D', '', str(item.get("telefono", "") or ""))
    tel_clean = normalizza_telefono_chiave(tel_raw)
    em_clean = str(item.get("email_contatto", "") or "").lower().strip()
    return bool(
        (item_id and memoria_attiva.get(item_id))
        or (tel_clean and memoria_attiva.get(f"TEL_{tel_clean}"))
        or (tel_raw and memoria_attiva.get(f"TEL_{tel_raw}"))
        or (em_clean and memoria_attiva.get(f"EMAIL_{em_clean}"))
    )


def aggiorna_e_pulisci_memoria_30gg(db):
    """
    Controlla la memoria degli invii di presentazione (WhatsApp/Email/Qualsiasi canale).
    Dopo 30 giorni (1 mese) cancella automaticamente il blocco così il cliente torna da contattare.
    """
    memoria = db.setdefault("memoria_invii_30gg", {})
    # Sincronizza eventuale memoria salvata sul Cloud Google Apps Script
    webhook_url = CONFIG.get("google_apps_script", {}).get("webhook_url", "")
    if webhook_url:
        try:
            r = SESSION.get(f"{webhook_url}?action=get_memoria_contatti", timeout=10)
            if r.status_code == 200:
                cloud_data = r.json()
                cloud_mem = cloud_data.get("memoria", {})
                if isinstance(cloud_mem, dict):
                    memoria.update(cloud_mem)
        except Exception:
            pass

    now_ms = int(time.time() * 1000)
    trenta_gg_ms = 30 * 24 * 60 * 60 * 1000
    scaduti_rimossi = []
    memoria_attiva = {}

    for key, rec in list(memoria.items()):
        ts_ms = rec.get("timestamp_ms", 0)
        if ts_ms and (now_ms - ts_ms < trenta_gg_ms):
            giorni_passati = int((now_ms - ts_ms) / (24 * 60 * 60 * 1000))
            rec["giorni_trascorsi"] = giorni_passati
            rec["giorni_rimanenti"] = max(1, 30 - giorni_passati)
            memoria_attiva[key] = rec
            if key.startswith("TEL_"):
                tel_norm = normalizza_telefono_chiave(key[4:])
                if tel_norm and f"TEL_{tel_norm}" not in memoria_attiva:
                    memoria_attiva[f"TEL_{tel_norm}"] = rec
        else:
            scaduti_rimossi.append(key)

    db["memoria_invii_30gg"] = memoria_attiva

    # Aggiorna lo stato su ciascun immobile in db['immobili']
    for item_id, it in db.get("immobili", {}).items():
        tel_raw = re.sub(r'\D', '', str(it.get("telefono", "") or ""))
        tel_clean = normalizza_telefono_chiave(tel_raw)
        em_clean = str(it.get("email_contatto", "") or "").lower().strip()
        rec_mem = (
            memoria_attiva.get(item_id)
            or (memoria_attiva.get(f"TEL_{tel_clean}") if tel_clean else None)
            or (memoria_attiva.get(f"TEL_{tel_raw}") if tel_raw else None)
            or (memoria_attiva.get(f"EMAIL_{em_clean}") if em_clean else None)
        )
        if rec_mem:
            it["contattato_30gg"] = True
            it["ultimo_invio_presentazione"] = rec_mem.get("data_invio", "")
            it["giorni_allo_sblocco"] = rec_mem.get("giorni_rimanenti", 30)
            it["canale_ultimo_invio"] = rec_mem.get("canale", "WHATSAPP")
        else:
            if it.get("contattato_30gg"):
                it["scaduto_30gg_da_ricontattare"] = True
            it["contattato_30gg"] = False
            it["giorni_allo_sblocco"] = 0

    return scaduti_rimossi


def migra_e_deduplica_db(db):
    immobili_raw = db.get("immobili", {})
    if not immobili_raw:
        return db, 0

    nuovi_immobili = {}
    duplicati_rimossi = 0

    for old_key, item in immobili_raw.items():
        url = item.get("url", "")
        new_id = estrai_id_univoco_subito(url, fallback_id=old_key)
        item["id"] = new_id
        item["superficie"] = normalizza_metri_quadri(item.get("superficie", ""))
        item["titolo"] = converti_abbreviazioni_metri_quadri(item.get("titolo", ""))
        item["via_zona"] = converti_abbreviazioni_metri_quadri(item.get("via_zona", item["titolo"]))
        item["descrizione"] = formatta_testo_colonna_f(
            item.get("descrizione", ""),
            item.get("titolo", "")
        )
        if not item.get("email_contatto"):
            item["email_contatto"] = estrai_email_da_testo(item.get("descrizione", ""))

        if new_id not in nuovi_immobili:
            nuovi_immobili[new_id] = item
        else:
            duplicati_rimossi += 1
            esistente = nuovi_immobili[new_id]
            ts_old = esistente.get("timestamp", "")
            ts_new = item.get("timestamp", "")
            first_ts = min(ts_old, ts_new) if (ts_old and ts_new) else (ts_old or ts_new)
            latest_ts = max(
                esistente.get("ultimo_rilevamento", ts_old),
                item.get("ultimo_rilevamento", ts_new)
            )
            if ts_new >= ts_old:
                esistente.update(item)
            esistente["id"] = new_id
            esistente["timestamp"] = first_ts
            if latest_ts:
                esistente["ultimo_rilevamento"] = latest_ts

    db["immobili"] = nuovi_immobili
    classifica_sospetti_agenzie_e_ribassi(db["immobili"])
    aggiorna_e_pulisci_memoria_30gg(db)
    return db, duplicati_rimossi


def carica_db():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
            db, rimossi = migra_e_deduplica_db(db)
            if rimossi > 0:
                salva_db(db)
            return db
        except Exception as e:
            print(f"[DB] Errore lettura db locale: {e} — Immobiliare Giancani")
    return {"immobili": {}, "memoria_invii_30gg": {}, "ultimo_aggiornamento": ""}


def salva_db(db):
    try:
        db["ultimo_aggiornamento"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[DB] Errore salvataggio db locale: {e} — Immobiliare Giancani")


def pubblica_su_github_pages(file_paths_map):
    """
    Carica automaticamente la pagina HTML di resoconto e il database su GitHub Pages
    (Tonyhood2345/live-stream-serverless) così dal cellulare è sempre online e sincronizzata.
    """
    token = GITHUB_API_TOKEN.strip()
    if not token:
        return False

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CacciatoriImmobili-Giancani"
    }

    success_any = False
    for local_path, remote_path in file_paths_map.items():
        if not os.path.exists(local_path):
            continue
        try:
            with open(local_path, "rb") as f:
                b64_content = base64.b64encode(f.read()).decode("utf-8")

            url_api = f"https://api.github.com/repos/{GITHUB_REPO_PAGES}/contents/{remote_path}"
            r_get = SESSION.get(url_api, headers=headers, timeout=12)
            sha = r_get.json().get("sha") if r_get.status_code == 200 else None

            payload = {
                "message": f"chore(cacciatori): aggiornamento live {remote_path} [skip ci] — Immobiliare Giancani",
                "content": b64_content,
                "branch": "main"
            }
            if sha:
                payload["sha"] = sha

            r_put = SESSION.put(url_api, headers=headers, json=payload, timeout=20)
            if r_put.status_code in (200, 201):
                print(f"  [GitHub Pages] Pubblicato online: https://tonyhood2345.github.io/live-stream-serverless/{remote_path} — Immobiliare Giancani")
                success_any = True
            else:
                print(f"  [GitHub Pages Nota] {remote_path} status {r_put.status_code} — Immobiliare Giancani")
        except Exception as e:
            print(f"  [GitHub Pages Eccezione] {remote_path}: {e} — Immobiliare Giancani")

    return success_any


def invia_report_giornaliero_contatti_telegram(db, html_path=None):
    """
    Invia su Telegram il report giornaliero (e ad ogni aggiornamento) che indica:
    - Quanti nuovi numeri di privati sono pronti da contattare su WhatsApp (1-Click dal cellulare)
    - Quanti contatti sono pronti da contattare via Email
    - Quanti clienti hanno superato 1 mese (30 giorni) e vanno ricontattati con la presentazione
    - Quanti ribassi di agenzie immobiliari e sospetti agenzie sono stati rilevati
    """
    token = CONFIG["telegram"]["bot_token"]
    chat_id = CONFIG["telegram"]["chat_id"]
    if not token or not chat_id:
        return

    immobili = list(db.get("immobili", {}).values())
    privati_puri = [x for x in immobili if x.get("categoria_classificazione") == "privato"]
    sospetti_ag = [x for x in immobili if x.get("categoria_classificazione") == "sospetto_agenzia"]
    agenzie = [x for x in immobili if x.get("categoria_classificazione") == "agenzia"]
    ribassi_agenzie = [x for x in agenzie if x.get("ha_ribasso")]

    wa_da_contattare = [
        x for x in privati_puri
        if x.get("telefono") and not x.get("contattato_30gg", False)
    ]
    email_da_contattare = [
        x for x in privati_puri
        if x.get("email_contatto") and not x.get("contattato_30gg", False)
    ]
    ricontattare_dopo_30gg = [
        x for x in privati_puri
        if x.get("scaduto_30gg_da_ricontattare", False) and not x.get("contattato_30gg", False)
    ]
    in_memoria_30gg = [
        x for x in privati_puri
        if x.get("contattato_30gg", False)
    ]

    # Elenco anteprima dei primi 6 numeri pronti da cliccare su WhatsApp
    anteprima_numeri = ""
    for idx, p in enumerate(wa_da_contattare[:6], 1):
        nome_p = sanitizza_testo_anti_pirata(p.get("nome_privato", "Privato"))
        com_p = sanitizza_testo_anti_pirata(p.get("comune", ""))
        tel_p = p.get("telefono", "")
        prz_p = p.get("prezzo", "")
        anteprima_numeri += f"  {idx}) 👤 <b>{nome_p}</b> ({com_p}) — 📞 <code>{tel_p}</code> ({prz_p})\n"

    if not anteprima_numeri:
        anteprima_numeri = "  <i>Tutti i numeri attuali sono già stati contattati (in memoria per 30 giorni)</i>\n"

    messaggio = (
        f"☀️ <b>BUONGIORNO! ABBIAMO TROVATO NUOVI IMMOBILI: CONTROLLA E COLLEGATI!</b>\n"
        f"<i>Bot @Programmaagenzia_bot — Console Mobile 1-Click WhatsApp &amp; Email</i>\n\n"
        f"🟢 <b>NUOVI NUMERI DA CONTATTARE SU WHATSAPP:</b> <b>{len(wa_da_contattare)}</b>\n"
        f"✉️ <b>CONTATTI DA CONTATTARE VIA EMAIL:</b> <b>{len(email_da_contattare)}</b>\n"
        f"🔄 <b>SCADUTO 1 MESE (30 GG) DA RICONTATTARE:</b> <b>{len(ricontattare_dopo_30gg)}</b>\n"
        f"⏳ <b>Già Contattati in Memoria (Bloccati 30 gg):</b> {len(in_memoria_30gg)}\n\n"
        f"📋 <b>Primi Numeri Privati Pronti per 1-Click WhatsApp:</b>\n"
        f"{anteprima_numeri}\n"
        f"📊 <b>Panoramica Categorie Smistate:</b>\n"
        f"• 👤 Privati Verificati: <b>{len(privati_puri)}</b>\n"
        f"• 🕵️ Sospetti Agenzie / Falsi Privati: <b>{len(sospetti_ag)}</b>\n"
        f"• 🏢 Agenzie Immobiliari Monitorate: <b>{len(agenzie)}</b> (di cui <b>{len(ribassi_agenzie)} con Ribasso Prezzo</b>)\n\n"
        f"🚀 <a href='{GITHUB_PAGES_URL}'>👉 APRI DAL CELLULARE LA CONSOLE 1-CLICK WHATSAPP (GITHUB PAGES)</a>\n\n"
        f"— Immobiliare Giancani"
    )

    url_text = f"https://api.telegram.org/bot{token}/sendMessage"
    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "🚀 APRI CONSOLE 1-CLICK WHATSAPP DENTRO TELEGRAM",
                    "web_app": {"url": GITHUB_PAGES_URL}
                }
            ],
            [
                {
                    "text": "🌐 Apri nel Browser Esterno",
                    "url": GITHUB_PAGES_URL
                }
            ]
        ]
    }
    try:
        r = SESSION.post(url_text, json={
            "chat_id": chat_id,
            "text": messaggio,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
            "reply_markup": reply_markup
        }, timeout=12)
        if r.status_code == 200:
            print("  [Telegram Report Giornaliero] Riepilogo numeri WhatsApp/Email con Mini-App Telegram inviato con successo! — Immobiliare Giancani")
        else:
            print(f"  [Telegram Report Nota] Status {r.status_code}: {r.text} — Immobiliare Giancani")
    except Exception as e:
        print(f"  [Telegram Report Errore]: {e} — Immobiliare Giancani")

    if html_path and os.path.exists(html_path):
        url_doc = f"https://api.telegram.org/bot{token}/sendDocument"
        caption_doc = (
            f"📱 <b>CONSOLE MOBILE HTML — CACCIATORI DI IMMOBILI</b>\n"
            f"🟢 <b>{len(wa_da_contattare)} Numeri WhatsApp</b> e <b>{len(email_da_contattare)} Email</b> pronti all'invio con 1 click.\n"
            f"🔗 Online su GitHub: {GITHUB_PAGES_URL}\n\n"
            f"— Immobiliare Giancani"
        )
        try:
            with open(html_path, "rb") as f_html:
                SESSION.post(
                    url_doc,
                    data={"chat_id": chat_id, "caption": caption_doc, "parse_mode": "HTML"},
                    files={"document": ("CONSOLE_CACCIATORI_GIANCANI.html", f_html, "text/html")},
                    timeout=20
                )
        except Exception as e:
            print(f"  [Telegram HTML Doc Errore]: {e} — Immobiliare Giancani")


def invia_notifica_telegram(item, event_type="NUOVO_PRIVATO", old_price=None, old_agency=None):
    token = CONFIG["telegram"]["bot_token"]
    chat_id = CONFIG["telegram"]["chat_id"]
    if not token or not chat_id:
        return

    is_privato = item.get("is_privato", True)
    comune = item.get("comune", "N/D")
    titolo = sanitizza_testo_anti_pirata(item.get("titolo", "Immobile in Vendita"))
    via_zona = sanitizza_testo_anti_pirata(item.get("via_zona", titolo))
    tipologia = item.get("tipologia", "Immobile")
    prezzo = item.get("prezzo", "Su richiesta")
    superficie = normalizza_metri_quadri(item.get("superficie", "Non specificata"))
    url = item.get("url", "")
    foto_url = item.get("foto_url", "")
    telefono = item.get("telefono", "")
    email_c = item.get("email_contatto", "")
    locali = item.get("locali", "")
    descrizione_col_f = sanitizza_testo_anti_pirata(item.get("descrizione", ""))
    estratto_col_f = descrizione_col_f[:180] + "..." if len(descrizione_col_f) > 180 else descrizione_col_f

    if event_type == "PASSAGGIO_AGENZIA_PRIVATO":
        header = "🔄 <b>PASSAGGIO DA AGENZIA A PRIVATO RILEVATO!</b>\n"
        if old_price:
            header += f"📉 <i>Prezzo Agenzia: {old_price} ➔ Ora da Privato: {prezzo}</i>\n"
    elif event_type == "RIBASSO_PREZZO":
        header = f"📉 <b>RIBASSO PREZZO DA PRIVATO!</b>\n<i>Da {old_price} ➔ {prezzo}</i>\n"
    elif event_type == "RIBASSO_AGENZIA":
        header = f"🏢📉 <b>RIBASSO PREZZO AGENZIA IMMOBILIARE!</b>\n<i>{item.get('nome_agenzia', 'Agenzia')}: da {old_price} ➔ {prezzo}</i>\n"
    elif item.get("categoria_classificazione") == "sospetto_agenzia":
        header = f"🕵️ <b>SOSPETTO AGENZIA / FALSO PRIVATO RILEVATO</b>\n<i>Motivo: {item.get('motivo_sospetto', '')}</i>\n"
    elif is_privato:
        header = "🚨 <b>NUOVO IMMOBILE DA PRIVATO INTERCETTATO!</b>\n"
    else:
        header = "🏢 <b>NUOVO ANNUNCIO AGENZIA (Registrato in Inventario)</b>\n"

    nome_privato = item.get("nome_privato") or item.get("nome_inserzionista") or "Proprietario Privato"
    yt_url = CONFIG.get("presentazione", {}).get("youtube_url", "https://www.youtube.com/watch?v=TsdEk3Y9ewc")

    clean_phone = re.sub(r'\D', '', telefono) if telefono else ""
    if clean_phone and len(clean_phone) >= 9:
        if clean_phone.startswith("0"):
            clean_phone = f"39{clean_phone}"
        elif not clean_phone.startswith("39"):
            clean_phone = f"39{clean_phone}"
        saluto = f"Gentile {nome_privato}" if nome_privato != "Proprietario Privato" else "Gentile proprietario"
        wa_text = urllib.parse.quote(
            f"{saluto}, buongiorno!\n"
            f"Sono Antonio Giancani, titolare dell'agenzia Immobiliare Giancani.\n"
            f"Ho visto il Suo immobile in vendita a {comune} ({superficie} a {prezzo}) e Le scrivo perché vorrei lavorare per Lei per venderLe l'immobile al miglior prezzo e senza perditempo.\n\n"
            f"🌐 Pagina Facebook ufficiale: https://www.facebook.com/immobiliaregiancani.it\n"
            f"📺 Canale YouTube ufficiale: https://youtube.com/@immobiliaregiancani\n\n"
            f"📱 Antonio Giancani: +39 320 166 7156\n"
            f"— Immobiliare Giancani"
        )
        wa_link = f"https://api.whatsapp.com/send?phone={clean_phone}&text={wa_text}"
        call_link = f"tel:+{clean_phone}"
        contatto_html = (
            f"📞 <b>Telefono Diretto:</b> <code>{telefono}</code>\n"
            f"💬 <a href='{wa_link}'>👉 INVIA PRESENTAZIONE + VIDEO YOUTUBE SU WHATSAPP (1-CLICK)</a>\n"
            f"📲 <a href='{call_link}'>👉 Chiama Subito al Telefono</a>\n"
        )
    else:
        contatto_html = "📞 <b>Contatto:</b> Verificabile sull'annuncio originale\n"

    if email_c:
        contatto_html += f"✉️ <b>Email:</b> <code>{email_c}</code>\n"

    info_locali = f" ({locali} locali)" if locali else ""
    venditore_str = f"👤 {nome_privato} (Privato)" if is_privato else f"🏢 {item.get('nome_agenzia', 'Agenzia')}"

    messaggio = (
        f"{header}\n"
        f"📍 <b>Comune:</b> {comune} — {via_zona}\n"
        f"🏠 <b>Tipologia:</b> {tipologia}{info_locali} | 📐 <b>{superficie}</b>\n"
        f"💰 <b>Prezzo:</b> {prezzo}\n"
        f"👤 <b>Inserzionista:</b> {venditore_str}\n"
        f"📄 <b>Testo (Colonna F):</b> <i>{estratto_col_f}</i>\n"
        f"{contatto_html}\n"
        f"📱 <a href='{GITHUB_PAGES_URL}'>🌐 Apri Console Mobile su GitHub Pages (Con Memoria 30gg)</a>\n"
        f"🔗 <a href='{url}'>🌐 Apri Annuncio Originale</a>\n\n"
        f"— Immobiliare Giancani"
    )

    inviato = False
    if foto_url and foto_url.startswith("http"):
        url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
        try:
            r = SESSION.post(url_photo, json={
                "chat_id": chat_id,
                "photo": foto_url,
                "caption": messaggio[:1024],
                "parse_mode": "HTML"
            }, timeout=12)
            if r.status_code == 200:
                inviato = True
        except Exception:
            pass

    if not inviato:
        url_text = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            SESSION.post(url_text, json={
                "chat_id": chat_id,
                "text": messaggio,
                "parse_mode": "HTML"
            }, timeout=10)
        except Exception:
            pass


def invia_a_google_apps_script(items):
    webhook_url = CONFIG.get("google_apps_script", {}).get("webhook_url")
    if not webhook_url:
        return
    try:
        res = SESSION.post(webhook_url, json={"action": "salva_batch", "items": items}, timeout=25)
        print(f"  [Google Sheet] Sincronizzazione webhook completata. Status: {res.status_code} — Immobiliare Giancani")
    except Exception as e:
        print(f"  [Google Sheet Errore] {e} — Immobiliare Giancani")


def arricchisci_dettaglio_annuncio(page, item):
    url = item.get("url", "")
    if not url:
        return item
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1200)
        soup = BeautifulSoup(page.content(), "lxml")
        next_data = soup.find("script", id="__NEXT_DATA__")
        if not next_data or not next_data.string:
            return item
        data = json.loads(next_data.string)
        ad = data.get("props", {}).get("pageProps", {}).get("ad", {})
        if not ad:
            return item

        adv_detail = ad.get("advertiser", {})
        adv_name_det = str(adv_detail.get("name", "") or "").strip()
        phone_det = str(adv_detail.get("phone", "") or "").strip()
        if phone_det in ("0", "None", "null"):
            phone_det = ""

        body_full = ad.get("body", "")
        if body_full and len(body_full) > len(item.get("descrizione", "")):
            item["descrizione"] = formatta_testo_colonna_f(body_full, item.get("titolo", ""))
            item["via_zona"] = estrai_via_zona(item.get("titolo", ""), body_full, item.get("comune", ""))

        if not item.get("telefono"):
            item["telefono"] = phone_det or estrai_telefono_da_testo(body_full)
        if not item.get("email_contatto"):
            item["email_contatto"] = estrai_email_da_testo(body_full)
        if item.get("is_privato", False):
            nuovo_nome = estrai_nome_cognome_privato(adv_name_det or item.get("nome_privato", ""), body_full)
            item["nome_privato"] = nuovo_nome
            item["nome_inserzionista"] = nuovo_nome
            item["email"] = nuovo_nome
            item["note"] = f"Proprietario: {nuovo_nome} | Tel: {item.get('telefono') or 'Protetto su annuncio'}"
    except Exception as e:
        print(f"  [Dettaglio Scheda] Nota apertura {url[:50]}: {e} — Immobiliare Giancani")
    return item


def estrai_annunci_subito(page_html):
    soup = BeautifulSoup(page_html, "lxml")
    next_data = soup.find("script", id="__NEXT_DATA__")
    if not next_data or not next_data.string:
        return []

    try:
        data = json.loads(next_data.string)
    except Exception:
        return []

    items_container = data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("items", {})
    items = items_container.get("originalList") or items_container.get("list") or []
    risultati = []

    for raw_it in items:
        it = raw_it.get("item", raw_it) if isinstance(raw_it, dict) else {}
        if not it:
            continue

        geo = it.get("geo", {})
        town_val = geo.get("town", {}).get("value", "")
        town_norm = town_val.lower().strip()

        is_target = any(c in town_norm for c in TARGET_COMUNI)
        if not is_target:
            continue

        adv = it.get("advertiser", {})
        is_company = adv.get("company", False)
        is_privato = not is_company
        user_id = str(adv.get("userId", "") or "")

        features = it.get("features", {})
        price_val = features.get("/price", {}).get("values", [{}])[0].get("value", "Su richiesta")

        size_raw = features.get("/size", {}).get("values", [{}])[0].get("value", "")
        superficie = normalizza_metri_quadri(size_raw)

        rooms_val = features.get("/room", {}).get("values", [{}])[0].get("value", "")
        bathrooms_val = features.get("/bathrooms", {}).get("values", [{}])[0].get("value", "")

        subject_raw = it.get("subject", "Immobile")
        subject = converti_abbreviazioni_metri_quadri(subject_raw)
        body_raw = it.get("body", "")
        descrizione_col_f = formatta_testo_colonna_f(body_raw, subject)

        urls = it.get("urls", {})
        ad_url = urls.get("default", "")
        urn = it.get("urn", "")
        item_id = estrai_id_univoco_subito(ad_url, urn=urn)

        images_raw = it.get("images", [])
        foto_url = ""
        if images_raw:
            base = images_raw[0].get("cdnBaseUrl", "") or images_raw[0].get("uri", "")
            if base:
                foto_url = f"{base}?rule=gallery-desktop-1x-auto" if "?" not in base else base

        phone = str(adv.get("phone", "") or "").strip()
        if phone in ("0", "None", "null"):
            phone = ""
        if not phone and body_raw:
            phone = estrai_telefono_da_testo(body_raw)

        email_contatto = estrai_email_da_testo(body_raw)

        adv_name_raw = str(adv.get("name", "") or "").strip()
        nome_privato = estrai_nome_cognome_privato(adv_name_raw, body_raw) if is_privato else ""
        adv_name = nome_privato if is_privato else (adv_name_raw or "Agenzia")

        category_obj = it.get("category", {})
        cat_label = category_obj.get("label") or category_obj.get("friendlyName") or ""
        prop_type_feat = features.get("/property_type", {}).get("values", [{}])[0].get("value", "")
        tipologia = prop_type_feat or cat_label or "Appartamento / Immobile"

        map_info = geo.get("map", {})
        latitudine = str(map_info.get("latitude", "") or "")
        longitudine = str(map_info.get("longitude", "") or "")

        via_zona = estrai_via_zona(subject_raw, body_raw, town_val)
        nota_sheet = (
            f"Proprietario: {nome_privato} | Tel: {phone if phone else 'Protetto su annuncio'}"
            if is_privato else f"Agenzia: {adv_name}"
        )

        risultati.append({
            "id": item_id,
            "user_id": user_id,
            "fonte": "Subito.it",
            "comune": town_val,
            "titolo": subject,
            "via_zona": via_zona,
            "tipologia": tipologia,
            "locali": rooms_val,
            "bagni": bathrooms_val,
            "superficie": superficie,
            "prezzo": price_val,
            "prezzo_iniziale": price_val,
            "is_privato": is_privato,
            "tipologia_venditore": "privato" if is_privato else "agenzia",
            "nome_privato": nome_privato,
            "nome_inserzionista": adv_name,
            "nome_agenzia": "Privato" if is_privato else adv_name,
            "telefono": phone,
            "email_contatto": email_contatto,
            "email": nome_privato if is_privato else adv_name,
            "note": nota_sheet,
            "url": ad_url,
            "foto_url": foto_url,
            "latitudine": latitudine,
            "longitudine": longitudine,
            "descrizione": descrizione_col_f,
            "timestamp": datetime.now().isoformat()
        })

    return risultati


def estrai_portale_generico(page_html, fonte_nome, base_url):
    """
    Estrattore universale per portali minori (Bakeca.it, CasaDaPrivato.it, Cambiocasa.it, PCase.it):
    estrae titolo, link, comune tra i 7 target, prezzo, superficie in 'metri quadri',
    telefono ed email dal testo dell'annuncio (Colonna F).
    """
    soup = BeautifulSoup(page_html, "lxml")
    risultati = []
    visti_url = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
        full_url = urllib.parse.urljoin(base_url, href)
        if full_url in visti_url:
            continue

        # Filtra solo link che sembrano schede immobile
        href_low = full_url.lower()
        if not any(kw in href_low for kw in ["/annunc", "/casa", "/appartament", "/villa", "/immobil", "/vendita", "/dettaglio", ".htm", ".html"]):
            continue
        if any(skip in href_low for skip in ["login", "registr", "privacy", "cookie", "contatti", "pubblica", "facebook.com", "instagram.com"]):
            continue

        card = a.find_parent(["article", "li", "div", "section"])
        testo_card = card.get_text(" ", strip=True) if card else a.get_text(" ", strip=True)
        if len(testo_card) < 25 or len(testo_card) > 1800:
            continue

        testo_low = testo_card.lower()
        comune_trovato = None
        for c_target in CONFIG.get("comuni_target", ["Favara", "Agrigento", "Aragona", "Comitini", "Porto Empedocle", "Siculiana", "Realmonte"]):
            if c_target.lower() in testo_low or c_target.lower().replace(" ", "-") in href_low:
                comune_trovato = c_target
                break
        if not comune_trovato:
            continue

        visti_url.add(full_url)
        titolo_raw = a.get_text(" ", strip=True) or testo_card[:80]
        titolo = converti_abbreviazioni_metri_quadri(titolo_raw[:110])

        match_prezzo = re.search(r'(?:€|eur)\s*([\d\.]{4,10})|([\d\.]{4,10})\s*(?:€|eur)', testo_card, re.IGNORECASE)
        prezzo_str = "Su richiesta"
        if match_prezzo:
            cifre = (match_prezzo.group(1) or match_prezzo.group(2) or "").replace(".", "")
            if cifre.isdigit() and int(cifre) >= 5000:
                prezzo_str = f"{cifre} €"

        match_mq = re.search(r'(\d{2,4})\s*(?:mq\.?|m²|m2|metri\s+quadri)', testo_card, re.IGNORECASE)
        superficie = f"{match_mq.group(1)} metri quadri" if match_mq else "Non specificata"

        phone = estrai_telefono_da_testo(testo_card)
        email_c = estrai_email_da_testo(testo_card)
        is_agenzia_kw = bool(re.search(r'(?i)\b(agenzia|immobiliare|remax|tecnocasa|gabetti|tempocasa|srl|studio)\b', testo_card))
        is_privato = ("casadaprivato" in fonte_nome.lower()) or not is_agenzia_kw

        foto_url = ""
        if card:
            img = card.find("img")
            if img:
                foto_url = img.get("data-src") or img.get("src") or ""
                if foto_url and not foto_url.startswith("http"):
                    foto_url = urllib.parse.urljoin(base_url, foto_url)

        item_id = f"{fonte_nome[:3].upper()}-{hashlib.md5(full_url.encode('utf-8')).hexdigest()[:10]}"
        descrizione_col_f = formatta_testo_colonna_f(testo_card, titolo)

        risultati.append({
            "id": item_id,
            "user_id": "",
            "fonte": fonte_nome,
            "comune": comune_trovato,
            "titolo": titolo,
            "via_zona": estrai_via_zona(titolo, testo_card, comune_trovato),
            "tipologia": "Immobile",
            "locali": "",
            "bagni": "",
            "superficie": superficie,
            "prezzo": prezzo_str,
            "prezzo_iniziale": prezzo_str,
            "is_privato": is_privato,
            "tipologia_venditore": "privato" if is_privato else "agenzia",
            "nome_privato": "Proprietario Privato" if is_privato else fonte_nome,
            "nome_inserzionista": "Proprietario Privato" if is_privato else fonte_nome,
            "nome_agenzia": "Privato" if is_privato else fonte_nome,
            "telefono": phone,
            "email_contatto": email_c,
            "email": "Proprietario Privato" if is_privato else fonte_nome,
            "note": f"Fonte: {fonte_nome} | Tel: {phone or 'Su annuncio'}",
            "url": full_url,
            "foto_url": foto_url,
            "latitudine": "",
            "longitudine": "",
            "descrizione": descrizione_col_f,
            "timestamp": datetime.now().isoformat()
        })

    return risultati


def costruisci_lista_portali_minori():
    return [
        ("Bakeca.it", "https://agrigento.bakeca.it/annunci/vendita-case/", "https://agrigento.bakeca.it"),
        ("CasaDaPrivato.it", "https://www.casadaprivato.it/annunci-vendita/immobili/agrigento-provincia", "https://www.casadaprivato.it"),
        ("Cambiocasa.it", "https://www.cambiocasa.it/vendita/case/agrigento/", "https://www.cambiocasa.it"),
        ("PCase.it", "https://www.pcase.it/vendita/agrigento/", "https://www.pcase.it"),
    ]


def avvia_browser_playwright(playwright_instance):
    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage"
    ]
    if sys.platform.startswith("win"):
        try:
            print("[Playwright] Avvio browser Microsoft Edge Headless... — Immobiliare Giancani")
            return playwright_instance.chromium.launch(channel="msedge", headless=True, args=launch_args)
        except Exception as e:
            print(f"[Playwright] Fallback da Edge a Chromium standard ({e})... — Immobiliare Giancani")

    print("[Playwright] Avvio browser Chromium Headless (compatibile GitHub Actions)... — Immobiliare Giancani")
    return playwright_instance.chromium.launch(headless=True, args=launch_args)


def costruisci_lista_pagine_subito():
    pagine = []
    for nome_comune, slug in COMUNI_SUBITO_SLUGS:
        if nome_comune.lower() in TARGET_COMUNI:
            url_privati = f"https://www.subito.it/annunci-sicilia/vendita/immobili/agrigento/{slug}/?order=datedesc&f=p"
            pagine.append((f"Comune di {nome_comune} (SOLO PRIVATI)", url_privati))
            url_tutti = f"https://www.subito.it/annunci-sicilia/vendita/immobili/agrigento/{slug}/?order=datedesc"
            pagine.append((f"Comune di {nome_comune} (Tutti)", url_tutti))

    pagine.append(("Agrigento Provincia (SOLO PRIVATI)", "https://www.subito.it/annunci-sicilia/vendita/immobili/agrigento/?order=datedesc&f=p"))
    pagine.append(("Agrigento Provincia Pagina 1", "https://www.subito.it/annunci-sicilia/vendita/immobili/agrigento/?order=datedesc"))
    pagine.append(("Agrigento Provincia Pagina 2", "https://www.subito.it/annunci-sicilia/vendita/immobili/agrigento/?order=datedesc&o=2"))
    return pagine


def esegui_ciclo_scansione():
    print("\n" + "=" * 75)
    print("🎯 CACCIATORI DI IMMOBILI — SCANSIONE, SMISTAMENTO & MEMORIA 30 GIORNI")
    print("Brand: Immobiliare Giancani • Antonio Giancani (+39 320 166 7156)")
    print(f"Orario Scansione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Comuni Target: {', '.join(CONFIG.get('comuni_target', []))}")
    print("=" * 75)

    db = carica_db()
    immobili_db = db.setdefault("immobili", {})

    annunci_raccolti = []

    with sync_playwright() as p:
        browser = avvia_browser_playwright(p)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="it-IT",
            timezone_id="Europe/Rome"
        )
        page = context.new_page()

        def intercept(route):
            url_req = route.request.url.lower()
            if any(ext in url_req for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".woff", ".woff2", ".ttf"]):
                return route.abort()
            if any(trk in url_req for trk in ["googletagmanager", "criteo", "datadome", "adnxs", "doubleclick", "amazon-adsystem"]):
                return route.abort()
            return route.continue_()

        page.route("**/*", intercept)

        pagine_da_scansionare = costruisci_lista_pagine_subito()

        for label, url in pagine_da_scansionare:
            print(f"\n[Scansione Feed] {label} -> {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(1500)
                trovati = estrai_annunci_subito(page.content())
                print(f"  Trovati {len(trovati)} annunci target in questa pagina. — Immobiliare Giancani")
                annunci_raccolti.extend(trovati)
            except Exception as e:
                print(f"  Errore caricamento {label}: {e} — Immobiliare Giancani")

        # Scansione automatica dei Portali Minori (Bakeca, CasaDaPrivato, Cambiocasa, PCase)
        for nome_portale, url_portale, base_portale in costruisci_lista_portali_minori():
            print(f"\n[Scansione Portale Minore] {nome_portale} -> {url_portale}")
            try:
                page.goto(url_portale, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1500)
                trovati_min = estrai_portale_generico(page.content(), nome_portale, base_portale)
                print(f"  Trovati {len(trovati_min)} annunci target su {nome_portale}. — Immobiliare Giancani")
                annunci_raccolti.extend(trovati_min)
            except Exception as e:
                print(f"  Nota {nome_portale}: {e} — Immobiliare Giancani")

        visti_in_questo_giro = set()
        annunci_unici = []
        for ann in annunci_raccolti:
            if ann["id"] not in visti_in_questo_giro:
                visti_in_questo_giro.add(ann["id"])
                annunci_unici.append(ann)

        for item in annunci_unici:
            if item["id"] not in immobili_db and item.get("is_privato", False):
                if len(item.get("descrizione", "")) < 60:
                    arricchisci_dettaglio_annuncio(page, item)

        browser.close()
        print("[Playwright] Browser chiuso regolarmente. — Immobiliare Giancani")

    nuovi_privati = 0
    passaggi_rilevati = 0
    ribassi_privati = 0
    ribassi_agenzie = 0

    for item in annunci_unici:
        item_id = item["id"]
        is_privato = item.get("is_privato", False)
        prezzo_attuale = item.get("prezzo", "")
        p_attuale_num = parse_prezzo_numerico(prezzo_attuale)

        if item_id not in immobili_db:
            item["prezzo_iniziale"] = prezzo_attuale
            item["storico_prezzi"] = [{"data": datetime.now().strftime("%Y-%m-%d"), "prezzo": prezzo_attuale}]
            immobili_db[item_id] = item
            if is_privato:
                nuovi_privati += 1
                if is_item_in_memoria_30gg(item, db):
                    print(f"  ⏭️ [Già in Memoria 30gg - Skip Notifica]: {item['comune']} - {item['titolo'][:40]} — Immobiliare Giancani")
                else:
                    print(f"  🚨 [Nuovo Privato Rilevato]: {item['comune']} - {item['titolo'][:40]} ({prezzo_attuale}) — Immobiliare Giancani")
                    invia_notifica_telegram(item, event_type="NUOVO_PRIVATO")
                    time.sleep(1)
        else:
            vecchio = immobili_db[item_id]
            vecchio_privato = vecchio.get("is_privato", False)
            vecchio_prezzo = vecchio.get("prezzo", "")
            p_vecchio_num = parse_prezzo_numerico(vecchio_prezzo)
            p_iniziale_str = vecchio.get("prezzo_iniziale") or vecchio_prezzo
            storico = vecchio.get("storico_prezzi", [{"data": vecchio.get("timestamp", "")[:10], "prezzo": p_iniziale_str}])

            # Controllo passaggio da Agenzia a Privato
            if not vecchio_privato and is_privato:
                passaggi_rilevati += 1
                print(f"  🔄 [Passaggio ad Annuncio Privato!]: {item['comune']} - {item['titolo'][:40]} — Immobiliare Giancani")
                invia_notifica_telegram(
                    item,
                    event_type="PASSAGGIO_AGENZIA_PRIVATO",
                    old_price=vecchio_prezzo,
                    old_agency=vecchio.get("nome_agenzia")
                )
                vecchio.update(item)
                time.sleep(1)

            # Controllo variazione/ribasso prezzo (sia su Privati sia su Agenzie!)
            elif p_vecchio_num > 0 and p_attuale_num > 0 and p_vecchio_num != p_attuale_num:
                diff = p_attuale_num - p_vecchio_num
                storico.append({"data": datetime.now().strftime("%Y-%m-%d"), "prezzo": prezzo_attuale, "delta": diff})
                vecchio["prezzo_precedente"] = vecchio_prezzo
                vecchio["prezzo"] = prezzo_attuale
                vecchio["storico_prezzi"] = storico
                vecchio["data_ultimo_ribasso"] = datetime.now().strftime("%Y-%m-%d %H:%M")

                if is_privato:
                    ribassi_privati += 1
                    print(f"  📉 [Ribasso Prezzo Privato]: {item['comune']} - {item['titolo'][:40]} (da {vecchio_prezzo} a {prezzo_attuale}) — Immobiliare Giancani")
                    invia_notifica_telegram(vecchio, event_type="RIBASSO_PREZZO", old_price=vecchio_prezzo)
                    time.sleep(1)
                else:
                    if diff < 0:
                        ribassi_agenzie += 1
                        print(f"  🏢📉 [Ribasso Prezzo Agenzia]: {item.get('nome_agenzia')} - {item['comune']} (da {vecchio_prezzo} a {prezzo_attuale}) — Immobiliare Giancani")
                        invia_notifica_telegram(vecchio, event_type="RIBASSO_AGENZIA", old_price=vecchio_prezzo)
                        time.sleep(1)

            # Aggiornamento metadati continui
            vecchio["prezzo_iniziale"] = p_iniziale_str
            vecchio["storico_prezzi"] = storico
            vecchio["descrizione"] = item.get("descrizione") or vecchio.get("descrizione", "")
            vecchio["latitudine"] = item.get("latitudine") or vecchio.get("latitudine", "")
            vecchio["longitudine"] = item.get("longitudine") or vecchio.get("longitudine", "")
            if item.get("user_id"):
                vecchio["user_id"] = item["user_id"]
            if item.get("nome_privato") and item.get("nome_privato") != "Proprietario Privato":
                vecchio["nome_privato"] = item["nome_privato"]
                vecchio["nome_inserzionista"] = item["nome_privato"]
                vecchio["email"] = item["nome_privato"]
            if item.get("telefono"):
                vecchio["telefono"] = item["telefono"]
            if item.get("email_contatto"):
                vecchio["email_contatto"] = item["email_contatto"]
            if item.get("note"):
                vecchio["note"] = item["note"]
            vecchio["ultimo_rilevamento"] = datetime.now().isoformat()

    # Ricalcola smistamento (Privati / Sospetti Agenzie / Agenzie + Ribassi) e pulizia memoria 30 giorni
    classifica_sospetti_agenzie_e_ribassi(immobili_db)
    aggiorna_e_pulisci_memoria_30gg(db)
    salva_db(db)

    # Rigenera la pagina HTML interattiva
    html_generato = None
    parent_dir = os.path.dirname(BASE_DIR)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    try:
        import genera_pagina_risultati
        html_generato = genera_pagina_risultati.genera_html_resoconto()
    except Exception as e:
        print(f"  [HTML Dashboard Errore]: {e} — Immobiliare Giancani")

    # Pubblica la pagina HTML aggiornata su GitHub Pages per l'uso da cellulare
    if html_generato and os.path.exists(html_generato):
        pubblica_su_github_pages({
            html_generato: "cacciatori.html",
            DB_PATH: "cacciatore_db.json"
        })

    # Invia batch complessivo a Google Apps Script / Sheet
    if annunci_unici:
        print("\n[Google Sheet] Sincronizzazione con il foglio Google... — Immobiliare Giancani")
        invia_a_google_apps_script(list(immobili_db.values())[:220])

    # Invia il Report Giornaliero Telegram con i nuovi numeri da contattare su WhatsApp o Email
    invia_report_giornaliero_contatti_telegram(db, html_path=html_generato)

    print("\n" + "=" * 75)
    print("✅ CICLO DI SCANSIONE E SINCRONIZZAZIONE TERMINATO CON SUCCESSO")
    print(f"Totale DB: {len(immobili_db)} | Nuovi Privati: {nuovi_privati} | Ribassi Privati: {ribassi_privati} | Ribassi Agenzie: {ribassi_agenzie}")
    print("— Immobiliare Giancani")
    print("=" * 75)


def main():
    esegui_ciclo_scansione()


if __name__ == "__main__":
    main()
