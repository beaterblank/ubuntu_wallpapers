import time
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

from fit_type import FitType, Fill, Fit, Stretch, Tile, Center, FIT  # Import your FitType classes
from fit_type import Wallpaper,make_wallpaper
from util import set_picture_spanned,get_monitor_info,set_wallpaper_from

class UbuntuMultiWall(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ubuntu Multi Wall")
        self.configure(bg="#2E2E2E")  # Dark background color
        self.resize_id = None
        self.after_id = None
        self.bind("<Configure>", self.on_resize)
        # Create and configure canvas
        self.canvas = tk.Canvas(self, bg="#1E1E2E", highlightthickness=0, width=800, height=400)
        self.canvas.grid(row=1, column=0, columnspan=4, sticky="nsew")

        self.monitor_info = get_monitor_info()
        
        # Create and configure refresh button
        self.refresh_button = tk.Button(self, text="Reset", command=self.refresh, bg="#3C3C3C", fg="white", relief=tk.FLAT)
        self.refresh_button.grid(row=0, column=0, padx=5, pady=10)

        self.set_wallpaper_button = tk.Button(self, text="Set Wallaper", command=self.set_wallpaper, bg="#3C3C3C", fg="white", relief=tk.FLAT)
        self.set_wallpaper_button.grid(row=0, column=3, padx=5, pady=10)

        screen_numbers = ["Screen - "+ str(screen['screen_number']) for screen in self.monitor_info['screens']]
        self.selected_screen_number = 0

        # Create and configure screen dropdown
        self.screen_dropdown = ttk.Combobox(self, values=screen_numbers, style="TCombobox")
        self.screen_dropdown.grid(row=0, column=2, padx=5, pady=10)
        self.screen_dropdown.bind("<<ComboboxSelected>>", self.on_screen_select)

        # Create and configure fit type dropdown
        self.fit_type = tk.StringVar(value="fill")
        self.fit_type_menu = ttk.Combobox(self, textvariable=self.fit_type, values=["fill", "fit", "center", "stretch", "tile"], style="TCombobox")
        self.fit_type_menu.grid(row=0, column=1, padx=5, pady=10)
        self.fit_type_menu.bind('<<ComboboxSelected>>', self.modified)

        # Configure styles
        style = ttk.Style()
        style.configure("TCombobox", background="#2E2E2E", foreground="black", borderwidth=1, relief="flat")
        style.configure("TCombobox.dropdown", background="#2E2E2E", foreground="black")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.monitor_ids = {}
        self.image_refs = {}
        self.image_paths = {}
        self.selected_fit_types = {}  # Dictionary to keep track of fit types for each monitor
        self.selected_rectangle = None
        self.selected_border = None  # ID of the selected border
        self.scale_factor = 10
        self.canvas.bind_all("<Button-4>", self.on_mouse_wheel_up)
        self.canvas.bind_all("<Button-5>", self.on_mouse_wheel_down)

        self.update_idletasks()

        self.fit_type_menu.set("fill")
        self.screen_dropdown.set(screen_numbers[0])


        self.refresh()

    def on_resize(self, event):
        if self.after_id is not None:
            self.after_cancel(self.after_id)
        self.after_id = self.after(100, self._on_resize_end)

    def set_wallpaper(self):
        monitors = self.monitor_info['screens'][self.selected_screen_number]['devices']
        bg_w = self.monitor_info['screens'][self.selected_screen_number]["current_width"]
        bg_h = self.monitor_info['screens'][self.selected_screen_number]["current_height"]
        wallpapers = []
        for monitor in monitors:
            if not monitor['is_connected']:
                continue
            fit_type = self.selected_fit_types.get(monitor['device_name'], self.fit_type.get())
            if monitor['device_name'] not in self.image_paths.keys():
                return
            wallpapers.append(Wallpaper(  
                    image_dir = self.image_paths[monitor['device_name']],
                    w = monitor['resolution_width'],
                    h = monitor['resolution_height'],
                    x = monitor['offset_width'],
                    y = monitor['offset_height'],
                    device_name = monitor['device_name'],
                    fit_type = FIT[fit_type.upper()].value,
                )
            )
        save_dir = make_wallpaper(wallpapers,bg_w,bg_h,"default")
        set_wallpaper_from(save_dir)
        set_picture_spanned()



    def _on_resize_end(self):
        self.draw_monitors()
        for monitor_name, file_path in self.image_paths.items():
            self.process_image(file_path, monitor_name)
        
    def modified(self, event):
        if not self.selected_rectangle:
            return
        for monitor_name, file_path in self.image_paths.items():
            if monitor_name == self.selected_rectangle:
                self.selected_fit_types[monitor_name] = self.fit_type.get()
                self.process_image(file_path, monitor_name)

    def on_mouse_wheel_up(self,event):
        # Adjust the scale factor
        self.scale_factor = min(self.scale_factor + 1, 50)
        # Refresh the canvas with the new scale factor
        self.draw_monitors()
        for monitor_name, file_path in self.image_paths.items():
            self.process_image(file_path, monitor_name)

    def on_mouse_wheel_down(self,event):
        # Adjust the scale factor
        self.scale_factor = max(self.scale_factor - 1, 2)
        # Refresh the canvas with the new scale factor
        self.draw_monitors()
        for monitor_name, file_path in self.image_paths.items():
            self.process_image(file_path, monitor_name)

    def refresh(self):
        self.monitor_info = get_monitor_info()
        for image_ref in self.image_refs.keys():
            self.canvas.delete(image_ref)
        self.canvas.delete(self.selected_border)  # Remove the old border
        self.monitor_ids = {}
        self.image_refs = {}
        self.image_paths = {}
        self.selected_fit_types = {}  # Dictionary to keep track of fit types for each monitor
        self.selected_rectangle = None
        self.selected_border = None
        self.draw_monitors()

    def draw_monitors(self):
        self.canvas.delete("all")
        if not self.monitor_info:
            self.monitor_info = get_monitor_info()

        monitors = self.monitor_info['screens'][self.selected_screen_number]['devices']
        self.monitor_ids.clear()

        scale_factor = self.scale_factor
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        total_width = self.monitor_info['screens'][self.selected_screen_number]["current_width"] / scale_factor
        total_height = self.monitor_info['screens'][self.selected_screen_number]["current_height"] / scale_factor


        x_offset = canvas_width/2 - total_width/2
        y_offset = canvas_height/2 - total_height/2

        for monitor in monitors:
            if monitor['is_connected']:
                scaled_width = monitor['resolution_width'] / scale_factor
                scaled_height = monitor['resolution_height'] / scale_factor
                x0 = x_offset + (monitor['offset_width'] / scale_factor)
                y0 = y_offset + (monitor['offset_height'] / scale_factor)
                x1 = x0 + scaled_width
                y1 = y0 + scaled_height

                monitor_id = self.canvas.create_rectangle(x0, y0, x1, y1, fill="#4C4C4C", outline="#6C6C6C", tags=monitor['device_name'])
                self.monitor_ids[monitor['device_name']] = self.canvas.coords(monitor_id)
                self.canvas.tag_bind(monitor_id, "<Button-1>", self.on_monitor_click)  # Single-click
                self.canvas.tag_bind(monitor_id, "<Double-1>", self.on_monitor_double_click)  # Double-click

    def on_monitor_click(self, event):
        monitor_name = self.canvas.gettags(event.widget.find_closest(event.x, event.y))[0]
        self.selected_rectangle = monitor_name
        self.update_border(monitor_name)

    def update_border(self, monitor_name):
        # Remove the old border
        if self.selected_border:
            self.canvas.delete(self.selected_border)

        # Draw a white border around the selected rectangle
        if monitor_name in self.monitor_ids:
            x0, y0, x1, y1 = self.monitor_ids[monitor_name]
            self.selected_border = self.canvas.create_rectangle(x0, y0, x1, y1, outline="white", width=2)

    def on_monitor_double_click(self, event):
        monitor_name = self.canvas.gettags(event.widget.find_closest(event.x, event.y))[0]
        monitor = next((m for m in self.monitor_info['screens'][self.selected_screen_number]['devices'] if m['device_name'] == monitor_name), None)
        if monitor:
            print("Opening file dialog for monitor:", monitor_name)  # Debug statement
            file_path = filedialog.askopenfilename(title="Select New Image File")
            if file_path:
                print("Selected file path:", file_path)  # Debug statement
                self.process_image(file_path, monitor_name)
            else:
                print("No file selected.")  # Debug statement
        else:
            print(f"{monitor_name} not found")

    def process_image(self, file_path, monitor_name):
        monitor = next((m for m in self.monitor_info['screens'][self.selected_screen_number]['devices'] if m['device_name'] == monitor_name), None)
        if monitor:
            # Get the fit type for the selected monitor
            fit_type = self.selected_fit_types.get(monitor_name, self.fit_type.get().lower())
            fit_type_class = FIT[fit_type.upper()].value
            fit_type_instance = fit_type_class(monitor['resolution_width'], monitor['resolution_height'], file_path)
            processed_image = fit_type_instance.fit_to_size()

            # Convert the processed image to PhotoImage
            tk_image = ImageTk.PhotoImage(processed_image)

            # Get the coordinates of the selected rectangle
            x0, y0, x1, y1 = self.monitor_ids[monitor_name]
            width = x1 - x0
            height = y1 - y0

            image_tag = monitor_name

            # Resize the processed image to fit within the rectangle
            processed_image = processed_image.resize((int(width), int(height)), Image.LANCZOS)
            tk_image = ImageTk.PhotoImage(processed_image)

            # Remove any existing image on the canvas
            self.canvas.delete(image_tag)

            # Display the image on the canvas within the bounds of the rectangle
            monitor_id = self.canvas.create_image((x0, y0), image=tk_image, anchor=tk.NW, tags=image_tag)
            self.canvas.tag_bind(monitor_id, "<Button-1>", self.on_monitor_click)  # Single-click
            self.canvas.tag_bind(monitor_id, "<Double-1>", self.on_monitor_double_click)  # Double-click
            self.image_refs[image_tag] = tk_image  # Keep a reference to avoid garbage collection
            self.image_paths[monitor_name] = file_path

            # Update border around selected rectangle
            if monitor_name == self.selected_rectangle:
                self.update_border(monitor_name)

    def on_screen_select(self, event):
        selected_screen = self.screen_dropdown.get()
        screen_number =  int(selected_screen.split(" - ")[1])
        self.selected_screen_number = screen_number
        # Handle screen selection if needed


if __name__ == "__main__":
    app = UbuntuMultiWall()
    app.mainloop()

