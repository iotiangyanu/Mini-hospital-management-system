from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def create_event(doctor_email, patient_email, start_time, end_time, doctor_name, patient_name):

    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': f'Appointment with Dr. {doctor_name}',
        'description': f'Appointment with {patient_name}',
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
        'attendees': [
            {'email': doctor_email},
            {'email': patient_email},
        ],
    }

    service.events().insert(calendarId='primary', body=event).execute()