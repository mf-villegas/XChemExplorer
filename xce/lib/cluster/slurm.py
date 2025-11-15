import os
import ssl
import json
import http.client
import paramiko
import time
import traceback

# GTK is only available in Python 2 and needed for Coot plugins
# Make it optional for Python 3 compatibility
try:
    import gtk
    HAS_GTK = True
except (ImportError, ModuleNotFoundError):
    HAS_GTK = False

from PyQt5 import QtGui, QtWidgets
from datetime import datetime
from xce.lib.XChemLog import updateLog
from uuid import uuid4

CLUSTER_BASTION = "wilson.diamond.ac.uk"
CLUSTER_USER = os.environ.get("CLUSTER_USER", os.getlogin())
CLUSTER_HOST = "slurm-rest.diamond.ac.uk"
CLUSTER_PORT = 8443
CLUSTER_PARTITION = "cs05r"

TOKEN = None
TOKEN_EXPIRY = None

POPUP_TITLE = "SLURM Authentication"


def fetch_password_qt(password_prompt):
    password, ok = QtWidgets.QInputDialog.getText(
        None, POPUP_TITLE, password_prompt, mode=QtWidgets.QLineEdit.Password
    )
    return password if ok else None


def fetch_password_gtk(password_prompt):
    """
    GTK password dialog for Coot plugins.
    Falls back to Qt dialog if GTK is not available (Python 3).
    """
    if not HAS_GTK:
        # Fallback to Qt dialog when GTK is not available
        print("Warning: GTK not available, using Qt dialog instead")
        return fetch_password_qt(password_prompt)

    dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK_CANCEL,
        None,
    )
    dialog.set_title(POPUP_TITLE)
    dialog.set_markup(password_prompt)

    entry = gtk.Entry()
    entry.set_visibility(False)
    dialog.vbox.pack_end(entry)
    dialog.show_all()

    dialog.run()
    password = entry.get_text()
    dialog.destroy()
    return password


def get_token(fetch_password, error=None):
    global TOKEN
    global TOKEN_EXPIRY

    if TOKEN is None or TOKEN_EXPIRY is None or TOKEN_EXPIRY < time.time() + 60:
        password_prompt = error + "\n" + "Password:" if error else "Password:"
        password = fetch_password(password_prompt)
        if password is None:
            return None

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        try:
            ssh.connect(CLUSTER_BASTION, username=CLUSTER_USER, password=str(password))
        except paramiko.AuthenticationException:
            print(traceback.format_exc())
            return get_token(fetch_password, error="SSH Authentication Failed")
        stdin, stdout, stderr = ssh.exec_command("scontrol token lifespan=3600")
        if stdout.channel.recv_exit_status() != 0:
            return get_token(fetch_password, error="Token Acquisition Failed")
        final_line = next(stdout)
        for final_line in stdout:
            continue
        TOKEN = final_line.split("=")[1].strip()
        TOKEN_EXPIRY = time.time() + 3600
    return TOKEN


def construct_headers(token):
    return {
        "Content-Type": "application/json",
        "X-SLURM-USER-NAME": CLUSTER_USER,
        "X-SLURM-USER-TOKEN": token,
    }


def submit_cluster_job(
    name, file, xce_logfile, token, array=None, exclusive=False, memory=None, tasks=None
):
    with open(file) as script_file:
        script = "\n".join(script_file.readlines())
    payload = dict(
        script=script,
        job=dict(
            partition=CLUSTER_PARTITION,
            name=str(name),
            account=CLUSTER_USER,
            current_working_directory=os.getcwd(),
            environment=[
                "USER={}".format(os.environ["USER"]),
                "XChemExplorer_DIR={}".format(os.environ["XChemExplorer_DIR"]),
            ],
            standard_output=os.path.join(os.getcwd(), "{}.stdout".format(name)),
            standard_error=os.path.join(os.getcwd(), "{}.stderr".format(name)),
        ),
    )
    if array is not None:
        payload["job"]["array"] = array
    if exclusive is True:
        payload["job"]["exclusive"] = "mcs"
        payload["job"]["mcs_label"] = str(uuid4())
    if memory is not None:
        payload["job"]["memory_per_node"] = dict()
        payload["job"]["memory_per_node"]["set"] = True
        payload["job"]["memory_per_node"]["number"] = memory
    if tasks is not None:
        payload["job"]["tasks_per_node"] = tasks
    body = json.dumps(payload)
    logfile = updateLog(xce_logfile)
    logfile.insert("Submitting job, '{}', to Slurm with body: {}".format(name, body))
    connection = http.client.HTTPSConnection(
        CLUSTER_HOST, CLUSTER_PORT, context=ssl._create_unverified_context()
    )
    connection.request(
        "POST", "/slurm/v0.0.40/job/submit", body=body, headers=construct_headers(token)
    )
    response = connection.getresponse().read()
    logfile.insert("Got response: {}".format(response))


def query_running_jobs(xce_logfile, token):
    connection = http.client.HTTPSConnection(
        CLUSTER_HOST,
        CLUSTER_PORT,
        context=ssl._create_unverified_context(),
    )
    connection.request("GET", "/slurm/v0.0.40/jobs", headers=construct_headers(token))
    response = connection.getresponse()
    response_body = response.read()

    if response.status != 200:
        logifle = updateLog(xce_logfile)
        logifle.insert("Got response: {}".format(response_body))

    jobs = []
    for job in json.loads(response_body)["jobs"]:
        if job["user_name"] != CLUSTER_USER:
            continue

        job_id = job["job_id"]
        job_name = job["name"]
        job_status = job["job_state"]

        start_time = datetime.utcfromtimestamp(job["start_time"])
        run_time = datetime.now() - start_time

        jobs.append((job_id, job_name, job_status, run_time))

    return jobs
