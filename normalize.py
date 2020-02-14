#!/usr/bin/env python3

import csv
import datetime
import fileinput
import sys


# Setup datetime timezones
# pretending dst doesn't exist since, acknowledging its existence would require pytz
pacific_offset = datetime.timedelta(hours=-8)
eastern_offset = datetime.timedelta(hours=-5)
pacific_tz = datetime.timezone(pacific_offset, 'Pacific Time')
eastern_tz = datetime.timezone(eastern_offset, 'Eastern Time')


def clean_address(address):
    if ',' in address:
        address = '"{address}"'.format(address=address)
    return address


def print_error(error):
    print('WARN: row will be omitted due to invalid input format: {e}'.format(e=error), file=sys.stderr)


# Convert timestamps to RFC3339 format: 2002-10-02T10:00:00-05:00, 2002-10-02T15:00:00Z, 2002-10-02T15:00:00.05Z
# US/Pacific time; please convert it to US/Eastern
# The sample data we provide will contain all date and time format variants you will need to handle.
# Possible input formats: M/D/YY HH:MM:SS AM/PM, MM/DD/YY HH:MM:SS AM/PM
def format_timestamp(timestamp):
    py_timestamp = datetime.datetime.strptime(timestamp, '%m/%d/%y %I:%M:%S %p')
    py_timestamp = py_timestamp.replace(tzinfo=pacific_tz)
    eastern_datetime = py_timestamp.astimezone(eastern_tz)
    return eastern_datetime.isoformat()


# If less than 5 digit zip code, assume 0(s?) as the prefix
def validate_zip(zip_code):
    # validate that it isn't a bunch of letters, needs to be done before adding 0's
    int(zip_code)
    add_zeroes = 5 - len(zip_code)
    if add_zeroes:
        return '0' * add_zeroes + zip_code
    return zip_code


# The FullName column should be converted to uppercase. Asian characters?
def format_full_name(full_name):
    return full_name.upper()


# The FooDuration and BarDuration columns are in HH:MM:SS.MS format (
# where MS is milliseconds); convert to total number of seconds
# expressed in floating point format. No rounding
def convert_duration(duration):
    h, m, s = duration.split(':')
    total_seconds = int(h) * 3600 + int(m) * 60 + float(s)
    return total_seconds


# The TotalDuration column is filled with garbage data. For each row, please
# replace the value of TotalDuration with the sum of FooDuration and BarDuration
def get_total_duration(foo_duration, bar_duration):
    return foo_duration + bar_duration


# map list of strings to cleaner and any additional transformation
def clean_and_normalize_row(row):
    """
    Format according to given specifications. Invalid data will be removed from output and a WARN printed.
    Expected csv column order: Timestamp,Address,ZIP,FullName,FooDuration,BarDuration,TotalDuration,Notes
    Each row's values will map to the following indexes:
    0 - Timestamp
    1 - Address
    2 - Zip
    3 - Full name
    4 - Foo duration
    5 - Bar duration
    6 - total duration
    7 - Notes
    """
    try:
        cleaned_row = []
        cleaned_row.append(format_timestamp(row[0]))
        cleaned_row.append(clean_address(row[1]))
        cleaned_row.append(validate_zip(row[2]))
        cleaned_row.append(format_full_name(row[3]))
        foo_duration = convert_duration(row[4])
        cleaned_row.append(str(foo_duration))
        bar_duration = convert_duration(row[5])
        cleaned_row.append(str(bar_duration))
        total_duration = get_total_duration(foo_duration, bar_duration)
        cleaned_row.append(str(total_duration))
        cleaned_row.append(row[7])
        return cleaned_row
    except ValueError as error:
        print_error(error)


# Read and parse CSV data: prob csv reader/writer
def read_and_clean_file():
    # Read in byte mode in case there are non unicode chars
    all_lines = fileinput.input(mode='rb')
    csv_usable_lines = []
    # Replace all non unicode chars
    for byte_row in all_lines:
        csv_usable_lines.append(byte_row.decode('utf-8', 'replace'))
    csv_rows = csv.reader(csv_usable_lines)
    # Skip parsing header, but send to stdout to show in new file
    header = next(csv_rows)
    header = ','.join(header)
    print(header)
    for row in csv_rows:
        normalized_data = clean_and_normalize_row(row)
        if normalized_data:
            print(','.join(normalized_data))


if __name__ == "__main__":
    read_and_clean_file()

