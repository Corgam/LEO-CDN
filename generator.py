import json
import os
import shutil
import subprocess
import sys

import toml
from jinja2 import Template

############
## Config ##
############

# Load the config
with open("./config.toml") as f:
    config = toml.load(f)
# Number of nodes to generate
planes = config["satellites"]["planes"]
satellite_per_planes = config["satellites"]["satellites_per_plane"]
nodes = planes * satellite_per_planes

# Create temp directory
print("Creating temp directory...")
if not os.path.exists("./temp"):
    os.makedirs("./temp")
else:
    # If the temp dir already exists, remove it and it's files and make new empty one
    shutil.rmtree("./temp")
    os.makedirs("./temp")

##########
## Data ##
##########

# Copy the file containing all groundstations information
gsts_list = config["general"]["gsts_list"]
print("Selecting all data files...")
shutil.copyfile(gsts_list, "./temp/gsts.csv")

# Copy the file order
# TODO: If workload is not generated: run the makefile command
if os.path.isfile(config["workload"]["output_file"]) and os.path.isfile(
    config["workload"]["file_size_output_file"]
):
    shutil.copyfile(config["workload"]["output_file"], "./temp/file_orders.json")
    shutil.copyfile(
        config["workload"]["file_size_output_file"], "./temp/file_sizes.csv"
    )
else:
    print("Workload is not generated. Please generate with `make generate_workload`!")


##################
## Certificates ##
##################

# Copy the certificates generator files
shutil.copyfile("./common/cert/gen-cert.sh", "./temp/gen-cert.sh")
shutil.copyfile(
    "./common/cert/generate-n-certificates.sh", "./temp/generate-n-certificates.sh"
)
shutil.copyfile("./common/cert/ca.crt", "./temp/ca.crt")
shutil.copyfile("./common/cert/ca.key", "./temp/ca.key")

# Generating certificates for every store and fred node
print(f"Generating certificates for {nodes} nodes...")

# Generate n certificates
# Run specific command based on OS
# Nodes will have IP starting from 127.26.7.1 (to not use the NS's IP)
# To prevent 'Anomalous backslash in string' warning: '\\' inside string
if sys.platform.startswith("win"):
    subprocess.call(".\\temp\\generate-n-certificates.sh '%s'" % str(nodes), shell=True)
elif sys.platform.startswith("linux"):
    subprocess.call(
        "sh ./temp/generate-n-certificates.sh '%s'" % str(nodes), shell=True
    )

# Remove the certificate generator files
os.remove("./temp/gen-cert.sh")
os.remove("./temp/generate-n-certificates.sh")
os.remove("./temp/ca.crt")
os.remove("./temp/ca.key")
os.remove("./temp/ca.srl")

###############
## YML files ##
###############

# Creating the yml files
print(f"Generating yml file for {nodes} nodes...")

with open("common/templates/satelliteX.yaml.jinja2") as file_:
    node_template = Template(file_.read())

for x in range(nodes):
    node_IP = f"172.26.{x + 7}.1"
    store_IP = f"172.26.{x + 7}.2"
    server_IP = f"172.26.{x + 7}.3"
    node_name = f"fred{x}"
    store_name = f"store{x}"
    server_name = f"satellite{x}"
    host_port = 9000 + x + 3
    nase_host = "https://172.26.6.1:2379"

    nodex_yaml = node_template.render(
        node_IP=node_IP,
        store_IP=store_IP,
        node_name=node_name,
        store_name=store_name,
        host_port=host_port,
        nase_host=nase_host,
        server_name=server_name,
        server_IP=server_IP,
    )
    with open(f"./temp/satellite{x}.yml", "w") as f:
        f.write(nodex_yaml)

################
## SH scripts ##
################

# Create a list of node names
node_names = [f"satellite{x}" for x in range(nodes)]

# Generate start script
with open("common/templates/run-nodes.sh.jinja2") as file_:
    run_script_template = Template(file_.read())

run_script = run_script_template.render(node_names=node_names)

with open(f"./temp/run-nodes.sh", "w") as f:
    f.write(run_script)

# Generate clean script
with open("common/templates/clean.sh.jinja2") as file_:
    clean_script_template = Template(file_.read())

clean_script = clean_script_template.render(node_names=node_names)

with open(f"./temp/clean.sh", "w") as f:
    f.write(clean_script)

###############
## JSON file ##
###############

# Generate JSON with node data
with open("./temp/freds.json", "w") as f:
    nodes_config = {
        f"fred{x}": {"host": f"172.26.{x + 7}.1", "port": 9001} for x in range(nodes)
    }
    json.dump(nodes_config, f, indent=4)

for x in range(nodes):
    with open(f"./temp/satellite{x}.json", "w") as f:
        nodes_config = {
            f"satellite{x}": {
                "server": f"172.26.{x + 7}.3",
                "sport": 5000,
                "node": f"172.26.{x + 7}.1",
                "nport": 9001,
                "fred": f"fred{x}",
            }
        }
        json.dump(nodes_config, f, indent=4)
