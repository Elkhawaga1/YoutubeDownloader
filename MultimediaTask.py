import os
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import yt_dlp as youtube_dl
import time


output_path = "downloads"
ffmpeg_path = r'C:/ffmpeg/bin/ffmpeg.exe'
download_cancelled = threading.Event()
download_paused = threading.Event()  
current_download = None
download_thread = None


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
            current_download = ydl  
            ydl.download([url])
            if not download_cancelled.is_set():
                messagebox.showinfo("Success", f"Downloaded {download_type} successfully!")
            else:
                messagebox.showinfo("Cancelled", "Download was cancelled.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

    
    update_ui_for_idle()


def update_ui_for_idle():
    download_button.config(state="normal")
   

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        root.after(0, update_progress_bar, percent)  
    elif d['status'] == 'finished':
        print(f"Download finished: {d['filename']}")
        root.after(0, update_progress_bar, 100)


def update_progress_bar(percent):
    progress_bar['value'] = percent
    root.update_idletasks()


def start_download():
    url = url_entry.get()
    quality = quality_var.get()
    download_type = download_type_var.get()

    download_button.config(state="disabled")

    progress_bar['value'] = 0

    global download_thread
    download_thread = threading.Thread(target=download_video, args=(url, quality, download_type))
    download_thread.start()


def choose_output_folder():
    global output_path
    folder = filedialog.askdirectory(initialdir=output_path, title="Select Output Folder")
    if folder:
        output_path = folder
        output_label.config(text=f"Output folder: {output_path}")


def on_close():
    if download_thread and download_thread.is_alive():
        if messagebox.askokcancel("Quit", "Download in progress. Are you sure you want to quit?"):
            download_cancelled.set()
            root.quit()
    else:
        root.quit()


root = tk.Tk()
root.title("YouTube Video Downloader")
root.protocol("WM_DELETE_WINDOW", on_close)


tk.Label(root, text="Enter YouTube URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=10)


tk.Label(root, text="Select Video Quality:").pack(pady=10)
quality_var = tk.StringVar(value="720")
quality_menu = tk.OptionMenu(root, quality_var, "720", "1080", "480", "360")
quality_menu.pack(pady=10)


tk.Label(root, text="Select Download Type:").pack(pady=10)
download_type_var = tk.StringVar(value="video")
download_type_menu = tk.OptionMenu(root, download_type_var, "video", "audio")
download_type_menu.pack(pady=10)


output_button = tk.Button(root, text="Choose Output Folder", command=choose_output_folder)
output_button.pack(pady=10)


output_label = tk.Label(root, text=f"Output folder: {output_path}")
output_label.pack(pady=10)


progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=20)


download_button = tk.Button(root, text="Download", command=start_download)
download_button.pack(pady=10)


root.mainloop()
