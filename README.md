# DEBUGHUB 🚀
<img src="hakaton/static/images/logo.png" width="256" height="256" alt="logo" align="Center" />  

## Descriere

**DEBUGHUB** este o platformă inovatoare unde fiecare problemă pe care o rezolvi este creată de inteligența artificială. Indiferent dacă ești începător sau un programator experimentat, provocările generate de AI sunt concepute să se adapteze la nivelul tău de cunoștințe și să te împingă să gândești practic.

### 🎯 Caracteristici Principale

- **🤖 Provocări Generate de AI**: Utilizează OpenAI GPT pentru a crea probleme de programare personalizate
- **🔍 Evaluare Automată**: Evaluează soluțiile tale cu feedback folosind AI
- **👤 Sistem de Autentificare**: Înregistrare și autentificare utilizatori cu Django
- **📊 Urmărirea Progresului**: Monitorizează submisiile și progresul tău în timp

## 🛠️ Tehnologii Utilizate

### Backend
- **Django 5.2** - Framework web Python
- **SQLite** - Baza de date
- **OpenAI API** - Pentru generarea provocărilor și feedback-ul AI
- **Python 3.10+** - Limbajul de programare principal

### Frontend
- **HTML5/CSS3** - Markup și stilizare
- **JavaScript** - Funcționalitate dinamică
- **Bootstrap** - Framework CSS pentru design responsive

### Dependințe Principale
- `django` - Framework web
- `openai` - Integrare API OpenAI
- `python-decouple` - Gestionarea variabilelor de mediu


## 📖 Utilizare

### Pentru Utilizatori

1. **Înregistrare/Autentificare**
   - Creează un cont nou sau autentifică-te cu unul existent

2. **Explorarea Provocărilor**
   - Navighează la secțiunea "Challenges" pentru a vedea provocările disponibile
   - Filtrează după dificultate sau caută anumite subiecte
   - Vizualizează detaliile unei provocări specifice

3. **Crearea de Provocări**
   - Accesează "Challenge Creator"
   - Generează un challenge pe baza subiectului și nivelului dorit
   - Selectează un pas din challenge
   - Lasă AI-ul să creeze o provocare personalizată

4. **Evaluarea Soluțiilor**
   - Accesează "Solution Evaluator"
   - Selectează o provocare
   - Scrie codul soluției
   - Primește feedback detaliat generat de AI

### Pentru Administratori

1. **Accesează panoul de admin**
   ```
   http://localhost:8000/admin
   ```

2. **Gestionează provocările**
   - Creează, editează sau șterge provocări
   - Monitorizează submisiile utilizatorilor
   - Vizualizează statistici

## 🔧 Configurare Avansată

### Configurare Producție

1. **Setează DEBUG=False în .env**
2. **Configurează o bază de date PostgreSQL**
3. **Setează ALLOWED_HOSTS**
4. **Configurează servirea fișierelor statice**

### Personalizare

- **Stiluri CSS**: Modifică `static/style.css`
- **Template-uri**: Editează fișierele din `templates/`
- **Modele**: Extinde modelele din `models.py`


## 🐛 Probleme Cunoscute

- Evaluarea codului este limitată la feedback AI (fără execuție reală)
- Interface-ul este optimizat pentru desktop
- Suportul pentru limbaje de programare este limitat în prezent

## 🔮 Planuri Viitoare

- [ ] Execuția și testarea automată a codului
- [ ] Suport pentru mai multe limbaje de programare
- [ ] Sistem de gamification și badge-uri
- [ ] Interfață mobilă optimizată
- [ ] Integrare cu GitHub pentru portfolio
- [ ] Sistem de clasamente și competiții
