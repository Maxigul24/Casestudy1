from datetime import datetime
import streamlit as st
import pandas as pd
from users import User
from devices import Device

# Eine Überschrift der ersten Ebene
st.write("# Gerätemanagement")

tab1, tab2, tab3, tab4 = st.tabs(["Geräte", "Nutzerverwaltung", "Reservierungen", "Wartungsplan"])

with tab1:
    st.header("Geräteübersicht")
    
    # ---------------------------------------------------------
    # 1. DATEN LADEN & TABELLE ANZEIGEN
    # ---------------------------------------------------------
    # Echte Daten aus der Datenbank laden
    all_devices = Device.find_all()
    
    # Daten für den DataFrame aufbereiten
    devices_data = []
    for dev in all_devices:
        devices_data.append({
            "ID": dev.device_id,           # Wichtig für die Identifikation
            "Name": dev.device_name,
            "Typ": dev.device_type,        # Kommt aus dem Objekt
            "Verantwortlich": dev.managed_by_user_id,
            "Status": dev.device_status,   # Kommt aus dem Objekt
            "Nächste_Wartung": dev.next_maintenance.strftime("%Y-%m-%d"),
            "Tage_bis_Wartung": dev.get_days_until_maintenance()
        })
    
    df_devices = pd.DataFrame(devices_data)
    
    # Konfiguration: Wir verstecken die ID-Spalte optisch, nutzen sie aber für die Logik
    column_configuration = {
        "ID": st.column_config.NumberColumn("ID", disabled=True) 
    }

    # Interaktive Tabelle anzeigen
    event_devices = st.dataframe(
        df_devices,
        column_config=column_configuration,
        use_container_width=True,
        selection_mode="single-row",
        on_select="rerun",
        key="device_table",
        hide_index=True
    )
    
    # ---------------------------------------------------------
    # 2. GERÄT BEARBEITEN (Wenn eine Zeile ausgewählt wurde)
    # ---------------------------------------------------------
    if event_devices.selection.rows:
        selected_idx = event_devices.selection.rows[0]
        selected_device_id = df_devices.iloc[selected_idx]["ID"]
        
        # Das echte Objekt aus der DB laden
        # Wir nutzen deine find_by_attribute Methode
        selected_device_obj = Device.find_by_attribute("device_id", int(selected_device_id))
        
        if selected_device_obj:
            st.divider()
            st.subheader(f"Gerät bearbeiten: {selected_device_obj.device_name}")
            
            with st.form(f"edit_device_{selected_device_obj.device_id}"):
                # Vorbefüllte Werte aus dem OBJEKT
                edit_name = st.text_input("Name", value=selected_device_obj.device_name)
                edit_typ = st.text_input("Typ", value=selected_device_obj.device_type)
                edit_verantwortlich = st.text_input("Verantwortlich", value=selected_device_obj.managed_by_user_id)
                
                # Status Dropdown Logic
                status_options = ["Verfügbar", "In Wartung", "Reserviert", "Defekt"]
                try:
                    curr_index = status_options.index(selected_device_obj.device_status)
                except ValueError:
                    curr_index = 0
                
                edit_status = st.selectbox("Status", status_options, index=curr_index)
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Änderungen speichern")
                with col2:
                    deleted = st.form_submit_button("Gerät löschen", type="secondary")
                
                if submitted:
                    # Objekt aktualisieren
                    selected_device_obj.device_name = edit_name
                    selected_device_obj.device_type = edit_typ
                    selected_device_obj.managed_by_user_id = edit_verantwortlich
                    selected_device_obj.device_status = edit_status
                    
                    selected_device_obj.store_data()
                    st.success(f"Gerät {edit_name} aktualisiert!")
                    st.rerun()
                    
                if deleted:
                    selected_device_obj.delete()
                    st.warning(f"Gerät {edit_name} gelöscht!")
                    st.rerun()

    st.divider()
    
    # ---------------------------------------------------------
    # 3. NEUES GERÄT HINZUFÜGEN (Expander)
    # ---------------------------------------------------------
    with st.expander("Neues Gerät hinzufügen"):
        st.subheader("Neues Gerät anlegen")
        with st.form("new_device_form"):
            new_name = st.text_input("Gerätename")
            new_typ = st.text_input("Gerätetyp (z.B. Laser, 3D-Drucker)")
            new_verantwortlich = st.text_input("Verantwortliche User-ID (E-Mail)")
            new_status = st.selectbox("Status", ["Verfügbar", "In Wartung", "Reserviert", "Defekt"])
            
            submitted_new = st.form_submit_button("Gerät speichern")
            
            if submitted_new:
                if new_name and new_verantwortlich:
                    # ID generieren
                    current_devices = Device.find_all()
                    if current_devices:
                        new_id = max([d.device_id for d in current_devices]) + 1
                    else:
                        new_id = 1
                    
                    # Neues Objekt erstellen
                    new_device = Device(
                        device_id=new_id,
                        device_name=new_name,
                        managed_by_user_id=new_verantwortlich,
                        device_type=new_typ,
                        device_status=new_status
                    )
                    
                    new_device.store_data()
                    st.success(f"Gerät {new_name} angelegt!")
                    st.rerun()
                else:
                    st.warning("Bitte Name und Verantwortlichen angeben.")
