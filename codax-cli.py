import os
import subprocess
from typing import Optional

# third party
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
    subprocess.run(command)
    for prompt, script in scripts:
        spinner = Halo(text=f"CODAX CLI {VERSION}", spinner='dots')
        spinner.start()
        spinner.text = prompt
        typer.echo(script)
        if not subprocess.run(["bash", f"scripts/install/{script}"]).returncode:  # nosec
            spinner.stop_and_persist(symbol='🦄 '.encode(
                'utf-8'), text=f'\033[1;32mCompleted:{prompt}\n')
        else:
            spinner.fail(f"Failed:{prompt}")
        spinner.stop()

    typer.echo("\nProcedure Completed!  \n")


@app.command()
def get_container_info(pid: Optional[str] = None, n: Optional[int] = 50):
    if not is_service_running('codax.service'):
        raise ServiceNotFoundException(
            f"codax.service not found!! install and configure with `codax-cli  install` ")
    directory = os.path.join(os.path.expanduser("~"), ".codax", "data")
    threshold_info = dict()
    files = os.listdir(directory)
    for file_ in files:
        name, extension = os.path.splitext(file_)
        if extension == ".thresh":
            with open(os.path.join(directory, file_), 'r') as thresh_file:
                threshold_info[name] = {"data": thresh_file.read().strip()}
            try:
                with open(os.path.join(directory, name), 'r') as thresh_file:
                    threshold_info[name]["series"] = [
                        int(x) for x in thresh_file.read().split(" ")]
            except Exception as exception_:
                typer.echo(exception_)
                typer.echo(f"Failed to fetch the cpu-time sequence for {name}")
    # typer.echo(threshold_info)
    table_data = [
        ['Container ID', 'Threshold Value', 'info'], ]
    if pid:
        if pid in threshold_info:
            # nosec
            os.system(f'ps -p {pid} -o pid,ppid,user,stat,cmd,%cpu,%mem,etime')
            if n:
                if n >= len(threshold_info[pid]["series"]):
                    raise ExceedsLengthException(
                        f"N exceeds the size of cpu-sequence({n}>={len(threshold_info[pid]['series'])})")
                    return
            typer.echo(f"\033[33mThe graph shows the last {n} cpu-time sequence")
            plot_graph(threshold_info, pid, n)
            typer.echo(
                "\033[31mcodax-cli get-container-info --pid <container_pid> --log <n> : ")
            typer.echo("\t Log the past n  cpu-time sequence")

            input("\033[34mPress Enter to see the past cpu-times...")
            typer.echo(f"cpu-time sequence: {threshold_info[pid]['series']}")
            return

    for key, value in threshold_info.items():
        table_data.append([key, value["data"], ""])
    typer.echo(
        f"\nCODAX:{VERSION}\nFollowing table shows the list of containers with the present threshold value")
    plot_table(table_data)
    typer.echo("\033[31mcodax-cli get-container-info --pid <container_pid>: ")
    typer.echo("\t To get the detailed view of individual containers")
    typer.echo("\033[31mcodax-cli get-container-info --pid <container_pid> --log <n> : ")
    typer.echo("\t Log the past n  cpu-time sequence")


if __name__ == "__main__":
    app()
