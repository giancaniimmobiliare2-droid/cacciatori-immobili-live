# Regola Mandatoria: Memoria Contatti & Soppressione 30 Giorni — Immobiliare Giancani

Documento di specifica tecnica per integrare il sistema di **blocco automatico dei contatti già gestiti** (WhatsApp, Email, Telefono, SMS o qualsiasi altro canale) in altri progetti dell'ecosistema **Immobiliare Giancani**.

---

## 🎯 Obiettivo Funzionale
Quando un operatore invia un messaggio su **WhatsApp**, **Email**, oppure contatta il proprietario tramite **qualsiasi altro canale** (chiamata, SMS, chat portale), quel **numero di telefono** e quell'**immobile** non devono più riapparire il giorno successivo né nei giorni seguenti (per **30 giorni**) in:
1. **Coda e Lista "Da Contattare"** della Console HTML.
2. **Schede "Privati Verificati" e "Sospetti Agenzie"**.
3. **Notifiche e Report Telegram** generati dal Bot Python.

Trascorsi **30 giorni** dall'invio, il blocco scade automaticamente per consentire un eventuale ricontatto.

---

## 🔑 Regole Chiave di Implementazione

### 1. Normalizzazione Univoca del Numero di Telefono
Per evitare che lo stesso numero ricompaia con o senza prefisso `+39` / `0039`, la chiave telefonica va sempre normalizzata prima del salvataggio e del confronto:
- Rimuovere tutti i caratteri non numerici (`\D`).
- Se inizia con `0039` e ha lunghezza > 12, rimuovere `0039`.
- Se inizia con `39` e ha lunghezza > 10, rimuovere `39`.

### 2. Chiavi Multiple di Blocco (Immobile + Recapito)
Ogni contatto registrato genera fino a **3 chiavi** nella memoria condivisa (`GIANCANI_MEMORIA_30GG` / `MEMORIA_INVII_30GG`):
1. `item.id` (ID univoco dell'annuncio)
2. `TEL_<telefono_normalizzato>` (blocca il numero su qualsiasi annuncio/ripubblicazione)
3. `EMAIL_<email_normalizzata>` (blocca l'email su qualsiasi annuncio)

### 3. Struttura Record JSON
```json
{
  "id": "subito_123456789",
  "telefono": "3201234567",
  "email_contatto": "proprietario@esempio.it",
  "nome": "Mario Rossi",
  "comune": "Favara",
  "canale": "WHATSAPP",
  "data_invio": "22/11/2026 12:00",
  "timestamp_ms": 1795345200000,
  "giorni_rimanenti": 30
}
```
Valori supportati per `canale`: `"WHATSAPP"`, `"EMAIL"`, `"CONTATTO_DIRETTO"` (o qualsiasi altro canale manuale).

---

## 🔄 Flusso di Sincronizzazione a 3 Livelli

1. **Frontend HTML/JS (`localStorage` + Cloud Sync)**:
   - Al click su **WhatsApp 1-Click**, **Email 1-Click** o **✅ Già Contattato (30gg)** viene invocata `registraInvioInMemoria30Giorni(item, canale)`.
   - Salva immediatamente in `localStorage.GIANCANI_MEMORIA_30GG` ed esegue `POST` verso il webhook Google Apps Script (`action: "registra_invio_presentazione"`).
   - All'apertura della pagina, `sincronizzaMemoriaCloud()` scarica `?action=get_memoria_contatti` e fonde la memoria cloud con `localStorage`.
   - Tutti i tab di lavoro (`renderNumeriPrivati`, `renderPrivati`, `renderSospetti`) filtrano `!getStatoMemoriaItem(x, mem)`.

2. **Backend Cloud (`Google Apps Script` / `Code.gs`)**:
   - `registraInvioPresentazioneCloud(dati)` salva il record in `PropertiesService.getScriptProperties()` sotto `"MEMORIA_INVII_30GG"` usando `normalizzaTelefonoChiave(dati.telefono)`.
   - `caricaMemoriaInvii30Giorni()` elimina automaticamente i record con `nowMs - timestamp_ms >= 30 * 24 * 60 * 60 * 1000`.
   - `doGet` con `?action=get_memoria_contatti` espone la mappa aggiornata sia al frontend HTML che al bot Python.

3. **Bot di Scansione (`Python` / `cacciatore_bot.py`)**:
   - All'avvio del ciclo (`carica_db()`), `aggiorna_e_pulisci_memoria_30gg(db)` scarica la memoria dal Cloud Apps Script, normalizza le chiavi `TEL_`, rimuove i record scaduti (> 30 gg) e imposta `contattato_30gg = True` sugli immobili corrispondenti.
   - Durante la scansione, `is_item_in_memoria_30gg(item, db)` impedisce l'invio di notifiche Telegram per immobili o numeri già contattati.
   - Il report giornaliero esclude `contattato_30gg == True` da `wa_da_contattare` e `email_da_contattare`.

---

## 🧩 Snippet Pronti per l'Integrazione

### JavaScript (Frontend)
```javascript
function normalizzaTelefonoChiave(tel) {
  let digits = (tel || '').replace(/\D/g, '');
  if (digits.startsWith('0039') && digits.length > 12) digits = digits.slice(4);
  else if (digits.startsWith('39') && digits.length > 10) digits = digits.slice(2);
  return digits;
}

function getStatoMemoriaItem(item, mem) {
  const telRaw = (item.telefono || '').replace(/\D/g, '');
  const telClean = normalizzaTelefonoChiave(telRaw);
  const emClean = (item.email_contatto || '').toLowerCase().trim();
  return mem[item.id]
    || (telClean.length >= 8 ? mem['TEL_' + telClean] : null)
    || (telRaw.length >= 8 ? mem['TEL_' + telRaw] : null)
    || (emClean ? mem['EMAIL_' + emClean] : null)
    || null;
}
```

### Python (Bot / Scraper)
```python
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
```

---

## 📜 Standard Obbligatori del Progetto
- Testi estratti rigorosamente dalla **Colonna F**.
- Superfici riportate per esteso come **"metri quadri"** (mai `mq` o `m²`).
- Chiusura di ogni testo/messaggio con: **`— Immobiliare Giancani`**
