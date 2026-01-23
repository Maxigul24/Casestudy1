from datetime import datetime
import streamlit as st
import pandas as pd
from users import User
from devices import Device

st.write("# Gerätemanagement")

tab1, tab2, tab3, tab4 = st.tabs(["Geräte", "Nutzerverwaltung", "Reservierungen", "Wartungsplan"])

with tab1:
    st.header("Geräteübersicht")
    all_devices = Device.find_all()
    all_users_for_devices = User.find_all()
    user_emails = [u.id for u in all_users_for_devices]
    
    devices_data = []
    for dev in all_devices:
        devices_data.append({
            "ID": dev.id,                 
            "Name": dev.name,
            "Typ": dev.device_type,        
            "Verantwortlich": dev.managed_by_user_id,
            "Status": dev.status,          
            "Nächste_Wartung": dev.next_maintenance.strftime("%Y-%m-%d"),
            "Tage_bis_Wartung": dev.get_days_until_maintenance()
        })
    
    df_devices = pd.DataFrame(devices_data)
    
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
    
    if event_devices.selection.rows:
        selected_idx = event_devices.selection.rows[0]
        selected_device_id = df_devices.iloc[selected_idx]["ID"]
        
        selected_device_obj = Device.find_by_attribute("id", int(selected_device_id))
        
        if selected_device_obj:
            st.divider()
            st.subheader(f"Gerät bearbeiten: {selected_device_obj.name}")
            
            with st.form(f"edit_device_{selected_device_obj.id}"):
                # Vorbefüllte Werte aus dem OBJEKT
                edit_name = st.text_input("Name", value=selected_device_obj.name)
                edit_typ = st.text_input("Typ", value=selected_device_obj.device_type)
                
                # Verantwortlich Dropdown mit allen Nutzern
                if user_emails and selected_device_obj.managed_by_user_id in user_emails:
                    curr_user_index = user_emails.index(selected_device_obj.managed_by_user_id)
                else:
                    curr_user_index = 0
                edit_verantwortlich = st.selectbox("Verantwortlich", user_emails, index=curr_user_index if user_emails else 0)
                
                status_options = ["Verfügbar", "In Wartung", "Reserviert", "Defekt"]
                try:
                    curr_index = status_options.index(selected_device_obj.status)
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
                    selected_device_obj.name = edit_name
                    selected_device_obj.device_type = edit_typ
                    selected_device_obj.managed_by_user_id = edit_verantwortlich
                    selected_device_obj.status = edit_status
                    
                    selected_device_obj.store_data()
                    st.success(f"Gerät {edit_name} aktualisiert!")
                    st.rerun()
                    
                if deleted:
                    selected_device_obj.delete()
                    st.warning(f"Gerät {edit_name} gelöscht!")
                    st.rerun()

    st.divider()
    
    if 'show_add_device' not in st.session_state:
        st.session_state.show_add_device = False
    
    if not st.session_state.show_add_device:
        if st.button("➕ Neues Gerät hinzufügen"):
            st.session_state.show_add_device = True
            st.rerun()
    
    if st.session_state.show_add_device:
        st.subheader("Neues Gerät anlegen")
        with st.form("new_device_form"):
            new_name = st.text_input("Gerätename")
            new_typ = st.text_input("Gerätetyp (z.B. Laser, 3D-Drucker)")
            new_verantwortlich = st.selectbox("Verantwortlicher Nutzer", user_emails if user_emails else ["Keine Nutzer vorhanden"])
            new_status = st.selectbox("Status", ["Verfügbar", "In Wartung", "Reserviert", "Defekt"])
            
            col1, col2 = st.columns(2)
            with col1:
                submitted_new = st.form_submit_button("Gerät speichern")
            with col2:
                cancel = st.form_submit_button("Abbrechen")
            
            if submitted_new:
                if new_name and new_verantwortlich:
                    # ID generieren
                    current_devices = Device.find_all()
                    if current_devices:
                        new_id = max([d.id for d in current_devices]) + 1
                    else:
                        new_id = 1
                    
                    # Neues Objekt erstellen
                    new_device = Device(
                        id=new_id,
                        name=new_name,
                        managed_by_user_id=new_verantwortlich,
                        device_type=new_typ,
                        status=new_status
                    )
                    
                    new_device.store_data()
                    st.success(f"Gerät {new_name} angelegt!")
                    st.session_state.show_add_device = False
                    st.rerun()
                else:
                    st.warning("Bitte Name und Verantwortlichen angeben.")
            
            if cancel:
                st.session_state.show_add_device = False
                st.rerun()
