from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime, timedelta
import locale
import pytz

app = Flask(__name__)
FILENAME = "baillements.csv"
timezone = pytz.timezone("Europe/Paris")

# Mettre en français le format des dates
locale.setlocale(locale.LC_TIME, "")

# Vérifie si le fichier existe, sinon le crée avec un en-tête
def init_csv():
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp"])

init_csv()

# Lire la dernière entrée enregistrée
def read_last_entry():
    try:
        with open(FILENAME, mode='r') as file:
            reader = list(csv.reader(file))
            if len(reader) > 1:
                return format_datetime(reader[-1][0])
            return "Aucun enregistrement"
    except Exception:
        return "Erreur de lecture"

# Transformer la date en format "Lundi 1 Janvier - 00:00"
def format_datetime(timestamp):
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%A %d %B - %H:%M")

# Obtenir les bâillements filtrés
def get_filtered_baillements(period):
    now = datetime.now()
    filters = {
        'jour': now - timedelta(days=1),
        'semaine': now - timedelta(weeks=1),
        'mois': now - timedelta(days=30),
        'annee': now - timedelta(days=365),
        'toujours': None
    }
    
    with open(FILENAME, mode='r') as file:
        reader = list(csv.reader(file))[1:]
        baillements = [datetime.fromisoformat(row[0]) for row in reader]
        if filters[period]:
            baillements = [b for b in baillements if b >= filters[period]]
    return [b.isoformat() for b in baillements]

@app.route('/')
def index():
    last_baillement = read_last_entry()
    return render_template('index.html', last_baillement=last_baillement)

@app.route('/add', methods=['POST'])
def add_baillement():
    # Obtenir l'heure actuelle avec le fuseau horaire spécifié
    now = datetime.now(timezone)
    
    # Formater et enregistrer l'heure dans le fichier CSV
    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([now.isoformat()])  # Enregistrer l'heure dans le format ISO
    return redirect(url_for('index'))

@app.route('/history/<period>')
def history(period):
    # Obtenir les bâillements filtrés pour l'affichage principal
    baillements = get_filtered_baillements(period)
    baillements = [datetime.fromisoformat(b) if isinstance(b, str) else b for b in baillements]
    
    # Lire tous les bâillements pour les frises des trois derniers jours
    now = datetime.now()
    last_three_days = [now - timedelta(days=i) for i in range(3)]
    baillements_last_three_days = {str(d.date()): [] for d in last_three_days}
    with open(FILENAME, mode='r') as file:
        reader = list(csv.reader(file))[1:]
        all_baillements = [datetime.fromisoformat(row[0]) for row in reader]
        for b in all_baillements:
            if b.date() in [d.date() for d in last_three_days]:
                baillements_last_three_days[str(b.date())].append(b.hour + b.minute / 60)  # Heure en décimal
    
    return render_template('history.html', baillements=baillements, period=period, graph_data=baillements_last_three_days)

@app.route('/delete_last', methods=['POST'])
def delete_last_entry():
    try:
        with open(FILENAME, mode='r') as file:
            reader = list(csv.reader(file))
        if len(reader) > 1:
            with open(FILENAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(reader[:-1])
    except Exception as e:
        print(f"Erreur lors de la suppression de l'entrée : {e}")
    return redirect(url_for('history', period='toujours'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)