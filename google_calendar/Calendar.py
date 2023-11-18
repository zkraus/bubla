import datetime
import os.path
import pprint
import cachetools
from collections import namedtuple

from utils import config

import markdownify
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file calendar_token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

Event = namedtuple('Event', ['summary', 'start', 'end', 'active', 'upcoming', 'remains', 'starts_in', 'description'])


class Calendar:

    def __init__(self, calendar_id, credentials_filename, token_filename):
        self.calendar_id = calendar_id
        self.credentials_filename = credentials_filename
        self.token_filename = token_filename

    def authenticate(self):
        creds = None
        # The file calendar_token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_filename):
            creds = Credentials.from_authorized_user_file(self.token_filename, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_filename, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_filename, 'w') as token:
                token.write(creds.to_json())
        return creds

    @cachetools.cached(cachetools.TTLCache(100, 600))
    def get_events(self, event_limit=5):
        creds = self.authenticate()

        try:
            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            # print('Getting the upcoming 10 events')
            events_result = service.events().list(calendarId=self.calendar_id, timeMin=now,
                                                  maxResults=event_limit, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])
            if not events:
                print('No upcoming events found.')
                return

            results = []
            # Prints the start and name of the next 10 events
            for event in events:
                # pprint.pprint(event)
                start = datetime.datetime.strptime(event['start'].get('date'), '%Y-%m-%d')
                end = datetime.datetime.strptime(event['end'].get('date'), '%Y-%m-%d')
                now = datetime.datetime.utcnow()
                active = start < now < end
                upcoming = now < start
                remains = end - now
                starts_in = start - now
                results.append(Event(
                    summary=event.get('summary'),
                    start=start,
                    end=end,
                    active=active,
                    upcoming=upcoming,
                    remains=remains,
                    starts_in=starts_in,
                    description=event.get('description'),
                ))
            return results

        except HttpError as error:
            print('An error occurred: %s' % error)
            raise error

    def get_events_current(self):
        events = self.get_events()
        return [event for event in events if event.active]

    def get_events_upcoming(self):
        events = self.get_events()
        return [event for event in events if event.upcoming]

    def get_events_end_soon(self):
        events = self.get_events_current()
        return [event for event in events if event.remains.days <= config.DAYS_END_SOON]

    def get_events_next(self):
        events = self.get_events_upcoming()
        return [event for event in events if event.starts_in.days <= config.DAYS_START_SOON]

    def format_time_field(self, time_field):
        result = ''
        if time_field.days > 0:
            result = f"{time_field.days}d"
        else:
            result = f"{time_field.seconds / 3600}h"
        return result

    def get_semaphore(self, event):
        semaphore = '🔴'
        if event.active:
            semaphore = '🟢'
        if event.upcoming and event.starts_in.days <= config.DAYS_START_SOON:
            semaphore = '🟡'
        return semaphore

    def get_event_timing(self, event):
        result = ''
        if event.active:
            result = f"remaining: {self.format_time_field(event.remains)} @{event.end.date()}"
        if event.upcoming:
            result = f"starts in: {self.format_time_field(event.starts_in)} @{event.start.date()}"
        return result

    def format_events(self, events):
        result = []
        for event in events:
            semaphore = self.get_semaphore(event)
            timing = self.get_event_timing(event)
            result.append(f"{semaphore}**{event.summary}** {timing}")
            if event.description:
                description = [f"> {line}" for line in event.description.splitlines()]
                result.append("\n".join(description))
        return '\n'.join(result)
