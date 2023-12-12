import streamlit as st
import pandas as pd
import json
import requests
import datetime
import sqlite3
import smtplib
from email.message import EmailMessage
import base64


def create_database():
    conn = sqlite3.connect('padel.db')
    c = conn.cursor()
    c.execute("""
    SELECT name FROM sqlite_master WHERE type='table' AND name='players'
    """)
    if not c.fetchone():
        c.execute('''CREATE TABLE players
                     (email text, day text, time text)''')
        conn.commit()
    conn.close()

def add_player(email, day, time):
    conn = sqlite3.connect('padel.db')
    c = conn.cursor()
    c.execute("INSERT INTO players VALUES (?, ?, ?)", (email, day, time))
    conn.commit()
    conn.close()

def search_player(email, day, time):
    conn = sqlite3.connect('padel.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM players WHERE day=? AND time=?", (day, time))
    players = c.fetchone()
    conn.close()
    return players, day, time

def get_players(day, time):
    conn = sqlite3.connect("padel.db")
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE day = ? AND time = ?", (day, time))
    players = c.fetchall()
    conn.close()
    return players

def delete_player(email):
    conn = sqlite3.connect('padel.db')
    c = conn.cursor()
    c.execute("DELETE FROM players WHERE email=?", (email,))
    conn.commit()
    conn.close()

def reset_players():
    conn = sqlite3.connect('padel.db')
    c = conn.cursor()
    c.execute("DELETE FROM players")
    conn.commit()
    conn.close()

def view_players():
    conn = sqlite3.connect('padel.db')
    c = conn.cursor()
    c.execute("SELECT * FROM players")
    players = c.fetchall()
    conn.close()
    return players

def send_email(to_address, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "michele.epicode@gmail.com"
    msg['To'] = to_address

    # Connessione al server SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("michele.epicode@gmail.com", "Giacomo160511")
    server.send_message(msg)
    server.quit()

def notify_users(users, slot_time):
    subject = f"Prenotazione confermata per {slot_time}"
    body = f"La tua prenotazione per il padel è stata confermata per {slot_time}."
    for user in users:
        send_email(user[0], subject, body)

def sidebar_bg(side_bg):

   side_bg_ext = 'webp'

   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
      }}
      </style>
      """,
      unsafe_allow_html=True,
      )

def main():

    st.header('Gestione partite di Padel')

    side_bg = 'images/padel.webp'
    sidebar_bg(side_bg)

    create_database()

    #taking input from user
    emailaddr = st.text_input('Inserisci l\'indirizzo email',value="", type="default")
    giorno = st.date_input('Inserisci il giorno in cui vuoi giocare', value="today", format="DD/MM/YYYY")
    ora = st.time_input('Inserisci l\'ora in cui vuoi giocare', value="now", step=datetime.timedelta(minutes=60))

    #converting the input into a json format
    inputs = {"giorni": str(giorno), "ora": str(ora), "callback": str(emailaddr)}

    #when the user clicks on button it will fetch the API
    if st.button('Invio richiesta'):
        
        prenotazioni = search_player(str(emailaddr), str(giorno), str(ora))
        if int(prenotazioni[0][0]) >= 4:
            st.write("Il campo è già al completo per questo orario")
        else:
            add_player(str(emailaddr), str(giorno), str(ora))

            #fetching the API
            res = requests.post(url = "http://127.0.0.1:8000/disponibilita", data = json.dumps(inputs))
            st.write(f"{res.text}")

            #searching for players
            prenotazioni = search_player(str(emailaddr), str(giorno), str(ora))

            if int(prenotazioni[0][0]) >= 4:
                st.write("Prenotazione partita completata")
                giocatori = get_players(str(prenotazioni[1]), str(prenotazioni[2]))
                # notify_users(str(giocatori), str(giorno)+str(ora))
    
    if st.sidebar.button('Cancella prenotazione'):
        delete_player(str(emailaddr))
        st.write("Prenotazione cancellata", str(emailaddr))
    
    if st.sidebar.button('Reset prenotazioni'):
        reset_players()
        st.write("Tutte le prenotazioni sono state cancellate")

    #Dashboard
    st.subheader("Prenotazioni")
    Chart_Data = pd.DataFrame(view_players(), columns=['email', 'giorno', 'ora'])
    st.scatter_chart(Chart_Data, x='giorno', y='ora', size=(200),color=None, use_container_width=True) 

if __name__ == '__main__':
    main()
