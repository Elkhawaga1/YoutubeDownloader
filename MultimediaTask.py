import os
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import yt_dlp as youtube_dl
import time

# Global variables
output_path = "downloads"
ffmpeg_path = r'C:/ffmpeg/bin/ffmpeg.exe'
download_cancelled = threading.Event()
download_paused = threading.Event()  # Flag for paused state
current_download = None
download_thread = None

# Function to download the video/audio
def download_video(url, quality, download_type):
    global download_cancelled, download_paused, current_download
    ydl_opts = {
        'ffmpeg_location': ffmpeg_path,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'noplaylist': True
    }

    if download_type == 'video':
        ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best'
    elif download_type == 'audio':
        ydl_opts['format'] = 'bestaudio'

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            download_cancelled.clear()
            download_paused.clear()
            current_download = ydl  # Store the current download instance
            ydl.download([url])
            if not download_cancelled.is_set():
                messagebox.showinfo("Success", f"Downloaded {download_type} successfully!")
            else:
                messagebox.showinfo("Cancelled", "Download was cancelled.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

    # Re-enable UI
    update_ui_for_idle()

# Update UI elements for idle state
def update_ui_for_idle():
    download_button.config(state="normal")
   





# Progress hook for the progress bar
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        root.after(0, update_progress_bar, percent)  # Safely update UI
    elif d['status'] == 'finished':
        print(f"Download finished: {d['filename']}")
        root.after(0, update_progress_bar, 100)

# Update progress bar
def update_progress_bar(percent):
    progress_bar['value'] = percent
    root.update_idletasks()

# Start download in a separate thread
def start_download():
    url = url_entry.get()
    quality = quality_var.get()
    download_type = download_type_var.get()

    download_button.config(state="disabled")

    progress_bar['value'] = 0

    global download_thread
    download_thread = threading.Thread(target=download_video, args=(url, quality, download_type))
    download_thread.start()

# Choose output folder
def choose_output_folder():
    global output_path
    folder = filedialog.askdirectory(initialdir=output_path, title="Select Output Folder")
    if folder:
        output_path = folder
        output_label.config(text=f"Output folder: {output_path}")

# Exit handler
def on_close():
    if download_thread and download_thread.is_alive():
        if messagebox.askokcancel("Quit", "Download in progress. Are you sure you want to quit?"):
            download_cancelled.set()
            root.quit()
    else:
        root.quit()

# GUI setup
root = tk.Tk()
root.title("YouTube Video Downloader")
root.protocol("WM_DELETE_WINDOW", on_close)

# URL input
tk.Label(root, text="Enter YouTube URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=10)

# Video quality options
tk.Label(root, text="Select Video Quality:").pack(pady=10)
quality_var = tk.StringVar(value="720")
quality_menu = tk.OptionMenu(root, quality_var, "720", "1080", "480", "360")
quality_menu.pack(pady=10)

# Download type (Video or Audio)
tk.Label(root, text="Select Download Type:").pack(pady=10)
download_type_var = tk.StringVar(value="video")
download_type_menu = tk.OptionMenu(root, download_type_var, "video", "audio")
download_type_menu.pack(pady=10)

# Output folder button
output_button = tk.Button(root, text="Choose Output Folder", command=choose_output_folder)
output_button.pack(pady=10)

# Output folder label
output_label = tk.Label(root, text=f"Output folder: {output_path}")
output_label.pack(pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=20)

# Buttons for download, pause, and cancel
download_button = tk.Button(root, text="Download", command=start_download)
download_button.pack(pady=10)



# Start Tkinter event loop
root.mainloop()
