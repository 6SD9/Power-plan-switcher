import psutil
import subprocess
import time
import threading
import pystray
from PIL import Image, ImageDraw
import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, scrolledtext
import sys

if getattr(sys, "frozen", False):
    real_dir_path = os.path.dirname(sys.executable)
else:
    real_dir_path = os.path.dirname(os.path.realpath(__file__))

CONFIG_FILE = os.path.join(real_dir_path, "power_plan_config.json")

exit_flag = threading.Event()
reload_flag = threading.Event()

DEFAULT_CONFIG = {
    "check_interval": 1,
    "power_plans": {
        "0": {
            "name": "BALANCED_PLAN",
            "guid": "",
            "processes": [],
        },
        "1": {
            "name": "NO_TURBO_BOOST_PLAN",
            "guid": "",
            "processes": ["WINWORD.EXE"],
        },
        "2": {
            "name": "MEDIUM_FREQ_PLAN",
            "guid": "",
            "processes": ["Client-Win64-Shipping.exe"],
        },
        "3": {
            "name": "HIGH_FREQ_PLAN",
            "guid": "",
            "processes": ["Cherry Studio.exe"],
        },
        "4": {
            "name": "BALANCED_PLAN",
            "guid": "",
            "processes": [
                "EXCEL.EXE",
                "Photoshop.exe",
                "Code.exe",
            ],
        },
    },
}


class PowerPlan:
    def __init__(self, name, guid):
        self.name = name
        self.guid = guid


class ConfigManager:
    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                return DEFAULT_CONFIG
        else:
            with open(CONFIG_FILE, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)


def set_power_plan(power_plan):
    try:
        subprocess.run(f"powercfg /setactive {power_plan.guid}", shell=True, check=True)
    except subprocess.CalledProcessError:
        pass


def monitor_processes():
    config = ConfigManager.load_config()
    check_interval = config.get("check_interval", 1)
    power_plans_config = config["power_plans"]

    power_plan_dict = {}
    for level, plan_config in power_plans_config.items():
        power_plan_dict[int(level)] = PowerPlan(
            plan_config["name"], plan_config["guid"]
        )

    target_processes = {}
    for level, plan_config in power_plans_config.items():
        target_processes[int(level)] = [p.lower() for p in plan_config["processes"]]

    power_current_level = 0
    power_current_target_level = 0

    active_processes = set()

    try:
        while not exit_flag.is_set():
            if reload_flag.is_set():
                config = ConfigManager.load_config()
                check_interval = config.get("check_interval", 1)
                power_plans_config = config["power_plans"]

                power_plan_dict = {}
                for level, plan_config in power_plans_config.items():
                    power_plan_dict[int(level)] = PowerPlan(
                        plan_config["name"], plan_config["guid"]
                    )

                target_processes = {}
                for level, plan_config in power_plans_config.items():
                    target_processes[int(level)] = [
                        p.lower() for p in plan_config["processes"]
                    ]

                power_current_level = 0
                power_current_target_level = 0
                active_processes = set()
                set_power_plan(power_plan_dict[0])

                reload_flag.clear()

            current_processes = set()
            proc_current_target_level = set()

            for proc in psutil.process_iter(["name"]):
                try:
                    proc_name = proc.info["name"].lower()

                    for level, process_list in target_processes.items():
                        if proc_name in process_list:
                            proc_current_target_level.add(level)
                            current_processes.add(proc_name)
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            new_processes = current_processes - active_processes
            if new_processes:
                if proc_current_target_level:
                    power_current_target_level = max(proc_current_target_level)
                    if power_current_target_level > power_current_level:
                        set_power_plan(power_plan_dict[power_current_target_level])
                        power_current_level = power_current_target_level

            exited_processes = active_processes - current_processes
            if exited_processes:
                if proc_current_target_level:
                    power_current_target_level = max(proc_current_target_level)
                    if power_current_target_level < power_current_level:
                        set_power_plan(power_plan_dict[power_current_target_level])
                        power_current_level = power_current_target_level
                else:
                    set_power_plan(power_plan_dict[0])
                    power_current_level = 0

            active_processes = current_processes
            time.sleep(check_interval)

    except KeyboardInterrupt:
        exit_program()
    finally:
        set_power_plan(power_plan_dict[0])


class ConfigGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Power Plan Monitor")
        self.root.geometry("500x500")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.config = ConfigManager.load_config()

        self.tab_control = ttk.Notebook(self.root)

        self.general_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(self.general_frame, text="General")

        ttk.Label(self.general_frame, text="检测周期(秒)interval:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.interval_var = tk.StringVar(
            value=str(self.config.get("check_interval", 1))
        )
        ttk.Entry(self.general_frame, textvariable=self.interval_var, width=10).grid(
            row=0, column=1, padx=10, pady=10, sticky="w"
        )

        self.plan_frames = {}
        for level in ["0", "1", "2", "3", "4"]:
            frame = ttk.Frame(self.tab_control)
            self.tab_control.add(frame, text=f"Level {level}")
            self.plan_frames[level] = frame

            plan_config = self.config["power_plans"].get(level, {})

            ttk.Label(frame, text="计划名称 Name:").grid(
                row=0, column=0, padx=10, pady=5, sticky="w"
            )
            name_var = tk.StringVar(value=plan_config.get("name", ""))
            ttk.Entry(frame, textvariable=name_var, width=30).grid(
                row=0, column=1, padx=10, pady=5, sticky="w"
            )

            ttk.Label(frame, text="GUID:").grid(
                row=1, column=0, padx=10, pady=5, sticky="w"
            )
            guid_var = tk.StringVar(value=plan_config.get("guid", ""))
            ttk.Entry(frame, textvariable=guid_var, width=40).grid(
                row=1, column=1, padx=10, pady=5, sticky="w"
            )

            ttk.Label(frame, text="监控进程(每行一个) Processes:").grid(
                row=2, column=0, padx=10, pady=5, sticky="nw"
            )
            processes_text = scrolledtext.ScrolledText(frame, width=30, height=10)
            processes_text.grid(row=2, column=1, padx=10, pady=5, sticky="w")

            processes = plan_config.get("processes", [])
            processes_text.insert(tk.END, "\n".join(processes))

            self.__setattr__(f"name_var_{level}", name_var)
            self.__setattr__(f"guid_var_{level}", guid_var)
            self.__setattr__(f"processes_text_{level}", processes_text)

        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        save_button = ttk.Button(self.root, text="Save", command=self.save_config)
        save_button.pack(pady=10)

        close_button = ttk.Button(self.root, text="Close", command=self.on_closing)
        close_button.pack(pady=5)

    def save_config(self):
        try:
            self.config["check_interval"] = float(self.interval_var.get())

            for level in ["0", "1", "2", "3", "4"]:
                name_var = self.__getattribute__(f"name_var_{level}")
                guid_var = self.__getattribute__(f"guid_var_{level}")
                processes_text = self.__getattribute__(f"processes_text_{level}")

                processes = processes_text.get("1.0", tk.END).strip().splitlines()
                processes = [p.strip() for p in processes if p.strip()]

                self.config["power_plans"][level] = {
                    "name": name_var.get(),
                    "guid": guid_var.get(),
                    "processes": processes,
                }

            ConfigManager.save_config(self.config)
            messagebox.showinfo("成功", "配置已保存！")
            reload_flag.set()

        except Exception as e:
            messagebox.showerror("错误", f"保存配置时出错: {str(e)}")

    def on_closing(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def create_tray_icon():
    image = create_default_icon()

    menu = (
        pystray.MenuItem("Settings", open_config_gui),
        pystray.MenuItem("Exit", exit_program),
    )

    icon = pystray.Icon("Power_Plan_Monitor", image, "电源计划监控器", menu)
    return icon


def create_default_icon():
    image = Image.new("RGB", (64, 64), "Black")
    draw = ImageDraw.Draw(image)
    draw.rectangle([4, 4, 60, 60], fill="DarkGray")
    draw.rectangle([12, 12, 52, 52], fill="White")
    draw.rectangle([22, 22, 42, 42], fill="DarkGray")
    draw.rectangle([42, 28, 52, 36], fill="DarkGray")
    return image


def open_config_gui():
    def run_gui():
        try:
            ConfigGUI().run()
        except Exception as e:
            pass

    threading.Thread(target=run_gui, daemon=True).start()


def exit_program():
    exit_flag.set()

    try:
        config = ConfigManager.load_config()
        power_plans_config = config["power_plans"]
        balanced_plan = PowerPlan(
            power_plans_config["0"]["name"], power_plans_config["0"]["guid"]
        )
        set_power_plan(balanced_plan)
    except Exception as e:
        pass

    time.sleep(0.5)
    os._exit(0)


if __name__ == "__main__":
    try:
        subprocess.check_output(
            "whoami /groups /fo list | findstr S-1-16-12288", shell=True
        )
    except:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("错误", "请以管理员权限运行此程序")
        root.destroy()
        exit(1)

    tray_icon = create_tray_icon()
    tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
    tray_thread.start()

    monitor_processes()