with tab2:
    st.header("Nutzerverwaltung")
    
    all_users = User.find_all()
    
    
    users_data = []
    for u in all_users:
        users_data.append({
            "Name": u.name,
            "Email": u.id  
        })
    
    df_users = pd.DataFrame(users_data)
    
    # Tabelle anzeigen
    event_users = st.dataframe(
        df_users,
        use_container_width=True,
        selection_mode="single-row",
        on_select="rerun",
        key="user_table",
        hide_index=True
    )
    
    
    if event_users.selection.rows:
        selected_idx = event_users.selection.rows[0]
        selected_email = df_users.iloc[selected_idx]["Email"]
        
        selected_user_obj = next((u for u in all_users if u.id == selected_email), None)
        
        if selected_user_obj:
            st.divider()
            st.subheader(f"Nutzer bearbeiten: {selected_user_obj.name}")
            
            with st.form(f"edit_user_{selected_user_obj.id}"):
                edit_name = st.text_input("Name", value=selected_user_obj.name)
                st.text_input("Email (ID)", value=selected_user_obj.id, disabled=True)
                st.caption("Hinweis: Um die E-Mail zu ändern, bitte Nutzer löschen und neu anlegen.")
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Änderungen speichern")
                with col2:
                    deleted = st.form_submit_button("Nutzer löschen", type="secondary")
                
                if submitted:
                    # Objekt aktualisieren
                    selected_user_obj.name = edit_name
                    # Speichern
                    selected_user_obj.store_data()
                    st.success(f"Nutzer {edit_name} aktualisiert!")
                    st.rerun()
                    
                if deleted:
                    selected_user_obj.delete()
                    st.warning(f"Nutzer gelöscht!")
                    st.rerun()
    
    st.divider()

    if 'show_add_user' not in st.session_state:
        st.session_state.show_add_user = False
    
    if not st.session_state.show_add_user:
        if st.button("➕ Neuen Nutzer hinzufügen"):
            st.session_state.show_add_user = True
            st.rerun()
    
    # Formular nur anzeigen, wenn show_add_user True ist
    if st.session_state.show_add_user:
        st.subheader("Neuen Nutzer anlegen")
        with st.form("new_user_form"):
            new_name = st.text_input("Name")
            new_email = st.text_input("Email (wird als ID verwendet)")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted_new = st.form_submit_button("Nutzer speichern")
            with col2:
                cancel = st.form_submit_button("Abbrechen")
            
            if submitted_new:
                if new_name and new_email:
                    # Prüfen, ob Email schon existiert (Optional, aber gut)
                    existing = next((u for u in all_users if u.id == new_email), None)
                    if existing:
                        st.error("Ein Nutzer mit dieser E-Mail existiert bereits!")
                    else:
                        # Objekt erstellen
                        new_user = User(id=new_email, name=new_name)
                        new_user.store_data()
                        st.success(f"Nutzer {new_name} angelegt!")
                        st.session_state.show_add_user = False
                        st.rerun()
                else:
                    st.warning("Bitte Name und Email eingeben.")
            
            if cancel:
                st.session_state.show_add_user = False
                st.rerun()        
