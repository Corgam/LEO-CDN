from multiprocessing import Process
import coordinator_server
import simulation_with_h3

print("[setup_simulation]: Init simulation")
simulation_with_h3.init()


print("[setup_simulation]: Run coordinator")
server = Process(target=coordinator_server.run_server)
server.start()

print("[setup_simulation]: Run simulation")
simulation = Process(target=simulation_with_h3.run_simulation)
simulation.start()



