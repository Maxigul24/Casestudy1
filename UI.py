import streamlit as st
import pandas as pd

# Eine Überschrift der ersten Ebene
st.write("# Gerätemanagement")

tab1, tab2, tab3, tab4 = st.tabs(["Geräte", "Nutzerverwaltung", "Reservierungen", "Wartungsplan"])

with tab1:
    st.header("Geräteübersicht")
    
    # Mock-Daten für Geräte
    from datetime import datetime, timedelta
    
    devices = [
        {"Name": "Laser-Cutter", "Typ": "Laser", "Verantwortlich": "Max Müller", "Status": "Verfügbar", 
         "Nächste_Wartung": "2025-12-25", "Wartung_bis": None, "Tage_bis_Wartung": 10},
        {"Name": "3D-Drucker", "Typ": "3D-Druck", "Verantwortlich": "Anna Schmidt", "Status": "In Wartung", 
         "Nächste_Wartung": "2025-12-15", "Wartung_bis": "2025-12-18", "Tage_bis_Wartung": 0},
        {"Name": "CNC-Fräse", "Typ": "Fräse", "Verantwortlich": "Tom Weber", "Status": "Reserviert", 
         "Nächste_Wartung": "2026-01-05", "Wartung_bis": None, "Tage_bis_Wartung": 21},
        {"Name": "Oszilloskop", "Typ": "Messinstrument", "Verantwortlich": "Lisa Klein", "Status": "Verfügbar", 
         "Nächste_Wartung": "2025-12-20", "Wartung_bis": None, "Tage_bis_Wartung": 5},
    ]
    
    st.subheader("Alle Geräte")
    
    # Geräte als Tabelle anzeigen
    df_devices = pd.DataFrame(devices)
    
    event_devices = st.dataframe(
        df_devices,
        use_container_width=True,
        selection_mode="single-row",
        on_select="rerun",
        key="device_table"
    )
    
    # Wenn eine Zeile ausgewählt wurde
    if event_devices.selection.rows:
        selected_idx = event_devices.selection.rows[0]
        selected_device = devices[selected_idx]
        
        st.divider()
        st.subheader(f"Gerät bearbeiten: {selected_device['Name']}")
        
        with st.form("edit_device"):
            edit_name = st.text_input("Name", value=selected_device["Name"])
            edit_typ = st.text_input("Typ", value=selected_device["Typ"])
            edit_verantwortlich = st.text_input("Verantwortlich", value=selected_device["Verantwortlich"])
            edit_status = st.selectbox("Status", ["Verfügbar", "In Wartung", "Reserviert", "Defekt"], 
                                       index=["Verfügbar", "In Wartung", "Reserviert", "Defekt"].index(selected_device["Status"]))
            
            # Wartungsinformationen
            st.write("**Wartungsinformationen**")
            if selected_device["Status"] == "In Wartung" and selected_device["Wartung_bis"]:
                st.info(f"⚠️ In Wartung bis: {selected_device['Wartung_bis']}")
            else:
                st.info(f"🔧 Nächste Wartung in {selected_device['Tage_bis_Wartung']} Tagen ({selected_device['Nächste_Wartung']})")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Änderungen speichern")
            with col2:
                deleted = st.form_submit_button("Gerät löschen", type="secondary")
            
            if submitted:
                st.success(f"Gerät {edit_name} wurde aktualisiert!")
            if deleted:
                st.warning(f"Gerät {selected_device['Name']} wurde gelöscht!")
    
    st.divider()
    
    # Button zum Hinzufügen neuer Geräte
    if st.button("Neues Gerät hinzufügen"):
        st.subheader("Neues Gerät hinzufügen")
        with st.form("new_device"):
            name = st.text_input("Name")
            typ = st.text_input("Typ")
            verantwortlich = st.text_input("Verantwortlich")
            status = st.selectbox("Status", ["Verfügbar", "In Wartung", "Reserviert", "Defekt"])
            submitted = st.form_submit_button("Gerät speichern")
            if submitted:
                st.success(f"Gerät {name} wurde hinzugefügt!")