with tab3:
    st.header("Reservierungen")
    
    # Import Reservation class
    from reservation import Reservation
    
    all_reservations = Reservation.find_all()
    all_devices_for_res = Device.find_all()
    all_users_for_res = User.find_all()
    
    reservations_data = []
    for res in all_reservations:
        device_name = res.device_id
        for dev in all_devices_for_res:
            if str(dev.id) == str(res.device_id):
                device_name = dev.name
                break
        
        reservations_data.append({
            "ID": res.id,
            "Gerät": device_name,
            "Reserviert von": res.user_id,
            "Start": res.start_date.strftime("%Y-%m-%d") if res.start_date else "",
            "Ende": res.end_date.strftime("%Y-%m-%d") if res.end_date else "",
            "Grund": res.reason,
            "Status": res.status
        })
    
    st.subheader("Alle Reservierungen")
    
    if reservations_data:
        df_reservations = pd.DataFrame(reservations_data)
        event_reservations = st.dataframe(
            df_reservations, 
            use_container_width=True, 
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            key="reservation_table"
        )
        
        if event_reservations.selection.rows:
            selected_idx = event_reservations.selection.rows[0]
            selected_res_id = df_reservations.iloc[selected_idx]["ID"]
            
            # Das passende Objekt finden
            selected_res_obj = next((r for r in all_reservations if r.id == selected_res_id), None)
            
            if selected_res_obj:
                st.divider()
                st.subheader(f"Reservierung bearbeiten")
                
                with st.form(f"edit_reservation_{selected_res_obj.id}"):
                    st.text(f"ID: {selected_res_obj.id}")
                    st.text(f"Gerät: {selected_res_obj.device_id}")
                    st.text(f"Nutzer: {selected_res_obj.user_id}")
                    st.text(f"Zeitraum: {selected_res_obj.start_date.strftime('%d.%m.%Y')} - {selected_res_obj.end_date.strftime('%d.%m.%Y')}")
                    
                    # Status ändern
                    status_options = ["Aktiv", "Storniert", "Abgeschlossen"]
                    try:
                        curr_idx = status_options.index(selected_res_obj.status)
                    except ValueError:
                        curr_idx = 0
                    edit_status = st.selectbox("Status", status_options, index=curr_idx)
                    edit_reason = st.text_area("Grund", value=selected_res_obj.reason)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("Änderungen speichern")
                    with col2:
                        deleted = st.form_submit_button("Reservierung löschen", type="secondary")
                    
                    if submitted:
                        selected_res_obj.status = edit_status
                        selected_res_obj.reason = edit_reason
                        selected_res_obj.store_data()
                        st.success("Reservierung aktualisiert!")
                        st.rerun()
                    
                    if deleted:
                        selected_res_obj.delete()
                        st.warning("Reservierung gelöscht!")
                        st.rerun()
    else:
        st.info("Keine Reservierungen vorhanden.")
    
    st.divider()
    st.subheader("Neue Reservierung erstellen")
    with st.form("new_reservation"):
        device_names = [d.name for d in all_devices_for_res]
        geraet = st.selectbox("Gerät", device_names if device_names else ["Keine Geräte vorhanden"])
       
        user_emails = [u.id for u in all_users_for_res]
        reserviert_von = st.selectbox("Reserviert von", user_emails if user_emails else ["Keine Nutzer vorhanden"])
        
        col1, col2 = st.columns(2)
        with col1:
            start_datum = st.date_input("Start-Datum")
        with col2:
            end_datum = st.date_input("End-Datum")
        grund = st.text_area("Grund der Reservierung")
        
        submitted = st.form_submit_button("Reservierung speichern")
        if submitted:
            if geraet and reserviert_von:
                target_device = next((d for d in all_devices_for_res if d.name == geraet), None)
                
                if target_device:
                    if end_datum < start_datum:
                        st.error("Fehler: Enddatum muss nach dem Startdatum liegen!")
                    else:
                        start_dt = datetime.combine(start_datum, datetime.min.time())
                        end_dt = datetime.combine(end_datum, datetime.min.time())
                        
                        if Reservation.check_availability(str(target_device.id), start_dt, end_dt):
                            new_reservation = Reservation(
                                user_id=reserviert_von,
                                device_id=str(target_device.id),
                                start_date=start_dt,
                                end_date=end_dt,
                                reason=grund
                            )
                            new_reservation.store_data()
                            st.success(f"Reservierung für {geraet} wurde erstellt!")
                            st.rerun()
                        else:
                            st.error(f"Konflikt: {geraet} ist im gewählten Zeitraum bereits reserviert!")
                else:
                    st.error("Gerät nicht gefunden.")
            else:
                st.warning("Bitte Gerät und Nutzer auswählen.")


