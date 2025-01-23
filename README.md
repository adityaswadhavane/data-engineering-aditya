# data-engineering-aditya
Homework and Project Repo for Data Engineering zoomcamp

Question 1. 
1. Understanding docker first run   
    Answer - `docker run -it --entrypoint bash python:3.12.8`

2. What's the version of pip in the image?  
    Answer - `pip --version`
            pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)

Question 2. Understanding Docker networking and docker-compose
Answer - 
    hostname - localhost
    port (pgadmin should use to connect to the postgres) - localhost:5432

Question 3. Trip Segmentation Count
During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, respectively, happened:
Up to 1 mile
In between 1 (exclusive) and 3 miles (inclusive),
In between 3 (exclusive) and 7 miles (inclusive),
In between 7 (exclusive) and 10 miles (inclusive),
Over 10 miles

### SQL Query
```
with create_bucket as (
select 
	*,
	case when trip_distance<=1 then '1. Up to 1 mile'
		when trip_distance>1 and  trip_distance<=3 then '2. 1 to 3 mile' 
		when trip_distance>3 and  trip_distance<=7 then '3. 3 to 7 mile' 
		when trip_distance>7 and  trip_distance<=10 then '4. 7 to 10 mile' 
		when trip_distance>10 then  '5. Over 10 miles'
	else '6. No Record' end as trip_dist_bucket,
	TO_CHAR(lpep_dropoff_datetime::TIMESTAMP,'YYYY_MM') as year_month_col

from ny_taxi_yellow
where
	lpep_dropoff_datetime::DATE >= '2019-10-01'
	and lpep_dropoff_datetime::DATE < '2019-11-01'
)

select 
	year_month_col,
	trip_dist_bucket,
	count(*) as no_of_trips,
from create_bucket
group by year_month_col,trip_dist_bucket

```
Answer - 104,802; 198,924; 109,603; 27,678; 35,189

"2019_10"	"1. Up to 1 mile"	104802	1	-6.93
"2019_10"	"2. 1 to 3 mile"	198924	3	1.01
"2019_10"	"3. 3 to 7 mile"	109603	7	3.01
"2019_10"	"4. 7 to 10 mile"	27678	10	7.01
"2019_10"	"5. Over 10 miles"	35189	95.78	10.01


Question 4. Longest trip for each day
Which was the pick up day with the longest trip distance? Use the pick up time for your calculations.

Answer - 
2019-10-31

```
select 
	ny_taxi_yellow.lpep_pickup_datetime::DATE 
from ny_taxi_yellow
	where trip_distance =( select max(trip_distance) from ny_taxi_yellow)

-------------- OR ---------- 

select
	ny_taxi_yellow.lpep_pickup_datetime::DATE,
	max(trip_distance) as max_trip_distance
from ny_taxi_yellow
group by ny_taxi_yellow.lpep_pickup_datetime::DATE 
order by max_trip_distance desc
limit 1
```


Question 5. Three biggest pickup zones
Which were the top pickup locations with over 13,000 in total_amount (across all trips) for 2019-10-18?

Consider only lpep_pickup_datetime when filtering by date.

-- Question 5. Three biggest pickup zones
-- Which were the top pickup locations with over 13,000 in total_amount (across all trips) for 2019-10-18?
-- Consider only lpep_pickup_datetime when filtering by date.

Answer - East Harlem North, East Harlem South, Morningside Heights

```

select 
	zones."Zone",
	sum(taxis."total_amount") as tt_amt
from ny_taxi_yellow as taxis
inner join ny_taxi_zones as zones
on taxis."PULocationID" = zones."LocationID"
where lpep_pickup_datetime::DATE = '2019-10-18'
group by zones."Zone"
order by tt_amt desc
limit 3
```
"East Harlem North"	37373.359999999666
"East Harlem South"	33594.51999999975
"Morningside Heights"	26059.57999999993

Question 6. Largest tip
For the passengers picked up in October 2019 in the zone named "East Harlem North" which was the drop off zone that had the largest tip?
Answer - JFK Airport

```select 
	zones_drop."Zone",
	max(taxis.tip_amount) as max_tip
from ny_taxi_yellow as taxis
inner join ny_taxi_zones as zones_pick
on taxis."PULocationID" = zones_pick."LocationID"
inner join ny_taxi_zones as zones_drop
on taxis."DOLocationID" = zones_drop."LocationID"
where EXTRACT(year from taxis.lpep_pickup_datetime::DATE) = 2019 
and  EXTRACT(MONTH from taxis.lpep_pickup_datetime::DATE) = 10
and zones_pick."Zone" = 'East Harlem North'
group by zones_drop."Zone"
order by max_tip desc
limit 2```

"JFK Airport"	87.3
"Yorkville West"	80.88


### Creating Flow Commands
1. docker build command - Running Postgres Service
```
    docker run -it \
        -e POSTGRES_USER="root"\
        -e POSTGRES_PASSWORD="root"\
        -e POSTGRES_DB="ny_taxi_homework"\
        -v ny_taxi_postgres:/var/lib/postgresql/data\
        -p 5432:5432\
        --network=pg-net\
        --name pg-database_new\
        postgres:13
```

2. Docker Agadmin Image
```
    docker run -it\
        -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
        -e PGADMIN_DEFAULT_PASSWORD="root" \
        -p 8080:80 \
        --network=pg-net\
        --name pg-admin-new\
        dpage/pgadmin4
```

3. Run Docker Compose
`docker compose up`

4. Docker Build 
`docker build -t ingest:etl .`

5. Docker run Container
`
    docker run -it --network=pg-net\
    ingest:etl\
        --user=root\
        --password=root\
        --host=pg-database_new\
        --port=5432\
        --db=ny_taxi_homework\
        --table=ny_taxi_yellow\
        --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz\
        --file_name=output.csv

`

4. Running for Zones Data
```
docker run -it --network=pg-net\
    ingest:v1\
        --user=root\
        --password=root\
        --host=pg-database_new\
        --port=5432\
        --db=ny_taxi_homework\
        --table=ny_taxi_zones\
        --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv\
        --file_name=output.csv
```