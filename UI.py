import streamlit as st
import pandas as pd
from datetime import datetime

# Wir versuchen die Backend-Klassen zu laden.
# Falls 'devices.py' noch Leerzeichen hat oder fehlt, fangen wir den Fehler ab.
try:
    from devices import Device
    from users import User
    BACKEND_LOADED = True
except ImportError as e:
    st.error(f"Backend-Fehler: {e}. Bitte stelle sicher, dass 'devices.py' korrekt benannt ist.")
    BACKEND_LOADED = False

st.write("# Gerätemanagement")

tab1, tab2, tab3, tab4 = st.tabs(["Geräte", "Nutzerverwaltung", "Reservierungen", "Wartungsplan"])

# --- HILFSFUNKTIONEN ---
def load_all_devices_safe():
    """Lädt Geräte sicher, auch wenn die DB leer ist oder Fehler wirft."""
    if not BACKEND_LOADED: return []
    try:
        return Device.find_all()
    except Exception:
        return []

# --- TAB 1: GERÄTE ---
with tab1:
    st.header("Geräteübersicht")
    
    all_devices = load_all_devices_safe()
    
    # Daten für die Tabelle aufbereiten
    devices_list = []
    for dev in all_devices:
        # Wir fangen Fehler bei der Datumsberechnung ab
        try:
            days = dev.get_days_until_maintenance()
            next_maint = dev.next_maintenance.strftime('%Y-%m-%d')
        except:
            days = 0
            next_maint = "Fehler"

        devices_list.append({
            "ID": dev.device_id,
            "Name": dev.device_name,
            "Typ": "Standard", 
            "Verantwortlich": dev.managed_by_user_id,
            "Status": "Aktiv" if dev.is_active else "In Wartung/Inaktiv",
            "Nächste_Wartung": next_maint,
            "Tage_bis_Wartung": days
        })
    
    st.subheader(f"Alle Geräte ({len(devices_list)})")
    
    df_devices = pd.DataFrame(devices_list)
    
    # Tabelle anzeigen
    if not df_devices.empty:
        event_devices = st.dataframe(
            df_devices,
            use_container_width=True,
            selection_mode="single-row",
            on_select="rerun",
            key="device_table",
            hide_index=True
        )
    else:
        st.info("Keine Geräte gefunden.")
        event_devices = None

    # Bearbeiten-Logik
    if event_devices and event_devices.selection.rows:
        selected_idx = event_devices.selection.rows[0]
        selected_device_data = devices_list[selected_idx]
        
        # Das echte Objekt aus der Liste suchen
        real_device = next((d for d in all_devices if d.device_id == selected_device_data["ID"]), None)
        
        if real_device:
            st.divider()
            st.subheader(f"Gerät bearbeiten: {real_device.device_name}")
            
            with st.form("edit_device"):
                edit_name = st.text_input("Name", value=real_device.device_name)
                
                # User-Dropdown
                try:
                    all_users = [u.id for u in User.find_all()]
                except:
                    all_users = []
                
                current_user = real_device.managed_by_user_id
                if current_user in all_users:
                    u_index = all_users.index(current_user)
                    edit_verantwortlich = st.selectbox("Verantwortlich", all_users, index=u_index)
                else:
                    edit_verantwortlich = st.text_input("Verantwortlich", value=current_user)

                # Status bearbeiten
                status_options = ["Aktiv", "In Wartung"]
                current_status_idx = 0 if real_device.is_active else 1
                edit_status = st.selectbox("Status", status_options, index=current_status_idx)
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Speichern")
                with col2:
                    deleted = st.form_submit_button("Löschen", type="primary")
                
                if submitted:
                    real_device.device_name = edit_name
                    real_device.set_managed_by_user_id(edit_verantwortlich)
                    # Status Logik
                    real_device.is_active = (edit_status == "Aktiv")
                    real_device.store_data()
                    st.success("Gespeichert!")
                    st.rerun()
                if deleted:
                    real_device.delete()
                    st.warning("Gelöscht!")
                    st.rerun()
    
    st.divider()
    # Neues Gerät
    with st.expander("Neues Gerät hinzufügen"):
        with st.form("new_device"):
            new_id = st.number_input("ID", step=1, min_value=1)
            name = st.text_input("Name")
            
            try:
                user_options = [u.id for u in User.find_all()]
            except:
                user_options = []
                
            verantwortlich = st.selectbox("Verantwortlich", user_options) if user_options else st.text_input("Verantwortlich (Email)")
            
            submitted = st.form_submit_button("Gerät speichern")
            if submitted:
                if BACKEND_LOADED:
                    new_dev = Device(new_id, name, verantwortlich)
                    new_dev.store_data()
                    st.success(f"Gerät {name} angelegt!")
                    st.rerun()

