
# ---------- Google Calendar Setup ----------

# class SprintRequest(BaseModel):
#     name: str
#     email: EmailStr
#     company: str | None = None
#     role: str | None = None
#     scheduled_at: datetime

# SprintRequest.model_rebuild()

# from google.oauth2 import service_account
# from googleapiclient.discovery import build



# SCOPES = ['https://www.googleapis.com/auth/calendar']
# SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "bookadiscoverysprint.json")
# CALENDAR_ID = ""

# credentials = service_account.Credentials.from_service_account_file(
#     SERVICE_ACCOUNT_FILE, scopes=SCOPES
# )

# service = build('calendar', 'v3', credentials=credentials)

# from uuid import uuid4



# def create_google_meet_event(name: str, email: str, start_time: datetime) -> dict:
#     """
#     Creates a Google Calendar event with a Meet link.
    
#     Note: Service accounts cannot send invitations directly.
#     You must send the Meet link to attendees using your own email service.
    
#     Returns: dict with 'meet_link', 'event_link', and 'event_id'
#     """
#     end_time = start_time + timedelta(hours=1)

#     event = {
#         "summary": f"Discovery Sprint with {name}",
#         "description": f"Discovery Sprint with {name} ({email})",
#         "start": {
#             "dateTime": start_time.isoformat(),
#             "timeZone": "Asia/Kolkata",
#         },
#         "end": {
#             "dateTime": end_time.isoformat(),
#             "timeZone": "Asia/Kolkata",
#         },
#         # DO NOT include "attendees" - service accounts can't invite without Domain-Wide Delegation
#         "conferenceData": {
#             "createRequest": {
#                 "conferenceSolutionKey": {
#                     "type": "hangoutsMeet"
#                 },
#                 "requestId": f"meet-{uuid4()}"  # Unique ID for each request
#             }
#         },
#         "guestsCanModify": False,
#         "guestsCanInviteOthers": False,
#         "guestsCanSeeOtherGuests": False
#     }

#     try:
#         # First, try to create with Google Meet
#         created_event = (
#             service.events()
#             .insert(
#                 calendarId=CALENDAR_ID,
#                 body=event,
#                 conferenceDataVersion=1  # Required for Meet links
#                 # DO NOT use sendUpdates with service accounts
#             )
#             .execute()
#         )

#         # Check if Meet link was created
#         if "conferenceData" in created_event and "entryPoints" in created_event["conferenceData"]:
#             meet_link = created_event["conferenceData"]["entryPoints"][0]["uri"]
#             print(f"✓ Event created: {created_event.get('htmlLink')}")
#             print(f"✓ Meet link: {meet_link}")
            
#             return {
#                 'meet_link': meet_link,
#                 'event_link': created_event.get('htmlLink'),
#                 'event_id': created_event.get('id'),
#                 'status': 'success'
#             }
#         else:
#             # Fallback: return the event link if Meet wasn't created
#             event_link = created_event.get('htmlLink', 'No link available')
#             print(f"⚠ Event created but Meet link not generated: {event_link}")
#             return {
#                 'meet_link': None,
#                 'event_link': event_link,
#                 'event_id': created_event.get('id'),
#                 'status': 'no_meet_link'
#             }
            
#     except Exception as e:
#         error_message = str(e)
        
#         # If Google Meet is not available, create event without conferenceData
#         if "Invalid conference type" in error_message or "conference" in error_message.lower():
#             print(f"⚠ Google Meet not available for this calendar. Creating event without Meet link...")
            
#             # Remove conferenceData and try again
#             event_without_meet = {
#                 "summary": f"Discovery Sprint with {name}",
#                 "description": f"Discovery Sprint with {name} ({email})\n\nNote: Please use an alternative meeting link.",
#                 "start": {
#                     "dateTime": start_time.isoformat(),
#                     "timeZone": "Asia/Kolkata",
#                 },
#                 "end": {
#                     "dateTime": end_time.isoformat(),
#                     "timeZone": "Asia/Kolkata",
#                 },
#             }
            
#             try:
#                 created_event = (
#                     service.events()
#                     .insert(
#                         calendarId=CALENDAR_ID,
#                         body=event_without_meet
#                     )
#                     .execute()
#                 )
                
#                 print(f"✓ Event created without Meet link: {created_event.get('htmlLink')}")
#                 print(f"⚠ You'll need to add a meeting link manually or use a different service")
                
#                 return {
#                     'meet_link': None,
#                     'event_link': created_event.get('htmlLink'),
#                     'event_id': created_event.get('id'),
#                     'status': 'no_meet_support',
#                     'error': 'Google Meet not available for this calendar'
#                 }
#             except Exception as inner_e:
#                 print(f"✗ Error creating event: {str(inner_e)}")
#                 raise inner_e
#         else:
#             print(f"✗ Error creating event: {error_message}")
#             raise e




# @app.post("/schedule-sprint")
# def schedule_sprint(sprint: SprintRequest):
#   meet_link = create_google_meet_event(sprint.name, sprint.email, sprint.scheduled_at)
#   return {"message": meet_link}