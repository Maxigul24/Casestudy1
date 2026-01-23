import streamlit as st
import time

# Initialize state
if "state" not in st.session_state:
    st.session_state["state"] = "Geld_einwerfen"

# Callback function to change state
# Callback function are triggered when the button is clicked
def go_to_state_start():
    st.session_state["state"] = "Geld_einwerfen"

def go_to_state_a():
    st.session_state["state"] = "Getraenk_waehlen"

def go_to_state_b():
    st.session_state["state"] = "Cola"

def go_to_state_c():
    st.session_state["state"] = "Fanta"

def go_to_state_exit():
    st.session_state["state"] = "state_exit"

if st.session_state["state"] == "Geld_einwerfen":
    st.text("Geld einwerfen")
    betrag_geld = st.text_area("Betrag eingeben")
    if betrag_geld is None:
        betrag_geld = 0.0
    preis_getraenk = 1.5
    if betrag_geld is not None:
        if float(betrag_geld) >= preis_getraenk:
            st.button("bezahlen %f" % float(betrag_geld), type="primary", on_click=go_to_state_a)
            rückgeld = float(betrag_geld) - preis_getraenk
            st.text("Rückgeld: %f" % rückgeld)
        elif float(betrag_geld) < preis_getraenk:
            st.text("Zu wenig Geld eingeworfen")

if st.session_state["state"] == "Getraenk_waehlen":
    st.text("Getreank waelen") 
    st.button("cola", type="primary", on_click=go_to_state_b)
    st.button("fanta", type="primary", on_click=go_to_state_c)

elif st.session_state["state"] == "Cola":
    st.text("Cola gekauft")
    time.sleep(3)
    go_to_state_start()
    st.rerun()
    

elif st.session_state["state"] == "Fanta":
    st.text("Fanta gekauft")
    time.sleep(3)
    go_to_state_start()
    st.rerun()

elif st.session_state["state"] == "state_exit":
    st.text("I'm in exit state")
    st.button("Restart!", type="primary", on_click=go_to_state_start)
