import sys
import subprocess
import os
import shutil
import json
from jinja2 import Template

# Validates command line argument
if len(sys.argv) != 3:
    print("generator.py -node <number>")
    exit()

if sys.argv[1] != "-node":
    print("generator.py -node <number>")
    exit()

if not sys.argv[2].isnumeric():
    print("generator.py -node <number>")
    exit()

if int(sys.argv[2]) < 1:
    print("Please use a number >0")
    exit()

# Number of nodes to generate
nodes = int(sys.argv[2])

# Create temp directory
print("Creating temp directory...")
if not os.path.exists("./temp"):
    os.makedirs("./temp")
else:
    # If the temp dir already exists, remove it and make new one
    shutil.rmtree("./temp")
    os.makedirs("./temp")

# Copy the certificates generators
shutil.copyfile("./cert/gen-cert.sh", "./temp/gen-cert.sh")
shutil.copyfile(
    "./cert/generate-n-certificates.sh", "./temp/generate-n-certificates.sh"
)
shutil.copyfile("./cert/ca.crt", "./temp/ca.crt")
shutil.copyfile("./cert/ca.key", "./temp/ca.key")
shutil.copyfile("./cert/ca.key", "./temp/ca.key")


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

# Creating the yml files
print(f"Generating yml file for {nodes} nodes...")

with open("template/nodex.yaml.jinja2") as file_:
    node_template = Template(file_.read())

for x in range(nodes):
    node_IP = f"172.26.{x+7}.1"
    store_IP = f"172.26.{x+7}.2"
    node_name = f"node{x}"
    store_name = f"store{x}"
    host_port = 9000 + x + 3
    nase_host = "https://172.26.6.1:2379"

    nodex_yaml = node_template.render(
        node_IP=node_IP,
        store_IP=store_IP,
        node_name=node_name,
        store_name=store_name,
        host_port=host_port,
        nase_host=nase_host,
    )
    with open(f"./temp/node{x}.yml", "w") as f:
        f.write(nodex_yaml)


# Create a list of node names
node_names = [f"node{x}" for x in range(nodes)]


# Generate start script

with open("template/run-nodes.sh.jinja2") as file_:
    run_script_template = Template(file_.read())

run_script = run_script_template.render(node_names=node_names)

with open(f"./temp/run-nodes.sh", "w") as f:
    f.write(run_script)


# Generate clean script

with open("template/clean.sh.jinja2") as file_:
    clean_script_template = Template(file_.read())

clean_script = clean_script_template.render(node_names=node_names)

with open(f"./temp/clean.sh", "w") as f:
    f.write(clean_script)


# Generate JSON with node data

with open("./temp/nodes.json", "w") as f:
    nodes_config = {
        f"node{x}": {"host": f"172.26.{x + 7}.1", "port": 9001} for x in range(nodes)
    }
    json.dump(nodes_config, f, indent=4)

for x in range(nodes):
    with open(f"./temp/node{x}.json", "w") as f:
        nodes_config = {
            f"node{x}": {"server": f"172.26.{x + 7}.3", "sport": 5000, "node": f"172.26.{x + 7}.1", "nport": 9001}
        }
        json.dump(nodes_config, f, indent=4)