with tab4:
    st.header("Wartungsplan")
    all_devices_objects = Device.find_all()
    
    st.subheader("Geräte in Wartung")
    
    geraete_in_wartung = [d for d in all_devices_objects if d.status == "In Wartung"]
    
    if geraete_in_wartung:
        wartung_data = []
        for dev in geraete_in_wartung:
            tage_verbleibend = "Unbekannt" 
            
            wartung_data.append({
                "Gerät": dev.name,                 
                "Typ": dev.device_type,            
                "Verantwortlich": dev.managed_by_user_id,
                "Status": dev.status
            })
        df_wartung = pd.DataFrame(wartung_data)
        st.dataframe(df_wartung, use_container_width=True)
    else:
        st.info("Aktuell befinden sich keine Geräte in Wartung.")
    
    st.divider()
    
    st.subheader("Anstehende Wartungen")
    
    aktive_geraete = [d for d in all_devices_objects if d.status != "In Wartung"]
    
    wartungsplan = sorted(
        aktive_geraete,
        key=lambda x: x.get_days_until_maintenance()
    )
    
    wartungsplan_data = []
    for dev in wartungsplan:
        tage = dev.get_days_until_maintenance()
        
        wartungsplan_data.append({
            "Gerät": dev.name,
            "Typ": dev.device_type,
            "Nächste Wartung": dev.next_maintenance.strftime("%Y-%m-%d"),
            "Tage bis Wartung": tage,
            "Verantwortlich": dev.managed_by_user_id
        })
    
    df_wartungsplan = pd.DataFrame(wartungsplan_data)
    st.dataframe(df_wartungsplan, use_container_width=True)    
    
    st.divider()
    
    st.subheader("Wartung planen")
    with st.form("plan_wartung"):
        geraet_name = st.selectbox("Gerät", [d.name for d in all_devices_objects])
        neues_wartungsdatum = st.date_input("Nächstes Wartungsdatum")
        wartungsnotizen = st.text_area("Notizen")
        
        submitted = st.form_submit_button("Wartung planen")
        if submitted:
            target_device = Device.find_by_attribute("name", geraet_name)
            
            if target_device:
                st.success(f"Wartung für {geraet_name} am {neues_wartungsdatum} geplant!")
            else:
                st.error("Gerät nicht gefunden.")
    
    st.divider()
    
    st.subheader("Wartungskosten pro Quartal")
    
    if all_devices_objects:
        kosten_data = []
        gesamtkosten = 0.0
        
        for dev in all_devices_objects:
            quartal_kosten = dev.calculate_quarterly_maintenance_cost()
            gesamtkosten += quartal_kosten
            
            kosten_data.append({
                "Gerät": dev.name,
                "Typ": dev.device_type,
                "Wartungsintervall (Tage)": dev.maintenance_interval,
                "Kosten pro Wartung (€)": f"{dev.maintenance_cost:.2f}",
                "Kosten pro Quartal (€)": f"{quartal_kosten:.2f}"
            })
        
        df_kosten = pd.DataFrame(kosten_data)
        st.dataframe(df_kosten, use_container_width=True, hide_index=True)
        
        # Gesamtkosten anzeigen
        st.metric(
            label="📊 Gesamte Wartungskosten pro Quartal",
            value=f"{gesamtkosten:.2f} €"
        )
    else:
        st.info("Keine Geräte vorhanden für Kostenberechnung.")