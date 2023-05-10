
import subprocess  # nosec
import os
from typing import Optional
# third party
import numpy as np
import typer
from halo import Halo
# local
from exceptions import ServiceNotFoundException, ExceedsLengthException
from utils import is_service_running, plot_table, scripts, plot_graph

VERSION = '0.0.1'
app = typer.Typer()


@app.command()
def version():
    typer.echo(VERSION)


@app.command()
def install():
    command = ['sudo', 'echo', 'CODAX CLI']
    subprocess.run(command)  # nosec
    i=0
    for prompt, script in scripts:
        spinner = Halo(text=f"CODAX CLI {VERSION}", spinner='dots')
        spinner.start()
        spinner.text = prompt
        script_file = f"script{i}.sh" #nosec
        subprocess.run(["curl", "-o", script_file, script]) #nosec
        subprocess.run(["chmod", "+x", script_file]) #nosec
        subprocess.run(["bash",  script_file]) #nosec
        i+=1
    
        if not subprocess.run(["./" + script_file]).returncode:  # nosec
            spinner.stop_and_persist(symbol='🦄 '.encode(
                'utf-8'), text=f'\033[1;32mCompleted:{prompt}\n')
        else:
            spinner.fail(f"Failed:{prompt}")
        spinner.stop()
        
    print("\nInstalled Succesfully!  \n")


@app.command()
def get_container_info(pid: Optional[str] = None, n: Optional[int] = 50):
    if (not is_service_running('codax.service')):
        raise ServiceNotFoundException(
            f"codax.service not found!! install and configure with `codax-cli  install` ")
    DIRECTORY = os.path.join(os.path.expanduser("~"), ".codax", "data")
    threshold_info = dict()
    files = os.listdir(DIRECTORY)
    for file_ in files:
        name, extension = os.path.splitext(file_)
        if extension == ".thresh":
            with open(os.path.join(DIRECTORY, file_), 'r') as thresh_file:
                threshold_info[name] = {"data": thresh_file.read().strip()}
            try:
                with open(os.path.join(DIRECTORY, name), 'r') as thresh_file:
                    threshold_info[name]["series"] = [
                        int(x) for x in thresh_file.read().split(" ")]
            except Exception as e:
                print(e)
                print(f"Failed to fetch the cpu-time sequence for {name}")
    # print(threshold_info)
    table_data = [
        ['Container ID', 'Threshold Value', 'info'],]
    if pid:
        if pid in threshold_info:
            os.system(f"ps -p {pid} -o pid,ppid,user,stat,cmd,%cpu,%mem,etime") # nosec
            if n:
                if n >= len(threshold_info[pid]["series"]):
                    raise ExceedsLengthException(
                        f"N exceeds the size of cpu-sequence({n}>={len(threshold_info[pid]['series'])})")
                    return
            print(f"\033[33mThe graph shows the last {n} cpu-time sequence")
            plot_graph(threshold_info, pid, n);
            print(
                "\033[31mcodax-cli get-container-info --pid <container_pid> --log <n> : ")
            print("\t Log the past n  cpu-time sequence")

            input("\033[34mPress Enter to see the past cpu-times...")
            print(f"cpu-time sequence: {threshold_info[pid]['series']}")
            return

    for key, value in threshold_info.items():
        table_data.append([key, value["data"], ""])
    print(
        f"\nCODAX:{VERSION}\nFollowing table shows the list of containers with the present threshold value")
    plot_table(table_data)
    print("\033[31mcodax-cli get-container-info --pid <container_pid>: ")
    print("\t To get the detailed view of individual containers")
    print("\033[31mcodax-cli get-container-info --pid <container_pid> --log <n> : ")
    print("\t Log the past n  cpu-time sequence")


if __name__ == "__main__":
    app()
