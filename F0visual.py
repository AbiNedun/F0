# F0visual.py
 
# The greatest enemy of progress is the illusion of knowledge - John Young (Astronaut)

# Importing libraries 
import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from tkinter import ttk, messagebox

import fastf1
import pandas as pd

from F0acq import loadrdata,visualize_track


class TelemetryTracker:

    def __init__(self, master):

        # Define tkinter variables
        self.master = master
        self.master.title("F0 Telemetry Tracker")
        
        self.sessionsdict = {}
        
        self.year = tk.StringVar()
        self.grandprix = tk.StringVar()
        self.sessiontype = tk.StringVar()
        
        # Create widgets
        self.createwidgets()
        

    def createwidgets(self):
            
            # Creating the Year Selection dropdown
            tk.Label(self.master, text="Select Year:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.yeardropdown = ttk.Combobox(self.master, textvariable=self.year, values=[str(y) for y in range(2018, 2025)], state="readonly")
            self.yeardropdown.grid(row=0, column=1, padx=5, pady=5,sticky="w")

            # Creating the Fetch Sessions button
            fetchbutton = tk.Button(self.master, text="Fetch Sessions", command=self.fetchsessions)
            fetchbutton.grid(row=0, column=2, padx=5, pady=5,sticky='w')

            # Creating the Grand Prix dropdown
            tk.Label(self.master, text="Grand Prix:").grid(row=1, column=0, padx=5, pady=5,sticky="w")
            self.prixdropdown = ttk.Combobox(self.master, textvariable=self.grandprix, state="readonly")
            self.prixdropdown.grid(row=1, column=1, padx=5, pady=5,sticky="w")
            self.prixdropdown.bind("<<ComboboxSelected>>", self.updatesessdrop)

            # Creating the Session Type dropdown
            tk.Label(self.master, text="Session Type:").grid(row=2, column=0, padx=5, pady=5,sticky="w")
            self.sessdropdown = ttk.Combobox(self.master, textvariable=self.sessiontype, state="readonly")
            self.sessdropdown.grid(row=2, column=1, padx=5, pady=5,sticky="w")

            # Creating the Load Data button
            loadbutton = tk.Button(self.master, text="Load Data", command=self.loaddata)
            loadbutton.grid(row=1, column=2, padx=5, pady=5, sticky="w")

            # Creating the Visualize Track button
            visualize_button = tk.Button(self.master, text="Visualize Track", command=self.visualizetrack)
            visualize_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")
            
            # Creating the text widget for displaying output
            self.output_text = tk.Text(self.master, width=110, height=60)
            self.output_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

            # Creating a frame for track visualization
            self.track_frame = tk.Frame(self.master, width=400, height=200)
            self.track_frame.grid(row=4, column=2, padx=10, pady=10, sticky="nsew")
            self.track_frame.grid_propagate(False)

             
            # Dictionary for regulations: 
            
            self.regulations = {
            "Car Specification":

            """
            F1 Car Specification:

            Dimensions:

            - Maximum width: 200 cm
            - Maximum height: 95 cm
            - No maximum length, but indirectly limited by other rules
            - Maximum wheelbase: 360 cm

            Weight:

            - Minimum weight (car + driver): 798 kg as of 2024

            Safety Features:

            - Safety cell includes cockpit, front impact structure, and fuel cell
            - Driver must be able to enter/exit easily

            Crash Tests:

            - 30 mph (48 km/h) head-on impact test
            - Rear impact test from 30 mph (48 km/h) sled
            - Side impact test with specific force and energy absorption requirements
            - Steering wheel impact test
            - 'Squeeze tests' for cockpit sides, fuel tank, and nosebox

            Power Unit:

            - ICE (Internal Combustion Engine)
            - TC (Turbocharger)
            - MGU-K (Motor Generator Unit-Kinetic)
            - MGU-H (Motor Generator Unit-Heat)
            - ES (Energy Store)
            - CE (Control Electronics)

            Specifications:

            - 1.6-litre V6 turbocharged engines
            - Fuel limit: 110 kg per race 
            - Estimated power output: 750-850 bhp for ICE, 160 bhp from ERS
            - Total power: approximately 1,000 bhp

           
            Usage Limits:

            - Four of each component allowed per season (up to 20 races)
            - Fifth power unit allowed without penalty if more than 20 races
            - Penalties for exceeding allocation: 10-place grid penalty or pit lane start

            """,
            "Tires":

            """
            F1 Tire Regulations:

            Tire Supplier:

            - Pirelli has been the supplier since 2011

            Dry-Weather Tire Compounds:

            - 3 compounds provided at each race
            - Designated as soft, medium, and hard
            - Color-coded bands on sidewalls:
            * Red: Soft
            * Yellow: Medium
            * White: Hard

            Tire Allocation:

            - Drivers select 10 sets of tires per race weekend
            * 13 dry tire sets
            * 4 intermediate tire sets
            * 3 wet tire sets

            Tire Usage Rules:

            - Must use 2 different dry compounds during a race
            - One set of softest tires reserved for Q3
            - Two sets of medium and hard tires kept for race
            - Each tire marked with unique identifier

            Wet Weather Regulations:

            - Wet and intermediate tires only used when track is wet
            - Safety car start in heavy rain requires wet tires

            """,
            "Race Procedure": 

            """
            F1 Race Start Procedure:

            Formation Lap:

            - Also known as parade lap
            - Signaled by green lights
            - No passing allowed
            - Drivers weave to warm up tyres
            - Controlled burnouts performed approaching grid boxes

            Starting Grid Penalties:

            - 10-position penalty for cars unable to start (i.e engine failure)
            - Option to start from pit lane for strategic reasons
            - 5-place grid penalty for gearbox replacement before 5 consecutive events

            Race Start Procedure:

            - 10 red lights in two rows of five
            - Lights illuminate in pairs, left to right, at one-second intervals
            - Lights go out simultaneously after 4-7 seconds
            - Race officially begins when lights go out

            Aborted Start:

            - All red lights come on, then orange lights flash
            - Engines stopped
            - Start procedure resumes from 5-minute point

            Driver Unable to Start:

            - Driver raises hand
            - Marshal waves yellow flag
            - Red and orange lights extinguish
            - Green lights indicate another formation lap
            - No overtaking allowed in additional formation lap

            """,
            "Scoring": 
            """
            F1 Points Scoring System:

            Points Allocation:
            
            - 1st place:  25 points
            - 2nd place:  18 points
            - 3rd place:  15 points
            - 4th place:  12 points
            - 5th place:  10 points
            - 6th place:  8 points
            - 7th place:  6 points
            - 8th place:  4 points
            - 9th place:  2 points
            - 10th place: 1 point
            - Fastest Lap: 1 point 
            - 11th place onwards: No points

            Points Eligibility Conditions:

            - Driver must complete at least 90% of winner's race distance
            - Possible for no points to be awarded if insufficient drivers complete race distance

            Suspended Race Points Allocation:

            - Minimum 2 laps under green flag conditions required
            - 0-25% race distance: Top 5 receive 6-4-3-2-1 points
            - 25-50% race distance: Top 9 receive 13-10-8-6-5-4-3-2-1 points
            - 50-75% race distance: Top 10 receive 19-14-12-9-8-6-5-3-2-1 points
            - Over 75% race distance: Full points awarded
            - Fastest lap point only awarded if over 50% race distance completed

            Championship Determination:

            - Points awarded equally to driver and constructor
            - Champion determined by total points at season end
            - Tiebreaker criteria:
            * Most wins
            * Most second-place finishes
            * Continues down the finishing positions

            """,
            "Flags":
            """
            F1 Racing Flags:

            Yellow Flag:

            - Single yellow: Danger ahead
            * Slow down
            * No overtaking (except in unavoidable circumstances)
            - Double yellow: Great danger
            * Prepare to stop
            * No overtaking
            - With Safety Car board: Safety car deployed
            * Slow down
            * Prepare to leave racing line or stop

            Green Flag:

            - Indicates track is clear
            - Drivers can resume racing speed
            - Overtaking permitted
            - Used during parade lap or start of practice sessions

            Red Flag:

            - Race, practice, or qualifying suspended
            - Drivers must:
            * Not leave pits
            * Proceed cautiously to pit lane
            * Stop in racing order
            - Session may be resumed or abandoned

            Blue Flag:
            
            - Pit lane exit: Warns of approaching cars
            - Practice: Faster car approaching
            - Race: Being lapped
            * Must not impede faster car
            * Penalties for ignoring 3 successive blue flags

            White Flag:

            - Indicates slow-moving vehicle on track
            - Warns of ambulance, tow truck, or retiring car

            Black Flag:

            - Driver disqualified
            - Must return to pit within one lap
            - Accompanied by car number board

            Black and White Chequered Flag:

            - Signals end of race, practice, or qualifying
            - Shown to winner first, then to other finishers

            Black and White Flag:

            - Warning for unsporting behavior
            - Accompanied by car number

            Black Flag with Orange Circle:

            - Mechanical problem endangering driver or others
            - Must return to pit immediately

            Yellow and Red Striped Flag:

            - Warns of slippery track surface
            - Indicates debris or fluid on track
            - Drivers must slow down
            """,
            "Penalties":
            """
            F1 Penalty Types:

            Time Penalty:

            - Most common penalty type
            - 5 or 10 seconds duration
            - Served during next pit stop
            - Mechanics must wait penalty duration before working on car
            - If not served in pit lane, time added to race end

            Drive-Through Penalty:

            - Driver must enter pit lane
            - Drive through at pit lane speed limit
            - Exit without stopping
            - Less severe than stop-go penalty
            - Must be served within 2 laps of notification

            Stop-Go Penalty:

            - Driver must:
            * Enter pit lane
            * Stop for 10 seconds
            * Exit without mechanics working on car
            - Harshest penalty before disqualification
            - Given for serious offences
            - Must be served within 2 laps of notification

            Penalty Serving Exceptions:

            - If Safety Car deployed, penalty service delayed
            - Penalties in last 5 race laps:
            * Drive-through: 20 seconds added
            * Stop-go: 30 seconds added

            Black Flag:

            - Disqualification from race
            - Results do not count toward championship
            - Possible additional race ban
            - Often used for technical irregularities

            Grid Penalty:

            - Applied to next race
            - Can increase based on severity
            - Examples:
            * 5-place penalty moves driver back positions
            * Can be given for engine component quota excess

    
            Common Penalty Reasons:
            - Jumping start
            - Pit lane speeding
            - Causing avoidable accidents
            - Unsportsmanlike conduct
            - Ignoring flags
            - Technical irregularities
            """
            }

            # Creating a text widget for displaying regulation details
            self.regulation_text = tk.Text(self.master, width=110, height=60)
            self.regulation_text.grid(row=4, column=2, padx=10, pady=10, sticky="nsew")

            # Creating a frame for regulation buttons
            self.regulation_frame = tk.Frame(self.master)
            self.regulation_frame.grid(row=5, column=2, columnspan=2, padx=5, pady=5)

            # Creating a display for regulation information
            def show_regulation(regulation_key):
                self.regulation_text.delete(1.0, tk.END)  # Clear the regulation text widget
                regulation_details = self.regulations.get(regulation_key, "No information available.")
                self.regulation_text.insert(tk.END, regulation_details)

            # Arranging regulation buttons in two rows
            regulation_buttons = [
                "Car Specification", "Tires", "Race Procedure",
                "Scoring", "Flags", "Penalties"
            ]

            # Looping the iterations of buttons, incase 6 is not enough 
            for i, reg_name in enumerate(regulation_buttons):
                button = tk.Button(
                    self.regulation_frame, text=reg_name, width=20,
                    command=lambda reg=reg_name: show_regulation(reg)
                )
                button.grid(row=i // 3, column=i % 3, padx=5, pady=5)


    def fetchsessions(self):

        # Fetching the available sessions for the selected year and update dropdowns
        
        # Leftover code from previous attempts 
        try:
            year = int(self.year.get())
            self.popsessdict(year)

            if self.sessionsdict:
                self.prixdropdown['values'] = list(self.sessionsdict.keys())
                self.prixdropdown.current(0)
                self.updatesessdrop()
            else:
                messagebox.showerror("Hmm...theres been an Error...", "There are no sessions available for the selected year..!")
        except ValueError:
            messagebox.showerror("You have inputed an error..!", "Please select a valid year between 2018 and 2024..!")

    def popsessdict(self, year):

        # Populates the session dictionary for each race 

        self.sessionsdict.clear()
        schedule = fastf1.get_event_schedule(year)

        # Making a for loop for the few sprint events that happen during a season
        for _, event in schedule.iterrows():
            gp_name = event['EventName']
            is_sprint = event['EventFormat'] == 'sprint'

            # Sprint weekend format is different than the regular race weekend 
            if is_sprint:
                sessions = ['FP1', 'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race']
            else:
                sessions = ['FP1', 'FP2', 'FP3', 'Qualifying', 'Race']

            # Remove sessions that don't have a date, seems to resolve a lot of issues..!!!
            sessions = [s for s in sessions if pd.notna(event[f'Session{sessions.index(s)+1}Date'])]
            self.sessionsdict[gp_name] = sessions

    # Updates the session dropdown 
    def updatesessdrop(self, *args):
        selprix = self.grandprix.get()
        sessions = self.sessionsdict.get(selprix, [])
        self.sessdropdown['values'] = sessions
        if sessions:
            self.sessdropdown.current(0)

    # Loading the race session data 
    def loaddata(self):
        try:
            year = int(self.year.get())
            grand_prix = self.grandprix.get()
            session = self.sessiontype.get()

            # Loading the regular race weekend 
            if grand_prix and session:
                sessiondata = loadrdata(year, grand_prix, session)
                if sessiondata:
                    self.output_text.delete(1.0, tk.END)
                    self.output_text.insert(tk.END, f"Data for {grand_prix} {session} in {year} loaded successfully!\n\n")
                    
                    # Display session details
                    self.output_text.insert(tk.END, f"Date: {sessiondata.date}\nTrack: {grand_prix}\nSession Type: {session}\n\n")

                    # Results display
                    if session in ["Race", "Qualifying", "Sprint", "Sprint Qualifying"]:
                        self.output_text.insert(tk.END, "Template:\n\n")
                        self.output_text.insert(tk.END, "| Position | Driver Number | Driver | Team | Final Time | Last Lap |\n\n")
                        self.output_text.insert(tk.END, "Results:\n\n")

                        # Showing the attributes of the session data 
                        if hasattr(sessiondata, 'results'):
                            results = sessiondata.results
                            columns_to_display = ['Position', 'DriverNumber', 'BroadcastName', 'TeamName'] # Remember This..! 
                            time_column = 'TotalTime' if 'TotalTime' in results.columns else 'Time' if 'Time' in results.columns else None
                            if time_column:
                                columns_to_display.append(time_column)
                            
                            # In case there is not a last lap time or proper attribute otherwise...error..! 
                            for _, row in results[columns_to_display].iterrows():
                                total_time = row.get(time_column, "+Lap")
                                last_lap_time = "N/A"
                                
                                if hasattr(sessiondata, 'laps') and not sessiondata.laps.empty:
                                    laps = sessiondata.laps.pick_drivers(row['DriverNumber'])
                                    if not laps.empty:
                                        last_lap_time = laps.iloc[-1].LapTime
                                        if isinstance(last_lap_time, pd.Timedelta):
                                            last_lap_time = str(last_lap_time).split("days")[-1].strip()

                                # Taking the "days" out of the timing data 
                                if isinstance(total_time, pd.Timedelta):
                                    total_time = str(total_time).split("days")[-1].strip()

                                row_values = [str(row[col]) for col in columns_to_display if col != time_column]
                                row_values.append(f"Total Time: {total_time}")
                                row_values.append(f"Last Lap: {last_lap_time}")
                                self.output_text.insert(tk.END, " | ".join(row_values) + "\n\n")
                        else:
                            self.output_text.insert(tk.END, "Hmm..Sorry the results are not available..!\n")

                    # Display fastest laps if available (for practice sessions)
                    
                    # Needed to seperate practice sessions (FP1,FP2,FP3), otherwise... error.! 
                    elif session.startswith("FP"):

                        if hasattr(sessiondata, 'laps') and not sessiondata.laps.empty:

                            # Get the fastest lap per driver, really the only way to get grid position 
                            fastest_laps = sessiondata.laps.groupby('DriverNumber').apply(lambda x: x.nsmallest(1, 'LapTime')).reset_index(drop=True)
                            self.output_text.insert(tk.END, "Fastest Laps:\n\n")
                            self.output_text.insert(tk.END, "| Position | Driver Number | Driver | Team | Lap Time |\n\n")
                            
                            # Shoiwng N/A if there was no laptime, 
                            for index, lap in enumerate(fastest_laps.itertuples(), start=1):
                                lap_time = lap.LapTime if hasattr(lap, 'LapTime') else 'N/A' # DO NOT DELETE THIS..! 

                                # Taking the "days" out of the timing data 
                                if isinstance(lap_time, pd.Timedelta):
                                    lap_time = str(lap_time).split("days")[-1].strip() # Someone thought this was funny...
                                
                                # Access the fields directly from the lap object
                                self.output_text.insert(tk.END, f"| {index:<8} | {lap.DriverNumber:<13} | {lap.Driver:<6} | {lap.Team:<4} | {lap_time} |\n")
                        else:
                            self.output_text.insert(tk.END, "Hmm.. Sorry there was no data available..!\n")

                    else:
                        self.output_text.insert(tk.END, "Sorry, there is no specific data format for this session..!\n")

                    # Add general session statistics: Laps and Drivers 
                    if hasattr(sessiondata, 'laps'):
                        self.output_text.insert(tk.END, f"\nTotal Laps: {len(sessiondata.laps)}\n")
                        self.output_text.insert(tk.END, f"Number of Drivers: {len(sessiondata.drivers)}\n") # It would almost be funny to hardcode this...

                # Error messesages during testing        
                else:
                    messagebox.showerror("Hmm..there was an error", "Sorry the session data failed to load.!")
            else:
                messagebox.showwarning("Hmm..there was an error", "Could you please select a Grand Prix and session type ?")

        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Hmm..Sorry there was an error loading the data: {e}\n")
            import traceback
            traceback.print_exc()

    def visualizetrack(self):

        #Opens the track map visualization in a new window

        try:
            year = int(self.year.get())
            event = self.grandprix.get()
            session_type = self.sessiontype.get()

            if not (year and event and session_type):
                tk.messagebox.showwarning("Input Error", "Please select all fields to visualize the track.")
                return

            # Close the previous figure to ensure the new one is displayed properly
            plt.close('all')

            # Generate the track figure
            fig = visualize_track(year, event, session_type)
            if not fig:
                tk.messagebox.showerror("Hmm..there was an error", "Sorry the track could not be properly generated.!")
                return
            
            # Check if track_window exists and destroy it before creating a new one
            if hasattr(self, 'track_window') and self.track_window.winfo_exists():
                self.track_window.destroy()  # Close the previous window

            # Create a new Toplevel window for the track map
            self.track_window = tk.Toplevel(self.master)


            # Embed the matplotlib figure in the new window

            canvas = FigureCanvasTkAgg(fig, master=self.track_window)
            canvas.draw()

            # Pack the canvas into the Toplevel window
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Reminder for when I couldn't get the track visualization working 
        except Exception as e:
            tk.messagebox.showerror("Hmm..theres been an error..!", f"Sorry there was a visualization error..!: {str(e)}")

    def setup_regulation_view():

        #Sets up the regulation view with buttons and a text widget to display details

        # Placeholder dictionary for the regulations, filled in earlier
        regulations = {} # DO NOT DELETE THIS..!!

        def show_regulation(regulation_key):

            #Updates the regulation text widget with the selected regulation's details.
            regulation_text_widget.delete(1.0, tk.END)  # Clears existing text, sometimes there was leftover information
            regulation_text_widget.insert(tk.END, regulations.get(regulation_key, "Hmm..Sorry there was no information"))

        # Create a frame to hold the regulation buttons and text widget
        regulation_frame = tk.Frame(root)

        # I meant to put this up in the create widgets function, but it works just fine here 
        regulation_frame.grid(row=1, column=2, padx=10, pady=10, sticky="n") 

        # Add buttons for each regulation
        # same code as earlier, someone on the GITHUB formum said not doing this was a common error... and it was..!
        for i, regulation in enumerate(regulations.keys()):
            button = tk.Button(
                regulation_frame, text=regulation, width=20,
                command=lambda reg=regulation: show_regulation(reg)
            )
            button.grid(row=i, column=0, padx=5, pady=5)

        # Bogus text widget, here to remind myself of original rows and columns
        regulation_text_widget = tk.Text(root, width=50, height=25, bg="lightgray", fg="black")
        regulation_text_widget.grid(row=1, column=3, padx=10, pady=10)

# Creating the main window and running the application
if __name__ == "__main__":
    root = tk.Tk()
    app = TelemetryTracker(root)
    root.mainloop()