with tab2:
    st.header("Nutzerverwaltung")
    
    # Mock-Daten
    users = [
        {"Name": "Max Müller", "Email": "max.mueller@hochschule.de", "Rolle": "Administrator"},
        {"Name": "Anna Schmidt", "Email": "anna.schmidt@hochschule.de", "Rolle": "Mitarbeiter"},
        {"Name": "Tom Weber", "Email": "tom.weber@hochschule.de", "Rolle": "Student"},
        {"Name": "Lisa Klein", "Email": "lisa.klein@hochschule.de", "Rolle": "Student"},
    ]
    
    st.subheader("Alle Nutzer")
    
   
    df = pd.DataFrame(users)
    
    event = st.dataframe(
        df,
        use_container_width=True,
        selection_mode="single-row",
        on_select="rerun",
        key="user_table"
    )
    
    # Wenn eine Zeile ausgewählt wurde
    if event.selection.rows:
        selected_idx = event.selection.rows[0]
        selected_user = users[selected_idx]
        
        st.divider()
        st.subheader(f"Nutzer bearbeiten: {selected_user['Name']}")
        
        with st.form("edit_user"):
            edit_name = st.text_input("Name", value=selected_user["Name"])
            edit_email = st.text_input("Email", value=selected_user["Email"])
            edit_rolle = st.selectbox("Rolle", ["Administrator", "Mitarbeiter", "Student"], 
                                      index=["Administrator", "Mitarbeiter", "Student"].index(selected_user["Rolle"]))
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Änderungen speichern")
            with col2:
                deleted = st.form_submit_button("Nutzer löschen", type="secondary")
            
            if submitted:
                st.success(f"Nutzer {edit_name} wurde aktualisiert!")
            if deleted:
                st.warning(f"Nutzer {selected_user['Name']} wurde gelöscht!")
    
    st.divider()
    if st.button("Neuen Nutzer hinzufügen"):
        st.subheader("Neuen Nutzer hinzufügen")
        with st.form("new_user"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            rolle = st.selectbox("Rolle", ["Administrator", "Mitarbeiter", "Student"])
            submitted = st.form_submit_button("Nutzer speichern")
            if submitted:
                st.success(f"Nutzer {name} wurde hinzugefügt!")
        
with tab3:
    st.header("Reservierungen")
    
    # Mock-Daten
    reservations = [
        {"Gerät": "Laser-Cutter", "Reserviert von": "Prof. Müller", "Start": "2025-12-16", "Ende": "2025-12-20", "Grund": "Forschungsprojekt"},
        {"Gerät": "3D-Drucker", "Reserviert von": "Anna Schmidt", "Start": "2025-12-18", "Ende": "2025-12-22", "Grund": "Lehrlabor"},
        {"Gerät": "CNC-Fräse", "Reserviert von": "Tom Weber", "Start": "2025-12-15", "Ende": "2025-12-17", "Grund": "Abschlussarbeit"},
        {"Gerät": "Laser-Cutter", "Reserviert von": "Lisa Klein", "Start": "2025-12-22", "Ende": "2025-12-25", "Grund": "Studentenprojekt"},
    ]
    
    st.subheader("Alle Reservierungen")
    
    df_reservations = pd.DataFrame(reservations)
    st.dataframe(df_reservations, use_container_width=True)
    
    st.divider()
    
    # Neue Reservierung hinzufügen
    st.subheader("Neue Reservierung erstellen")
    with st.form("new_reservation"):
        geraet = st.selectbox("Gerät", ["Laser-Cutter", "3D-Drucker", "CNC-Fräse", "Oszilloskop"])
        reserviert_von = st.text_input("Reserviert von")
        col1, col2 = st.columns(2)
        with col1:
            start_datum = st.date_input("Start-Datum")
        with col2:
            end_datum = st.date_input("End-Datum")
        grund = st.text_area("Grund der Reservierung")
        
        submitted = st.form_submit_button("Reservierung speichern")
        if submitted:
            st.success(f"Reservierung für {geraet} wurde erstellt!")

with tab4:
    st.header("Wartungsplan")
    
    # Geräte in Wartung
    st.subheader("Geräte in Wartung")
    geraete_in_wartung = [d for d in devices if d["Status"] == "In Wartung"]
    
    if geraete_in_wartung:
        wartung_data = []
        for device in geraete_in_wartung:
            wartung_ende = datetime.strptime(device["Wartung_bis"], "%Y-%m-%d")
            tage_verbleibend = (wartung_ende - datetime.now()).days
            wartung_data.append({
                "Gerät": device["Name"],
                "Typ": device["Typ"],
                "Verantwortlich": device["Verantwortlich"],
                "Wartung bis": device["Wartung_bis"],
                "Verbleibende Tage": tage_verbleibend
            })
        df_wartung = pd.DataFrame(wartung_data)
        st.dataframe(df_wartung, use_container_width=True)
    else:
        st.info("Aktuell befinden sich keine Geräte in Wartung.")
    
    st.divider()
    
    # Anstehende Wartungen
    st.subheader("Anstehende Wartungen")
    
    # Sort
    # iere Geräte nach Tagen bis zur Wartung
    wartungsplan = sorted(
        [d for d in devices if d["Status"] != "In Wartung"],
        key=lambda x: x["Tage_bis_Wartung"]
    )
    
    wartungsplan_data = []
    for device in wartungsplan:
        tage = device["Tage_bis_Wartung"]
        wartungsplan_data.append({
            "Gerät": device["Name"],
            "Typ": device["Typ"],
            "Nächste Wartung": device["Nächste_Wartung"],
            "Tage bis Wartung": device["Tage_bis_Wartung"],
            "Verantwortlich": device["Verantwortlich"]
        })
    
    df_wartungsplan = pd.DataFrame(wartungsplan_data)
    st.dataframe(df_wartungsplan, use_container_width=True)    
    st.divider()
    
    # Wartung planen
    st.subheader("Wartung planen")
    with st.form("plan_wartung"):
        geraet_wartung = st.selectbox("Gerät", [d["Name"] for d in devices])
        neues_wartungsdatum = st.date_input("Nächstes Wartungsdatum")
        wartungsnotizen = st.text_area("Notizen")
        
        submitted = st.form_submit_button("Wartung planen")
        if submitted:
            st.success(f"Wartung für {geraet_wartung} am {neues_wartungsdatum} geplant!")