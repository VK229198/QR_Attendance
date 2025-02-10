from oauth2client.service_account import ServiceAccountCredentials
import gspread
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

class GoogleSheetsService:
    def __init__(self, credentials_file, spreadsheet_id):
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.service = self._authenticate()
        
        # Initialize gspread for reading and writing data
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(creds)
        self.sheet1 = client.open_by_key(spreadsheet_id).sheet1  # First sheet for registered participants
        self.sheet2 = client.open_by_key(spreadsheet_id).worksheet('Attendees')  # Second sheet for attendance

    def _authenticate(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(self.credentials_file, scopes=scopes)
        return build('sheets', 'v4', credentials=creds)

    def get_registered_participants(self):
        return self.sheet1.get_all_records()

    def append_attendee(self, attendee_data):
        self.sheet2.append_row(attendee_data)

    def fetch_attendance_sheet(self):
        return self.sheet2.get_all_records()
