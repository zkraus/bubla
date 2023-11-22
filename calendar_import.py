import csv
import logging
import pprint
import datetime
from collections import namedtuple, OrderedDict

import tabulate

from google_calendar import Calendar
from utils import config, logger_settings
from googleapiclient.discovery import build

logging.root.setLevel(logging.NOTSET)
logger_settings.config_console_logger(level=logging.NOTSET)
log = logging.getLogger(__name__)

log.info("asdf")
CSV_FILENAME = 'data/DiRT Rally 2.0 planner - 23Q4csv.csv'

rally_event = namedtuple('RallyEvent', 'event start end location distance stages')
stage_event = namedtuple('StageEvent', 'ss stage length condition service')


def load_csv(filename):
    with open(filename) as csvfile:
        csvdata = csv.reader(csvfile, delimiter=',')
        return list(csvdata)


def compile_rally_data_from_csv(csvdata):
    rally_data = OrderedDict()
    csv_iterator = iter(csvdata)
    next(csv_iterator)  # skip header
    for line in csv_iterator:
        line_rally = rally_event(line[0], line[1], line[2], line[3], line[4], [])
        line_stage = stage_event(line[5], line[6], line[7], line[8], line[9])

        rally_number = line_rally.event

        if rally_number not in rally_data:
            rally_data[rally_number] = line_rally

        line_rally = rally_data[rally_number]

        if line_stage.stage:
            line_rally.stages.append(line_stage)
    return rally_data


def prepare_calendar_event(line_rally_event):
    event = Calendar.get_event_template(
        f"{line_rally_event.event} {line_rally_event.location}",
        f"Total distance {line_rally_event.distance} over {len(line_rally_event.stages)} stage(s)"
        f"\n{format_stage_text(line_rally_event.stages)}",
        line_rally_event.start,
        line_rally_event.end
    )
    return event


def format_stage_text(rally_stages: [stage_event]):
    tmp_list = [list(item) for item in rally_stages]
    text = tabulate.tabulate(tmp_list)
    return text


def create_events(rally_data):
    calendar = Calendar(config.CALENDAR_ID, config.CALENDAR_SECRET_FILENAME, config.CALENDAR_TOKEN_FILENAME)
    for line in rally_data.values():
        event = prepare_calendar_event(line)
        if not calendar.event_exists(line.start, line.end):
            calendar.create_event(event)

csvdata = load_csv(CSV_FILENAME)
rally_data = compile_rally_data_from_csv(csvdata)
create_events(rally_data)
