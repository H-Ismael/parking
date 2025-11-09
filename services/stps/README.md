## STPS (Spatio-Temporal Prior Service)

### Interaction summary:

    - nearby-spots-api → serves immediate, user-reported data

    - stps → serves predicted congestion/availability baseline

    - Both run independently and compose results in the final response.

    | Service                                  | Purpose                                                 | Tech                           | Data Store                      | Status          |
| ---------------------------------------- | ------------------------------------------------------- | ------------------------------ | ------------------------------- | --------------- |
| **nearby-spots-api**                     | Collect & query live reported spots                     | FastAPI + SQLAlchemy + PostGIS | `parking_spots` table           | ✅ Already built |
| **stps (Spatio-Temporal Prior Service)** | Predict congestion & availability from travel-time data | FastAPI + H3 + DuckDB + Pandas | `heatmap_tiles`, `hex_features` | 🆕 To build     |
| **signals-worker (later)**               | Listen for user events → update STPS prior              | Background worker              | same DB + message queue         | ⏳ Future        |
| **dashboard**                            | Visual QA of heatmaps                                   | Streamlit/Leaflet              | reads from STPS                 | optional        |

### Overall flow

- Offline (batch):

    - Extract tables from the Excel (Casablanca dataset)

    - Build TTI → CI → baseline per hex/time_bin

    - Store in stps/data/heatmap_tiles.db

- Online (runtime):

    - STPS exposes /cell or /tiles

    - nearby-spots-api calls STPS with (lat, lon, time) to get congestion/availability priors

    - Fuse that with live spots → rank & return best spots

- Adaptive (later):

    - When users report spots, a sidecar worker updates priors in STPS (Kalman/EWMA).

### From ToDo list : 

- Add user sessions - tables , rank => beside gamification (credit system) it will serve as an additional signal source.
	- Gamification : credit system to retain and reward best users. 
	- Quality Signal/Data source : 
		- If number n_users of app users are within user_radius e.g 100 meters then set threshold to be used for final score update of the cell(user_app_density_score = user_r_coverage ).(take into account special driver categ : "dev" , "trusted sources" , "regulars"(ranked by credit sys). 
		- Capture business params to update regularly the new "congestion" scores (cold map ) .
		
- displace TTL params from env to a table 
	- for busy geo / zones so that it can be updated but with slow freq
	- for time zone same slow frequency but account for offdays / events / seasonal events
		- Potential sources : 
					- 2023 study for Casa
					- https://data.humdata.org
					- Passive feedback from users for adaptive heatmap as well as later analytics.(mid to high trusted source).
					- Addional datacollection from waze api or brokers
					- holidays calendars (per cities) as tables.