from datetime import datetime
from flask import Flask, jsonify, request, render_template, redirect, url_for
from email_service import EmailService
from google_sheets_service import GoogleSheetsService
from qr_code_service import QRCodeService
import os, json

app = Flask(__name__)

# Configuration

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "config.json")
settings={}
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        settings=json.load(f)
SPREADSHEET_ID = settings.get("SPREADSHEET_ID")
GMAIL_SENDER_EMAIL = settings.get("GMAIL_SENDER_EMAIL")
GMAIL_PASSWORD = settings.get("GMAIL_PASSWORD")

# Initialize services
email_service = EmailService("smtp.gmail.com", 587, GMAIL_SENDER_EMAIL, GMAIL_PASSWORD)
google_sheets_service = GoogleSheetsService(CREDENTIALS_FILE, SPREADSHEET_ID)
qr_code_service = QRCodeService()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/participants")
def participants():
    try:
        participants = google_sheets_service.get_registered_participants()
        return render_template("participants.html", participants=participants)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch participants: {e}"}), 500


@app.route("/attendees")
def attendees():
    try:
        attendees = google_sheets_service.fetch_attendance_sheet()
        return render_template("attendees.html", attendees=attendees)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch attendees: {e}"}), 500

@app.route("/scanner")
def scanner():
    return render_template("scanner.html")

@app.route('/send-qr-email', methods=['GET'])
def send_qr_email():
    # Fetch data from Google Sheets
    participants = google_sheets_service.get_registered_participants()
    print(participants)

    results = []  # Collect results for each participant

    for participant in participants:
        name = participant['Name']
        email = participant['Email']
        id = participant['ID']
        unique_data = f"ID: {id}, Name: {name}, Email: {email}"  # QR Code data

        # Generate QR code
        qr_filename = f"{name}_qr.png"
        qr_code_service.generate_qr(unique_data, qr_filename)

        # Send email with QR code
        subject = "Your Event QR Code"
        body = f"Hi {name},\n\nHere is your QR code for the event. Please find it attached."
        try:
            email_service.send_email(email, subject, body, qr_filename)
            print(f"QR code sent to {email}")
            results.append({"email": email, "status": "success"})
        except Exception as e:
            print(f"Failed to process {email}: {e}")
            results.append({"email": email, "status": "failed", "error": str(e)})

        # Delete the QR code file after sending
        if os.path.exists(qr_filename):
            os.remove(qr_filename)

    return jsonify({"results": results}), 200

@app.route('/get-registered', methods=['GET'])
def get_registered():
    try:
        participants = google_sheets_service.get_registered_participants()
        return jsonify({"participants": participants}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch participants: {e}"}), 500
    
@app.route('/get-attendees', methods=['GET'])
def get_attendees():
    try:
        participants = google_sheets_service.fetch_attendance_sheet()
        return jsonify({"participants": participants}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch attendees: {e}"}), 500
    
@app.route('/mark-attendance', methods=['POST','GET'])
def mark_attendance():
    data = request.json  
    print(data)
    attendee_id = data.get('id')
    name = data.get('name')
    email = data.get('email')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    attendee_data = [attendee_id, name, email, timestamp]
    try:
        attendance_records = google_sheets_service.fetch_attendance_sheet()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch attendees: {e}"}), 500
    try:
        registered = google_sheets_service.get_registered_participants()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch registerations: {e}"}), 500
    
    for row in attendance_records:
        if str(row.get("ID")).strip() == attendee_id:
            return jsonify({"success": False, "message": "Already marked present!"})
    if not any(str(row.get("ID")).strip() == attendee_id for row in registered):
            return jsonify({"success": False, "message": "Not found in registrations!"})

    try:
        # Append the attendee data to Sheet2
        google_sheets_service.append_attendee(attendee_data)
        return jsonify({"success": True,"message": f"Attendance marked for {name}"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to mark attendance: {e}"}), 500

# Changing the sheet
@app.route('/set-sheet', methods=['GET', 'POST'])
def set_sheet():
    if request.method == 'POST':
        new_sheet_id = request.form.get('sheet_id')
        if new_sheet_id:
            settings["SPREADSHEET_ID"]=new_sheet_id
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
            return redirect(url_for('home'))  # Redirect to home after setting
    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)
    current_sheet=settings.get("SPREADSHEET_ID", "Not Set")
    return render_template('set_sheet.html', current_sheet_id=current_sheet) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


