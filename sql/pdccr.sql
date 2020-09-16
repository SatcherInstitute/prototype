# Create query scope persistent PDCCR table with constant UUID.
# Table is joined with BQ PDP Census Counties table, joined by FIPS Code.
CREATE temp table cdc_pdccr_uuid_base AS(
  SELECT
    generate_uuid() AS uuid,
    geo.county_geom AS geo_county_geom,
    geo.lsad_name AS geo_lsad_name,
    LPAD(CAST(fips_code AS STRING), 5, "0") AS fips,
    cdc_pdccr.*
  FROM
    `prototype_tf_main_ingest.cdc_pdccr` cdc_pdccr
  JOIN
    `bigquery-public-data.geo_us_boundaries.counties` geo
  ON
    LPAD(CAST(fips_code AS STRING), 5, "0") = geo.county_fips_code);

# Create intermediary table that joins with the Urgent Care Facility data,
# joined by FIPS Code, and creates REPEATED column with urgent care facilities
# that match the FIPS Code.
WITH
cdc_pdccr_urgent_care AS (
  SELECT
    cdc_pdccr_uuid_base.uuid,
    ARRAY_AGG(
      STRUCT( ucf.id,
        ucf.name,
        st_geogpoint(ucf.x_26, ucf.y_27) as geog_pt,
        ucf.address,
        ucf.address2,
        ucf.city,
        ucf.state,
        ucf.zip,
        ucf.zipp4,
        ucf.county,
        ucf.fips,
        ucf.directions) 
      IGNORE NULLS ) AS ucf_ids
  FROM
    cdc_pdccr_uuid_base
  LEFT OUTER JOIN
    `prototype_tf_main_ingest.ucf` ucf
  ON
    cdc_pdccr_uuid_base.fips = CAST(ucf.fips AS string)
  GROUP BY
    cdc_pdccr_uuid_base.uuid )

# Join back with original PDCCR table to get all the remaining columns,
# and count the number of UCF locations for each row.
SELECT
  cdc_pdccr_uuid_base.*,
  if(cdc_pdccr_urgent_care.ucf_ids[OFFSET(0)].name is null, 0, ARRAY_LENGTH(cdc_pdccr_urgent_care.ucf_ids)) as ucf_count,
  cdc_pdccr_urgent_care.ucf_ids
FROM
  cdc_pdccr_uuid_base,
  cdc_pdccr_urgent_care
WHERE
  cdc_pdccr_uuid_base.uuid = cdc_pdccr_urgent_care.uuid