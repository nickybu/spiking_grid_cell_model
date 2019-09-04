# Standard library imports
import errno
import os
import random
import time
import cPickle as pickle
import matplotlib.pyplot as plt
import numpy as np
import utilities as util
from pyNN.random import RandomDistribution, NumpyRNG
from pyNN.space import Grid2D
from pyNN.utility.plotting import Figure, Panel
import spynnaker8 as p

"""
Grid cell model with periodic boundary constraints
Connectivity: uniform 
Broad feedforward input: i_offset
Velocity input: none
"""

p.setup(1)  # simulation timestep (ms)
runtime = 30000  # ms

n_row = 50
n_col = 50
n_neurons = n_row * n_row
p.set_number_of_neurons_per_core(p.IF_curr_exp, 255)

self_connections = False  # allow self-connections in recurrent grid cell network

rng = NumpyRNG(seed=77364, parallel_safe=True)
synaptic_weight = 0.05  # synaptic weight for inhibitory connections
synaptic_radius = 10  # inhibitory connection radius
centre_shift = 2  # number of neurons to shift centre of connectivity by

# Grid cell (excitatory) population
gc_neuron_params = {
    "v_thresh": -50.0,
    "v_reset": -65.0,
    "v_rest": -65.0,
    "i_offset": 0.8,  # DC input
    "tau_m": 20,  # membrane time constant
    "tau_refrac": 1.0,
}

exc_grid = Grid2D(aspect_ratio=1.0, dx=1.0, dy=1.0, x0=0, y0=0, z=0, fill_order='sequential')
# exc_space = p.Space(axes='xy', periodic_boundaries=((-n_col / 2, n_col / 2), (-n_row / 2, n_row / 2)))
v_init = RandomDistribution('uniform', low=-65, high=-55, rng=rng)
pop_exc_gc = p.Population(n_neurons,
                          p.IF_curr_exp(**gc_neuron_params),
                          cellparams=None,
                          initial_values={'v': v_init},
                          structure=exc_grid,
                          label="Excitatory grid cells"
                          )

# Create recurrent inhibitory connections
loop_connections = list()
for pre_syn in range(0, n_neurons):
    presyn_pos = (pop_exc_gc.positions[pre_syn])[:2]
    dir_pref = np.array(util.get_dir_pref(presyn_pos))

    # Shift centre of connectivity in appropriate direction
    shifted_centre = util.shift_centre_connectivity(presyn_pos, dir_pref, centre_shift, n_row, n_col)
    for post_syn in range(0, n_neurons):
        # If different neurons
        if pre_syn != post_syn or self_connections:
            postsyn_pos = (pop_exc_gc.positions[post_syn])[:2]
            dist = util.get_neuron_distance_periodic(n_col, n_row, shifted_centre, postsyn_pos)

            # Establish connection
            if np.all(dist <= synaptic_radius):
                # delay = util.normalise(dist, 1, 5)
                delay = 1.0
                singleConnection = (pre_syn, post_syn, synaptic_weight, delay)
                loop_connections.append(singleConnection)

# Create inhibitory connections
proj_exc = p.Projection(
    pop_exc_gc, pop_exc_gc, p.FromListConnector(loop_connections, ('weight', 'delay')),
    p.StaticSynapse(),
    receptor_type='inhibitory',
    label="Excitatory grid cells inhibitory connections")

"""
RUN
"""
pop_exc_gc.record(['v', 'gsyn_inh', 'spikes'])
p.run(runtime)

"""
WRITE DATA
"""

# Write data to files
data_dir = "data/" + time.strftime("%Y-%m-%d_%H-%M-%S") + "/"

# Create directory
try:
    os.makedirs(os.path.dirname(data_dir))
except OSError as exc:
    if exc.errno != errno.EEXIST:
        raise

