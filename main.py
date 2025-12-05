import tkinter as tk
from gui import UvsimGUI

def monitor_windows(root):
    # Count how many windows exist (root + Toplevels)
    if len(root.winfo_children()) == 0:
        root.quit()
    else:
        root.after(200, lambda: monitor_windows(root))

def main():
    #GUI Setup 
    root = tk.Tk()
    root.withdraw()            # -- Hiding the real root window --

    first_window = tk.Toplevel()
    app = UvsimGUI(first_window)

    monitor_windows(root)

    root.mainloop()

if __name__ == "__main__":
    main()

#test