# --- TAB 2: NUTZER ---
with tab2:
    st.header("Nutzerverwaltung")
    
    try:
        user_objects = User.find_all()
    except:
        user_objects = []
        
    users_data = [{"Name": u.name, "Email": u.id} for u in user_objects]
    st.dataframe(pd.DataFrame(users_data), use_container_width=True, hide_index=True)
    
    st.divider()
    with st.form("new_user"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        if st.form_submit_button("Nutzer speichern") and BACKEND_LOADED:
            User(email, name).store_data()
            st.success("Nutzer angelegt!")
            st.rerun()

# --- TAB 3: RESERVIERUNGEN (Visuelle Demo) ---
with tab3:
    st.header("Reservierungen")
    st.info("Dieses Modul läuft aktuell im Demo-Modus (keine Datenbank-Anbindung).")
    
    # Mock-Daten (damit die Tabelle nicht leer ist)
    reservations = [
        {"Gerät": "Laser-Cutter", "Von": "one@mci.edu", "Start": "2025-12-16", "Ende": "2025-12-20"},
        {"Gerät": "3D-Drucker", "Von": "two@mci.edu", "Start": "2025-12-18", "Ende": "2025-12-22"},
    ]
    st.dataframe(pd.DataFrame(reservations), use_container_width=True)
    
    st.divider()
    st.subheader("Neue Reservierung")
    
    with st.form("new_reservation"):
        # Wir versuchen echte Gerätenamen zu laden, sonst Fallback
        devs = load_all_devices_safe()
        dev_names = [d.device_name for d in devs] if devs else ["Beispielgerät 1", "Beispielgerät 2"]
        
        st.selectbox("Gerät", dev_names)
        st.text_input("Reserviert von")
        c1, c2 = st.columns(2)
        c1.date_input("Start")
        c2.date_input("Ende")
        
        if st.form_submit_button("Reservieren"):
            st.success("Reservierung (simuliert) erfolgreich!")

# --- TAB 4: WARTUNGSPLAN ---
with tab4:
    st.header("Wartungsplan")
    
    all_devices_maint = load_all_devices_safe()

    # 1. Geräte in Wartung
    st.subheader("Geräte aktuell in Wartung")
    # HINWEIS: Wenn devices.py den Status nicht lädt, ist diese Liste immer leer.
    in_wartung = [d for d in all_devices_maint if not d.is_active]
    
    if in_wartung:
        data_w = [{"Gerät": d.device_name, "Verantwortlich": d.managed_by_user_id} for d in in_wartung]
        st.dataframe(pd.DataFrame(data_w), use_container_width=True)
    else:
        st.info("Keine Geräte als 'Inaktiv / In Wartung' markiert.")

    st.divider()
    
    # 2. Anstehende Wartungen
    st.subheader("Anstehende Wartungen")
    
    # Sicherstellen, dass die Datumsberechnung nicht crasht
    valid_devices = []
    for d in all_devices_maint:
        if d.is_active: # Nur aktive Geräte planen
            try:
                # Testen ob Berechnung klappt
                d.get_days_until_maintenance()
                valid_devices.append(d)
            except:
                continue

    # Sortieren
    valid_devices.sort(key=lambda x: x.get_days_until_maintenance())
    
    plan_data = []
    for d in valid_devices:
        plan_data.append({
            "Gerät": d.device_name,
            "Nächste Wartung": d.next_maintenance.strftime('%Y-%m-%d'),
            "Tage verbleibend": d.get_days_until_maintenance(),
            "Kosten": f"{d.maintenance_cost} €"
        })
        
    df_plan = pd.DataFrame(plan_data)
    
    # Einfärbung
    def highlight_urgent(val):
        color = ''
        if isinstance(val, int):
            if val < 0: color = 'background-color: #ffcccc'
            elif val < 10: color = 'background-color: #ffffcc'
        return color

    if not df_plan.empty:
        st.dataframe(df_plan.style.map(highlight_urgent, subset=['Tage verbleibend']), use_container_width=True, hide_index=True)
        
        # Wartung durchführen Button
        st.write("### Wartung abschließen")
        with st.form("complete_maint"):
            target_name = st.selectbox("Gerät wählen", [d.device_name for d in valid_devices])
            if st.form_submit_button("Wartung als erledigt markieren"):
                dev_obj = next((d for d in valid_devices if d.device_name == target_name), None)
                if dev_obj:
                    dev_obj.complete_maintenance()
                    dev_obj.store_data()
                    st.success(f"Wartung für {target_name} protokolliert!")
                    st.rerun()
    else:
        st.info("Keine aktiven Geräte für den Wartungsplan.")