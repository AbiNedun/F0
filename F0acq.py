# F0acq.py

# Knowledge is a weapon and I intend to be formidably armed - Terry Goodkind (Author)

import fastf1 as ff1
import pandas as pd
import matplotlib.pyplot as plt


# Enabling cache for FastF1
ff1.Cache.enable_cache('data/racedat')

def availsessions(year=None):
   
    while True:

        # Attempts from a previous concept 

        try:
            if year is None:
                yearinput = input("Enter the season year (2018 - 2024): ")
                if not (yearinput.isdigit() and 2018 <= int(yearinput) <= 2024):
                    print("Hmm..Sorry that was an invlaid input, please enter a valid year between 2018 and 2024..!")
                    continue
                year = int(yearinput)
            else:
                if not (2018 <= year <= 2024):
                    print("Hmm..Sorry that was an invlaid input, please enter a valid year between 2018 and 2024..!")
                    return None, {}

            schedule = ff1.get_event_schedule(year)
            races = schedule[schedule['Session1Date'].notna()]
            sesdict = {} # DO NOT DELETE THIS

            for _, row in races.iterrows():
                gpn = row['EventName']
                is_sprint = row['EventFormat'] == 'sprint'

                if is_sprint:
                    sessions = ['FP1', 'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race']
                else:
                    sessions = ['FP1', 'FP2', 'FP3', 'Qualifying', 'Race']

                # Remove sessions that don't have a date
                sessions = [s for s in sessions if pd.notna(row[f'Session{sessions.index(s)+1}Date'])]
                sesdict[gpn] = sessions

            # Thankfully somone on the forum figured this out 
            print(f"\nAvailable sessions for {year}:")
            for gp, session_list in sesdict.items():
                print(f"{gp}: {', '.join(session_list)}")

            return year, sesdict
        
        # See the more error messages I wrote, the more I knew my code was wrong 
        except ValueError:
            print("Hmm..that was an invalid year, please enter a valid year.!")
            return None, {}
        except Exception as e:
            print(f"Hmm..Sorry there has been an error fetching the session list: {e}")
            return None, {}

def loadrdata(year, prix, session):
   
    try:
        # Mapping 'Sprint Qualifying' to 'Sprint' for comaptibility 
        fastf1_session = 'Sprint' if session == 'Sprint Qualifying' else session
        
        sesdata = ff1.get_session(year, prix, fastf1_session)
        sesdata.load()

        print(f"Data loaded for {prix} {session} in {year}.")

        if session in ['Race', 'Qualifying', 'Sprint', 'Sprint Qualifying']:
            datacols = {'Position', 'Driver', 'TeamName'}

            if datacols.issubset(sesdata.results.columns):
                grid = sesdata.results[['Position', 'Driver', 'TeamName']]
                order_type = "Starting" if session == 'Race' else "Final"
                print(f"\n{order_type} Grid Order:")
                print(grid.to_string(index=False))

            # This is was made for the errors I faced during the FP sessions.! 
            else:
                print("Hmm..Sorry grid data is unavailable for this session..!")
        else:
            print(f"Hmm..Sorry no grid order is available for {session} sessions.")

        return sesdata

    except Exception as e:
        print(f"Error loading session data: {e}")
        return None



def get_track_layout(sessiondata):
    
    # Fetch the track layout, including sector boundaries and start/finish line coordinates.
    
    try:
        track_layout = sessiondata.get_track_location()
        sectors = track_layout['sectors']
        start_finish = track_layout['start_finish']

    except AttributeError:
        # Fallback coordinates, sometimes the API acts funny 
        sectors = [(0, 0), (500, 100), (1000, 500), (1500, 1000)] 
        start_finish = (0, 0)

    return {"sectors": sectors, "start_finish": start_finish}


def get_driver_telemetry(sessiondata):
    
    # Retrieve telemetry data for all drivers in the session.
    
    driver_telemetry = {} # DO NOT DELETE 

    for lap in sessiondata.laps.iterlaps():
        driver = lap[1]['DriverNumber']
        telemetry = lap[1].get_telemetry()
        telemetry_data = telemetry[['X', 'Y', 'Speed', 'Time']]
        
        if driver not in driver_telemetry:
            driver_telemetry[driver] = telemetry_data
        else:
            driver_telemetry[driver] = pd.concat([driver_telemetry[driver], telemetry_data])
    
    return driver_telemetry


