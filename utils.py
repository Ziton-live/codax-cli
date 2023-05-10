import os
import subprocess

import numpy as np
import termplotlib as tpl

scripts = [["Disabling existing services", "compile.sh"],
           ["Fetching", 'disable-codax.sh'], ["Compiling", "compile.sh"],
           ["Enabling codax.services", "enable-codax.sh"]]


def plot_table(data):
    widths = [max(len(str(row[i])) for row in data)
              for i in range(len(data[0]))]
    print('+{}+'.format('+'.join('-' * (w + 2) for w in widths)))
    print('| {} | {} | {} |'.format(data[0][0].ljust(
        widths[0]), data[0][1].ljust(widths[1]), data[0][2].ljust(widths[2])))
    print('+{}+'.format('+'.join('-' * (w + 2) for w in widths)))

    for row in data[1:]:
        print('| {} | {} | {} |'.format(row[0].ljust(
            widths[0]), row[1].ljust(widths[1]), row[2].ljust(widths[2])))

    print('+{}+'.format('+'.join('-' * (w + 2) for w in widths)))


def is_service_running(service_name):
    try:
        output = subprocess.check_output(
            ['systemctl', 'is-active', service_name])  # nosec
        return output.strip() == b'active'
    except subprocess.CalledProcessError:
        return False


def plot_graph(threshold_info, pid, n):
    y = threshold_info[pid]["series"][-n:]
    x = np.array([i for i, num in enumerate(y)])
    fig = tpl.figure()
    fig.plot(x, y, width=os.get_terminal_size().columns, height=30, )
    fig.show()
