import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import os
from datetime import datetime 
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age 
        self.weight_records = [] #stores tuples 
    
    def add_weight(self,weight):
        date = datetime.today().strftime('%Y-%m-%d')
        self.weight_records.append((date,weight))

class WeightTrackerApp:
    def __init__(self,root):
        self.user = User("Add Name", 30) #example user

        self.root = root
        self.root.title("Weight Tracker")

        self.label = tk.Label(root, text="Enter Weight")
        self.label.pack(pady=5)

        self.weight_entry = tk.Entry(root)
        self.weight_entry.pack(pady=5)

        self.add_button = tk.Button(root, text="Add Weight", command=self.add_weight)
        self.add_button.pack(pady=5)

        self.save_button = tk.Button(root, text="Save to Excel", command=self.save_to_excel)
        self.save_button.pack(pady=5)

        self.view_button = tk.Button(root, text="View Past Records", command=self.view_past_records)
        self.view_button.pack(pady=5)

        self.plot_button = tk.Button(root, text="Visualize Weight Trend", command=self.plot_weight_trend)
        self.plot_button.pack(pady=5)
    

    def add_weight(self):
        weight = self.weight_entry.get() #get input value

        if weight.replace('.','',1).isdigit(): #allows decimals
            self.user.add_weight(float(weight))
            messagebox.showinfo("Success", f"Weight {weight} added")
            self.weight_entry.delete(0,tk.END) #clear input field
        else:
            messagebox.showerror("Error", "Please enter a valid number.")
    
    def save_to_excel(self):

        if not self.user.weight_records:
            messagebox.showwarning("Warning", "No weight records to save!")
            return
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "weight_tracker.xlsx")
        
        #converts weight records to dataframe
        new_data = pd.DataFrame(self.user.weight_records,columns=['Date','Weight'])

        if os.path.exists(filename):
            #load existing data
            existing_data = pd.read_excel(filename)
            
            #convert 'date' column to datetime format
            existing_data['Date'] = pd.to_datetime(existing_data['Date'])
            new_data['Date'] = pd.to_datetime(new_data['Date'])

            #get the first date in existing file 
            most_recent_date = existing_data['Date'].max()

            #filter new records that have a later date than the first entry
            new_data = new_data[new_data['Date'] > most_recent_date]

            if new_data.empty:
                messagebox.showwarning("Warning", "No new entries after the most recent recorded date.")
                return 
            updated_data = pd.concat([existing_data,new_data],ignore_index=True)
        else:
            updated_data = new_data

        updated_data.to_excel(filename,index=False)
        messagebox.showinfo("Saved", f"Data saved to {filename}")
    
    def view_past_records(self):
        """Displays past weight records in a new window"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "weight_tracker.xlsx")

        if not os.path.exists(filename):
            messagebox.showwarning("Warning","No records found.")

        #load data 
        df = pd.read_excel(filename)

        #create a new window to display records
        records_window = tk.Toplevel(self.root)
        records_window.title("Past Weight Records")

        # create a treeview widget 
        tree = ttk.Treeview(records_window, columns=("Date","Weight"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("Weight", text="Weight (lbs)")
        tree.pack(fill="both", expand=True)

        #Insert data into the treeview 
        for _, row in df.iterrows():
            tree.insert("", tk.END, values=(row['Date'], row['Weight']))
    
    def plot_weight_trend(self):
        #plots the weight trend over time 
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "weight_tracker.xlsx")

        if not os.path.exists(filename):
            messagebox.showwarning("Warning", "No records found.")
            return

        # Load data
        df = pd.read_excel(filename)

        # Convert 'Date' to datetime for sorting
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by="Date")

        # Create a new window for the plot
        plot_window = tk.Toplevel(self.root)
        plot_window.title("Weight Trend")

        # Create a Matplotlib figure
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(df['Date'], df['Weight'], marker='o', linestyle='-', color='b')

        ax.set_xlabel("Date")
        ax.set_ylabel("Weight (lb)")
        ax.set_title("Weight Trend Over Time")
        ax.grid(True)

        # Embed Matplotlib figure in Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

root = tk.Tk()

app = WeightTrackerApp(root)

root.mainloop()

