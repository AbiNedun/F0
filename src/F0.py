# Abisharan Nedun | ENAE380 | FINAL PROJECT 

############################################

# Open this file and run, may need to interrupt if user opened a track figure  

# Design is not just what it looks and feels like. Design is how it works - Steve Jobs 

from .F0visual import TelemetryTracker
import tkinter

def main():
    # Code to initialize and launch the GUI
    root = tkinter.Tk()
    app = TelemetryTracker(root) 
    root.mainloop()
if __name__ == "__main__":
   main()

# Enjoy..!
