#!/usr/bin/env python

import logging

from tulip import transys, spec, synth
# @import_section_end@

#
# System dynamics
#
# The system is modeled as a discrete transition system in which the
# robot can be located anyplace on a 2x3 grid of cells.  Transitions
# between adjacent cells are allowed, which we model as a transition
# system in this example (it would also be possible to do this via a
# formula)
#
# We label the states using the following picture
#
#     +----+----+----+
#     | X3 | X4 | X5 |
#     +----+----+----+
#     | X0 | X1 | X2 |
#     +----+----+----+

#     +----+-----+-----+
#     | X9 | X10 | X11 |
#     +----+-----+------+
#     | X6 | X7  | X8  |
#     +----+-----+-----+

#

# @system_dynamics_section@
# Create a finite transition system
sys = transys.FTS()

# Define the states of the system
sys.states.add_from(['X0', 'X1', 'X2', 'X3', 'X4', 'X5','X6', 'X7', 'X8', 'X9', 'X10', 'X11'])
sys.states.initial.add('X0')    # start in state X0

# Define the allowable transitions
#! TODO (IF): can arguments be a singleton instead of a list?
#! TODO (IF): can we use lists instead of sets?
#!   * use optional flag to allow list as label
sys.transitions.add_comb({'X0'}, {'X1', 'X3','X6'})
sys.transitions.add_comb({'X1'}, {'X0', 'X4', 'X2','X7'})
sys.transitions.add_comb({'X2'}, {'X1', 'X5','X8'})
sys.transitions.add_comb({'X3'}, {'X0', 'X4','X9'})
sys.transitions.add_comb({'X4'}, {'X3', 'X1', 'X5','X10'})
sys.transitions.add_comb({'X5'}, {'X4', 'X2','X11'})


sys.transitions.add_comb({'X6'}, {'X7', 'X9','X0'})
sys.transitions.add_comb({'X7'}, {'X6', 'X10', 'X8','X1'})
sys.transitions.add_comb({'X8'}, {'X7', 'X11','X2'})
sys.transitions.add_comb({'X9'}, {'X6', 'X10','X3'})
sys.transitions.add_comb({'X10'}, {'X9', 'X7', 'X11','X4'})
sys.transitions.add_comb({'X11'}, {'X10', 'X8','X5'})
# @system_dynamics_section_end@

# @system_labels_section@
# Add atomic propositions to the states
sys.atomic_propositions.add_from({'home', 'lot','obs'})
sys.states.add('X6', ap={'home'})
sys.states.add('X0', ap={'home'})

sys.states.add('X5', ap={'lot'})
sys.states.add('X3',ap={'obs'})
sys.states.add('X7',ap={'obs'})
# @system_labels_section_end@

# if IPython and Matplotlib available
#sys.plot()
#xx = raw_input("Pause...")

# @environ_section@
env_vars = {'park'}
env_init = set()                # empty set
env_prog = '!park'
env_safe = set()                # empty set
# @environ_section_end@

# System specification
# @specs_setup_section@
# Augment the system description to make it GR(1)
#! TODO: create a function to convert this type of spec automatically
sys_vars = {'UAV1'}          # infer the rest from TS
sys_init = {'home'}
sys_prog = {'home'}    # []<>home
sys_prog|={'UAV1'}                  
sys_safe = {'((X (UAV1) <-> lot) || ((UAV1 && !park) )) && (!obs)'}
#sys_safe |= {'((X (UAV2) <-> lot) || ((UAV2 && !park) )) && (!obs)'}

#sys_safe |= {'(dum) != (obs)'}
# @specs_setup_section_end@

# @specs_create_section@
# Create the specification
specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                    env_safe, sys_safe, env_prog, sys_prog,
                    )
2# @specs_create_section_end@
print("han: sys = ")
print(specs)
# @synthesize@
# Moore machines
# controller reads `env_vars, sys_vars`, but not next `env_vars` values
specs.moore = True
# synthesizer should find initial system values that satisfy
# `env_init /\ sys_init` and work, for every environment variable
# initial values that satisfy `env_init`.
specs.qinit = '\E \A'
ctrl = synth.synthesize('omega', specs, sys=sys)
assert ctrl is not None, 'unrealizable'
# @synthesize_end@

# @plot_print@
if not ctrl.save('twoUAV.png'):
	print(ctrl)
# @plot_print_end@
