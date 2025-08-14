# gui/dashboard.py
import tkinter as tk
from tkinter import ttk, messagebox
import queue


def start_dashboard(app_config, data_queue):
    """Initializes and runs the Tkinter GUI."""
    root = tk.Tk()
    root.title("AUTOQOS Dashboard")
    root.geometry("650x550")

    # --- Main Process Table ---
    tree = ttk.Treeview(root, columns=("Process", "Priority", "Limit", "Status"), show="headings")
    tree.heading("Process", text="Process Name")
    tree.heading("Priority", text="Priority")
    tree.heading("Limit", text="Speed Limit")
    tree.heading("Status", text="Status")
    # Column widths
    tree.column("Process", width=250)
    tree.column("Priority", width=80, anchor="center")
    tree.column("Limit", width=120, anchor="center")
    tree.column("Status", width=100, anchor="center")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Rule Editor Frame ---
    editor_frame = ttk.LabelFrame(root, text="Rule Editor", padding="10")
    editor_frame.pack(fill=tk.X, padx=10, pady=5)

    process_entry = ttk.Entry(editor_frame, width=30)
    priority_entry = ttk.Entry(editor_frame, width=10)

    def add_or_update_rule():
        """Handles the 'Add/Update' button click."""
        process_name = process_entry.get().strip()
        priority_str = priority_entry.get().strip()

        if not process_name or not priority_str:
            messagebox.showwarning("Input Error", "Process name and priority cannot be empty.")
            return
        try:
            priority_int = int(priority_str)
            if priority_int not in app_config["PRIORITY_SPEED_MAP"]:
                messagebox.showwarning("Input Error",
                                       f"Invalid priority: {priority_int}. Must be one of {list(app_config['PRIORITY_SPEED_MAP'].keys())}.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Priority must be a number.")
            return

        # Update the rule in the shared APP_CONFIG dictionary
        app_config["process_rules"][process_name] = {"priority": priority_int}
        messagebox.showinfo("Success", f"Rule for '{process_name}' has been set to priority {priority_int}.")
        process_entry.delete(0, tk.END)
        priority_entry.delete(0, tk.END)

    add_button = ttk.Button(editor_frame, text="Add / Update Rule", command=add_or_update_rule)

    ttk.Label(editor_frame, text="Process Name:").pack(side=tk.LEFT, padx=5)
    process_entry.pack(side=tk.LEFT, padx=5)
    ttk.Label(editor_frame, text="Set Priority (0-5):").pack(side=tk.LEFT, padx=5)
    priority_entry.pack(side=tk.LEFT, padx=5)
    add_button.pack(side=tk.LEFT, padx=10)

    def on_row_select(event):
        """Populates the editor when a row in the table is clicked."""
        if not tree.selection(): return
        # Get the selected item
        item = tree.item(tree.selection()[0])
        # Get values from the selected row (returns a tuple of strings)
        values = item['values']

        # Clear entry boxes and insert the new values
        process_entry.delete(0, tk.END)
        process_entry.insert(0, values[0])  # Process Name is the first value
        priority_entry.delete(0, tk.END)
        priority_entry.insert(0, str(values[1]))  # Priority is the second value

    tree.bind("<<TreeviewSelect>>", on_row_select)

    def process_queue():
        """Checks the queue for new data from the monitor thread and updates the GUI table."""
        try:
            data = data_queue.get_nowait()
            # Clear all existing items from the tree
            tree.delete(*tree.get_children())
            # Insert new data
            if data:
                for row in data:
                    tree.insert("", "end", values=row)
        except queue.Empty:
            # If the queue is empty, do nothing
            pass

        # Schedule this function to run again after 1 second
        root.after(1000, process_queue)

    # Start the queue processing loop
    root.after(100, process_queue)
    root.mainloop()