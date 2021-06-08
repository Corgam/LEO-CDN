import sys
import subprocess
import os
import shutil
import json
from jinja2 import Template
import toml

############
## Config ##
############

# Load the config
with open("./config.toml") as f:
    config = toml.load(f)
# Number of nodes to generate
planes = config["satellites"]["planes"]
satellite_per_planes = config["satellites"]["satellites_per_plane"]
groundstation_number = config["stardust"]["groundstations"]
# TODO: this +1 is for the simulation because atm it requires to init all keygroups in the beginning -> change this
satellite_number = planes * satellite_per_planes +1

# Create temp directory
print("Creating temp directory...")
if not os.path.exists("./temp"):
    os.makedirs("./temp")
else:
    # If the temp dir already exists, remove it and it's files and make new empty one
    shutil.rmtree("./temp")
    os.makedirs("./temp")

##################
## Certificates ##
##################

# Copy the certificates generator files
shutil.copyfile("./common/cert/gen-cert.sh", "./temp/gen-cert.sh")
shutil.copyfile("./common/cert/generate-n-certificates.sh", "./temp/generate-n-certificates.sh")
shutil.copyfile("./common/cert/generate-n-certificates-stardusts.sh", "./temp/generate-n-certificates-stardusts.sh")
shutil.copyfile("./common/cert/ca.crt", "./temp/ca.crt")
shutil.copyfile("./common/cert/ca.key", "./temp/ca.key")

# Generating certificates for satellites and groundstations

# Run specific command based on OS
# Nodes will have IP starting from 127.26.7.1 (to not use the NS's IP)
# To prevent 'Anomalous backslash in string' warning: '\\' inside string
if sys.platform.startswith("win"):
    print(f"Generating certificates for {satellite_number} satellites...")
    subprocess.call(".\\temp\\generate-n-certificates.sh '%s'" % str(satellite_number), shell=True)
    print(f"Generating certificates for {groundstation_number} groundstations...")
    subprocess.call(".\\temp\\generate-n-certificates-stardusts.sh '%s'" % str(groundstation_number), shell=True)
elif sys.platform.startswith("linux"):
    print(f"Generating certificates for {satellite_number} satellites...")
    subprocess.call("sh ./temp/generate-n-certificates.sh '%s'" % str(satellite_number), shell=True)
    print(f"Generating certificates for {groundstation_number} groundstations...")
    subprocess.call("sh ./temp/generate-n-certificates-stardusts.sh '%s'" % str(groundstation_number), shell=True)

# Remove the certificate generator files
os.remove("./temp/gen-cert.sh")
os.remove("./temp/generate-n-certificates.sh")
os.remove("./temp/generate-n-certificates-stardusts.sh")
os.remove("./temp/ca.crt")
os.remove("./temp/ca.key")
os.remove("./temp/ca.srl")

###############
## YML files ##
###############

# Creating the yml files for satellites
print(f"Generating yml files for {satellite_number} satellites...")

with open("common/templates/satelliteX.yaml.jinja2") as file_:
    node_template = Template(file_.read())

for x in range(satellite_number):
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

# Creating the yml files for stardusts
print(f"Generating yml files for {groundstation_number} groundstations...")

with open("common/templates/stardustX.yaml.jinja2") as file_:
    node_template = Template(file_.read())

for x in range(groundstation_number):
    stardust_IP = f"172.26.3.{x}"
    stardust_name = f"stardust{x}"
    host_port = 9001

    nodex_yaml = node_template.render(
        stardust_IP=stardust_IP,
        stardust_name=stardust_name,
        host_port=host_port,
    )
    with open(f"./temp/stardust{x}.yml", "w") as f:
        f.write(nodex_yaml)

################
## SH scripts ##
################

# Create a lists of satellites and stardusts names
node_names = [f"satellite{x}" for x in range(satellite_number)]
stardust_names = [f"stardust{x}" for x in range(groundstation_number)]

# Generate start script for satellites
with open("common/templates/run-nodes.sh.jinja2") as file_:
    run_script_template = Template(file_.read())

run_script = run_script_template.render(node_names=node_names)

with open(f"./temp/run-nodes.sh", "w") as f:
    f.write(run_script)

# Generate start script for groundstations
with open("common/templates/run-stardusts.sh.jinja2") as file_:
    run_stardusts_template = Template(file_.read())

run_stardusts_template = run_stardusts_template.render(stardust_names=stardust_names)

with open(f"./temp/run-stardusts.sh", "w") as f:
    f.write(run_stardusts_template)

# Generate clean script
with open("common/templates/clean.sh.jinja2") as file_:
    clean_script_template = Template(file_.read())

clean_script = clean_script_template.render(
    node_names=node_names,
    stardust_names=stardust_names
    )

with open(f"./temp/clean.sh", "w") as f:
    f.write(clean_script)

###############
## JSON file ##
###############

# Generate JSON with node data
with open("./temp/freds.json", "w") as f:
    nodes_config = {
        f"fred{x}": {"host": f"172.26.{x + 7}.1", "port": 9001} for x in range(satellite_number)
    }
    json.dump(nodes_config, f, indent=4)

for x in range(satellite_number):
    with open(f"./temp/satellite{x}.json", "w") as f:
        nodes_config = {
            f"satellite{x}": {"server": f"172.26.{x + 7}.3", "sport": 5000, "node": f"172.26.{x + 7}.1", "nport": 9001,
                              "fred": f"fred{x}"}
        }
        json.dump(nodes_config, f, indent=4)

################
## TOML files ##
################

print(f"Generating toml starting files for {groundstation_number} groundstations...")

with open("common/templates/stardustX.toml.jinja2") as file_:
    toml_template = Template(file_.read())

for x in range(groundstation_number):
    stardust_IP = f"172.26.3.{x}"
    stardust_name = f"stardust{x}"
    requests_per_stardust = config["stardust"]["requests_per_stardust"]

    nodex_yaml = toml_template.render(
        stardust_IP=stardust_IP,
        stardust_name=stardust_name,
        requests_per_stardust=requests_per_stardust
    )
    with open(f"./temp/stardust{x}.toml", "w") as f:
        f.write(nodex_yaml)
