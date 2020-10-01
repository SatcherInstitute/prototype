from .di_url_file_to_gcs import try_urls_to_download_file_to_gcs
import logging
import os
from google.cloud import storage
import google.cloud.exceptions
import requests

STATE_NAMES = [
"Alabama",
"Alaska",
"Arizona",
"Arkansas",
"California",
"Colorado",
"Connecticut",
"Delaware",
"Florida",
"Georgia",
"Hawaii",
"Idaho",
"Illinois",
"Indiana",
"Iowa",
"Kansas",
"Kentucky",
"Louisiana",
"Maine",
"Maryland",
"Massachusetts",
"Michigan",
"Minnesota",
"Mississippi",
"Missouri",
"Montana",
"Nebraska",
"Nevada",
"New Hampshire",
"New Jersey",
"New Mexico",
"New York",
"North Carolina",
"North Dakota",
"Ohio",
"Oklahoma",
"Oregon",
"Pennsylvania",
"Rhode Island",
"South Carolina",
"South Dakota",
"Tennessee",
"Texas",
"Utah",
"Vermont",
"Virginia",
"Washington",
"West Virginia",
"Wisconsin",
"Wyoming"]

FILEPATH = '{}-{}.xlsx'
URL1 = 'https://www.countyhealthrankings.org/sites/default/files/media/document/2020 County Health Rankings {} Data - v1_0.xlsx'
URL2 = 'https://www.countyhealthrankings.org/sites/default/files/media/document/2020 County Health Rankings {} Data - v1.xlsx'

def upload_primary_care_access(gcs_bucket, fileprefix):
  """Uploads one file containing primary care access info for each state."""

  for state in STATE_NAMES:
    try_urls_to_download_file_to_gcs([URL1.format(state), URL2.format(state)], {}, gcs_bucket, FILEPATH.format(fileprefix, state))