def prepare_simulation_data(sessiondata):
    
    # Organize telemetry and timing data for simulation playback.
    
    all_data = []

    for lap in sessiondata.laps.iterlaps():
        telemetry = lap[1].get_telemetry()
        telemetry['Driver'] = lap[1]['DriverNumber']
        all_data.append(telemetry)

    # Combine all telemetry data and sort by timestamp
    simulation_data = pd.concat(all_data).sort_values(by='Time').reset_index(drop=True)
    
    return simulation_data


def filter_session_type(sessiondata, session_type):
    """
    Filter session data based on the type (qualifying, race, sprint).
    """
    if session_type.lower() not in ["qualifying", "race", "sprint"]:
        raise ValueError("Invalid session type provided.")

    # Filter laps based on session type
    if session_type.lower() == "qualifying":
        filtered_laps = sessiondata.laps.pick_quickest()
    elif session_type.lower() in ["race", "sprint"]:
        filtered_laps = sessiondata.laps  # Use all laps for race or sprint
    else:
        filtered_laps = pd.DataFrame()  # Fallback if no match

    return filtered_laps

def visualize_track(year, event, session_type):
    
    import matplotlib.pyplot as plt
    import numpy as np
    import fastf1

    # Load the session data
    session = fastf1.get_session(year, event, session_type)
    session.load()

    lap = session.laps.pick_fastest()
    pos = lap.get_pos_data()

    circuit_info = session.get_circuit_info()

    # Need to rotate map 
    def rotate(xy, *, angle):
        rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                            [-np.sin(angle), np.cos(angle)]])
        return np.matmul(xy, rot_mat)

    # Get the track data
    track = pos.loc[:, ('X', 'Y')].to_numpy()
    track_angle = circuit_info.rotation / 180 * np.pi
    rotated_track = rotate(track, angle=track_angle)

     # Close the previous plot if one exists
    plt.close('all')

    # Create a new figure for the track
    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot the track
    ax.plot(rotated_track[:, 0], rotated_track[:, 1], color='lightblue', linewidth=2)

    # Plot the start and finsh markers 
    ax.scatter(rotated_track[0, 0], rotated_track[0, 1], color='green', s=150, label='Start Line', edgecolor='lightblue', linewidth=1)
    ax.scatter(rotated_track[-1, 0], rotated_track[-1, 1], color='red', s=150, label='Finish Line', edgecolor='lightblue', linewidth=1)

    # Plot corners
    offset_vector = [500, 0]
    for _, corner in circuit_info.corners.iterrows():
        # Corner text
        txt = f"{corner['Number']}{corner['Letter']}"
        offset_angle = corner['Angle'] / 180 * np.pi
        offset_x, offset_y = rotate(offset_vector, angle=offset_angle)
        text_x = corner['X'] + offset_x
        text_y = corner['Y'] + offset_y
        text_x, text_y = rotate([text_x, text_y], angle=track_angle)
        track_x, track_y = rotate([corner['X'], corner['Y']], angle=track_angle)

        # Corner markers
        ax.scatter(track_x, track_y, color='grey', s=100, label='Corner' if 'Corner' not in ax.get_legend_handles_labels()[1] else "")
        ax.text(text_x, text_y, txt, va='center_baseline', ha='center', size='large', color='black')

    # Finalize plot
    ax.set_title(f"Track Map for {event}, {year} - {session_type}")
    ax.legend(loc='upper right')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('equal')

    return fig

# Test the functions
if __name__ == "__main__":
    year, sessions_dict = availsessions()

    # Result of the previous idea
    while True:
        prix = input("\nEnter the name of the Grand Prix: ")
        if prix in sessions_dict:
            break
        else:
            print(f"Hmm.. the {prix} was not found. Could you enter a Grand Prix name from the list above ?")

    while True:
        session = input("Enter the session type: ")
        if session in sessions_dict[prix]:
            break
        else:
            print(f"Hmm..{session} is not valid for {prix}. Could you select from: {', '.join(sessions_dict[prix])}")

    sesdat = loadrdata(year, prix, session)
    if sesdat:
        print("Session data successfully loaded!")