# Excitatory population
# pickle.dump(pop_exc.get_data().segments[0].filter(name='v')[0],
#             open(data_dir + "pop_exc_v.pkl", 'wb'),
#             protocol=pickle.HIGHEST_PROTOCOL)
# pickle.dump(pop_exc.get_data().segments[0].filter(name='gsyn_exc')[0],
#             open(data_dir + "pop_exc_gsyn_exc.pkl", 'wb'),
#             protocol=pickle.HIGHEST_PROTOCOL)
# pickle.dump(pop_exc.get_data().segments[0].filter(name='gsyn_inh')[0],
#             open(data_dir + "pop_exc_gsyn_inh.pkl", 'wb'),
#             protocol=pickle.HIGHEST_PROTOCOL)
pickle.dump(pop_exc_gc.get_data().segments[0].spiketrains,
            open(data_dir + "pop_exc_gc_spiketrains.pkl", 'wb'),
            protocol=pickle.HIGHEST_PROTOCOL)
pickle.dump(pop_exc_gc.label, open(data_dir + "pop_exc_gc_label.pkl", 'wb'),
            protocol=pickle.HIGHEST_PROTOCOL)
pickle.dump(pop_exc_gc.positions, open(data_dir + "pop_exc_gc_positions.pkl", 'wb'),
            protocol=pickle.HIGHEST_PROTOCOL)
pickle.dump(gc_neuron_params, open(data_dir + "pop_exc_gc_parameters.pkl", 'wb'),
            protocol=pickle.HIGHEST_PROTOCOL)

f = open(data_dir + "params.txt", "w")
f.write("Single population grid cell (periodic) model")
f.write("\nruntime=" + str(runtime))
f.write("\nn_row=" + str(n_row))
f.write("\nn_col=" + str(n_col))
f.write("\nsyn_weight=" + str(synaptic_weight))
f.write("\nsyn_radius=" + str(synaptic_radius))
f.write("\norientation_pref_shift=" + str(centre_shift))
f.write("\npop_exc=" + str(pop_exc_gc.describe()))
f.close()

rand_neurons = random.sample(range(0, n_neurons), 4)
neuron_sample = p.PopulationView(pop_exc_gc, rand_neurons)

# Plot
F = Figure(
    # plot data for postsynaptic neuron
    Panel(neuron_sample.get_data().segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          xlabel="Time (ms)",
          data_labels=[neuron_sample.label], yticks=True, xticks=True, xlim=(0, runtime)
          ),
)
plt.savefig(data_dir + "sample_v.eps", format='eps')
plt.show()

F = Figure(
    Panel(neuron_sample.get_data().segments[0].filter(name='gsyn_inh')[0],
          ylabel="inhibitory synaptic conduction (nA)",
          xlabel="Time (ms)",
          data_labels=[neuron_sample.label], yticks=True, xticks=True, xlim=(0, runtime)
          ),
)
plt.savefig(data_dir + "sample_gsyn_inh.eps", format='eps')
plt.show()

F = Figure(
    Panel(neuron_sample.get_data().segments[0].spiketrains,
          yticks=True, xticks=True, markersize=2, xlim=(0, runtime)
          ),
)
rand_neurons = map(str, rand_neurons)
plt.yticks(np.arange(4), rand_neurons)
plt.savefig(data_dir + "sample_spikes.eps", format='eps')
plt.show()

# util.plot_gc_inh_connections([1325, 1275, 1326, 1276], pop_exc_gc.positions, synaptic_weight, loop_connections,
#                              n_col, n_row, synaptic_radius, orientation_pref_shift, data_dir)
# util.plot_neuron_init_order(pop_exc_gc.positions, data_dir)

gsyn_inh = pop_exc_gc.get_data().segments[0].filter(name='gsyn_inh')[0]
print("Max gsyn_inh=" + str(util.get_max_value_from_pop(gsyn_inh)))
# print("Min gsyn_inh=" + str(util.get_min_value_from_pop(gsyn_inh)))
print("Avg gsyn_inh=" + str(util.get_avg_gsyn_from_pop(gsyn_inh)))

print("Mean spike count: " + str(pop_exc_gc.mean_spike_count(gather=True)))
print("Max spike count: " + str(util.get_max_firing_rate(pop_exc_gc.get_data().segments[0].spiketrains)))

p.end()
print(data_dir)