with tab2:
    st.header("Nutzerverwaltung")
    
    # Lade alle User aus der Datenbank
    user_objects = User.find_all()
    users = [{"Name": u.name, "Email": u.id} for u in user_objects]
    
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
    if event_devices.selection.rows:
        selected_idx = event_devices.selection.rows[0]
        selected_device_id = df_devices.iloc[selected_idx]["ID"]
        
        # Objekt aus DB laden
        device_obj = Device.find_by_attribute("device_id", int(selected_device_id))
        
        if device_obj:
            st.divider()
            st.subheader(f"Gerät bearbeiten: {device_obj.device_name}")
            
            with st.form("edit_device"):
                # Vorbelegung mit echten Daten
                edit_name = st.text_input("Name", value=device_obj.device_name)
                edit_typ = st.text_input("Typ", value=device_obj.device_type)
                edit_verantwortlich = st.text_input("Verantwortlich", value=device_obj.managed_by_user_id)
                
                # Status Dropdown
                status_options = ["Verfügbar", "In Wartung", "Reserviert", "Defekt"]
                # Index finden (Fallback auf 0, falls aktueller Status unbekannt)
                try:
                    curr_index = status_options.index(device_obj.device_status)
                except ValueError:
                    curr_index = 0
                    
                edit_status = st.selectbox("Status", status_options, index=curr_index)
                
                submitted = st.form_submit_button("Änderungen speichern")
                
                if submitted:
                    # Werte im Objekt überschreiben
                    device_obj.device_name = edit_name
                    device_obj.device_type = edit_typ
                    device_obj.managed_by_user_id = edit_verantwortlich
                    device_obj.device_status = edit_status
                    
                    # Speichern
                    device_obj.store_data()
                    st.success("Gespeichert!")
                    st.rerun()
    
    st.divider()
    st.subheader("Neuen Nutzer hinzufügen")
    with st.form("new_user"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Nutzer speichern")
        if submitted:
            if name and email:
                # Speichere neuen User in der Datenbank
                new_user = User(email, name)
                new_user.store_data()
                st.success(f"Nutzer {name} wurde hinzugefügt!")
                st.rerun()
            else:
                st.error("Bitte Name und Email eingeben!")
        
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
    
    # 1. Wir laden die echten Objekte aus der Datenbank
    # WICHTIG: Das sind jetzt Instanzen deiner Klasse Device, keine Dictionaries mehr!
    all_devices_objects = Device.find_all()
    
    # ---------------------------------------------------------
    # Teil A: Geräte in Wartung
    # ---------------------------------------------------------
    st.subheader("Geräte in Wartung")
    
    # Filtern: Wir nutzen Punkt-Notation (.device_status statt ["Status"])
    geraete_in_wartung = [d for d in all_devices_objects if d.device_status == "In Wartung"]
    
    if geraete_in_wartung:
        wartung_data = []
        for dev in geraete_in_wartung:
            # Hier berechnen wir die Restzeit. 
            # Da dein Backend noch kein 'Wartung_bis' Feld hat, nehmen wir einen Platzhalter 
            # oder berechnen es basierend auf dem Wartungsintervall.
            tage_verbleibend = "Unbekannt" 
            
            wartung_data.append({
                "Gerät": dev.device_name,          # .device_name statt ["Name"]
                "Typ": dev.device_type,            # .device_type statt ["Typ"]
                "Verantwortlich": dev.managed_by_user_id,
                "Status": dev.device_status
            })
        df_wartung = pd.DataFrame(wartung_data)
        st.dataframe(df_wartung, use_container_width=True)
    else:
        st.info("Aktuell befinden sich keine Geräte in Wartung.")
    
    st.divider()
    
    # ---------------------------------------------------------
    # Teil B: Anstehende Wartungen
    # ---------------------------------------------------------
    st.subheader("Anstehende Wartungen")
    
    # Filter: Alle Geräte, die NICHT in Wartung sind
    aktive_geraete = [d for d in all_devices_objects if d.device_status != "In Wartung"]
    
    # Sortieren: Wir nutzen die Methode .get_days_until_maintenance() für die Sortierung
    wartungsplan = sorted(
        aktive_geraete,
        key=lambda x: x.get_days_until_maintenance()
    )
    
    wartungsplan_data = []
    for dev in wartungsplan:
        # Hier nutzen wir die Methoden deiner Klasse
        tage = dev.get_days_until_maintenance()
        
        wartungsplan_data.append({
            "Gerät": dev.device_name,
            "Typ": dev.device_type,
            "Nächste Wartung": dev.next_maintenance.strftime("%Y-%m-%d"),
            "Tage bis Wartung": tage,
            "Verantwortlich": dev.managed_by_user_id
        })
    
    df_wartungsplan = pd.DataFrame(wartungsplan_data)
    st.dataframe(df_wartungsplan, use_container_width=True)    
    
    st.divider()
    
    # ---------------------------------------------------------
    # Teil C: Wartung planen (Formular)
    # ---------------------------------------------------------
    st.subheader("Wartung planen")
    with st.form("plan_wartung"):
        # Dropdown Liste mit Namen füllen
        geraet_name = st.selectbox("Gerät", [d.device_name for d in all_devices_objects])
        neues_wartungsdatum = st.date_input("Nächstes Wartungsdatum")
        wartungsnotizen = st.text_area("Notizen")
        
        submitted = st.form_submit_button("Wartung planen")
        if submitted:
            # 1. Das passende Objekt wiederfinden
            target_device = Device.find_by_attribute("device_name", geraet_name)
            
            if target_device:
                # Hier könntest du Logik einbauen, um das Datum wirklich zu speichern
                # Z.B.: target_device.next_maintenance = ...
                # target_device.store_data()
                st.success(f"Wartung für {geraet_name} am {neues_wartungsdatum} geplant!")
            else:
                st.error("Gerät nicht gefunden.")