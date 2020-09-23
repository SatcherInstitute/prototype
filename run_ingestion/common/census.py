from .di_url_file_to_gcs import url_file_to_gcs


def get_household_income_columns():
  """Returns column names of SAIPE fields and their descriptions."""
  return {
    'COUNTY': 'County FIPS Code',
    'GEOCAT': 'Summary Level',
    'GEOID': 'State+County FIPS Code',
    'SAEMHI_LB90': 'Median Household Income Lower Bound for 90% Confidence Interval',
    'SAEMHI_MOE': 'Median Household Income Margin of Error',
    'SAEMHI_PT': 'Median Household Income Estimate',
    'SAEMHI_UB90': 'Median Household Income Upper Bound for 90% Confidence Interval',
    'SAEPOVALL_LB90': 'All ages in Poverty, Count Lower Bound for 90% Confidence Interval',
    'SAEPOVALL_MOE': 'All ages in Poverty, Count Margin of Error',
    'SAEPOVALL_PT': 'All ages in Poverty, Count Estimate',
    'SAEPOVALL_UB90': 'All ages in Poverty, Count Upper Bound for 90% Confidence Interval',
    'SAEPOVRTALL_LB90': 'All ages in Poverty, Rate Lower Bound for 90% Confidence Interval',
    'SAEPOVRTALL_MOE': 'All ages in Poverty, Rate Margin of Error',
    'SAEPOVRTALL_PT': 'All ages in Poverty, Rate Estimate',
    'SAEPOVRTALL_UB90': 'All ages in Poverty, Rate Upper Bound for 90% Confidence Interval',
    'SAEPOVU_ALL': 'All Ages in Poverty Universe',
    'STABREV': 'Two-letter State Postal abbreviation',
    'STATE': 'FIPS State Code',
    'YEAR': 'Estimate Year',
  }


def upload_household_income(url, gcs_bucket, filename):
  """Uploads household income data from SAIPE to GCS bucket for all available years."""
  year_range = {1989, 1993, *range(1995, 2019)}
  for year in year_range:
    url_params = {'get': ','.join(get_household_income_columns().keys()),
                  'for': 'county:*',
                  'in': 'state:*',
                  'time': year}
    url_file_to_gcs(url, url_params, gcs_bucket, '{}_{}.csv'.format(filename, year))


def upload_state_names(url, gcs_bucket, filename):
  """Uploads state names and FIPS codes from census to GCS bucket."""
  url_params = {'get': 'NAME', 'for': 'state:*'}
  url_file_to_gcs(url, url_params, gcs_bucket, filename)
