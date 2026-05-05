"""
Figure 4: The accessibility and travel distance over time for a certain scenario.
"""

import os
import sys
import piperabm as pa
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from analysis.access import access_json


path_here = os.path.dirname(os.path.realpath(__file__))
names = [
    '0_0_0_0',  # control
    '0_0_0_2',  # critical impact 15%
    '0_0_0_5',  # random impact 15%
]
titles = [
    'Control',
    '15% Critical Impact',
    '15% Random Impact',
]

def alive_ratio_from_accessibility(measurement):
    """
    Compute alive ratio using absorbing death logic.

    An agent is considered dead once A_i,t == 0, where A_i,t is the
    geometric mean of food, water, and energy accessibility. Once dead,
    the agent remains dead for all later time steps.
    """
    agent_access = measurement.accessibility.sum_resources(
        agents="all",
        resources="all"
    )

    agent_ids = list(agent_access.keys())
    n_agents = len(agent_ids)
    n_steps = measurement.accessibility.len

    dead_agents = set()
    alive_ratio = []
    alive_count = []
    death_count = []

    for t in range(n_steps):
        for agent_id in agent_ids:
            if agent_id in dead_agents:
                continue

            if agent_access[agent_id][t] <= 0:
                dead_agents.add(agent_id)

        n_alive = n_agents - len(dead_agents)

        alive_count.append(n_alive)
        death_count.append(len(dead_agents))
        alive_ratio.append(n_alive / n_agents)

    return alive_ratio, alive_count, death_count

results = []

for i, name in enumerate(names):
    path, access = access_json(
        path_here=path_here,
        scenario_name=name,
        file_name="measurement.json"
    )
    measurement = pa.Measurement(
        path=path,
        name=name
    )
    measurement.load()
    alive_ratio, alive_count, death_count = alive_ratio_from_accessibility(measurement)
    result = {
        'title': titles[i],
        'accessibility': measurement.accessibility(),
        'average accessibility': measurement.accessibility.average(),
        'alive ratio': alive_ratio,
        'alive count': alive_count,
        'death count': death_count,
        'travel distance': measurement.travel_distance(),
        'average travel distance': measurement.travel_distance.average(),
        'delta_times': measurement.filter_times()
    }
    results.append(result)

def show(results):
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(15, 8))

    # Variables to determine the global min and max for x and y axes
    min_time, max_time = float('inf'), float('-inf')
    min_access, max_access = 0, 1  # Assuming normalized accessibility between 0 and 1
    min_travel, max_travel = float('inf'), float('-inf')

    # Calculate global min and max for axes
    for result in results:
        min_time = min(min_time, min(result['delta_times']))
        max_time = max(max_time, max(result['delta_times']))
        min_travel = min(min_travel, min(result['travel distance']))
        max_travel = max(max_travel, max(result['travel distance']))

    # Convert seconds to days
    min_time /= 86400
    max_time /= 86400

    # Plotting and setting the same axis ranges for all subplots
    for i, result in enumerate(results):
        times_in_days = [time / 86400 for time in result['delta_times']]  # Convert each time point to days

        # Accessibility plot in the first row
        axes[0, i].plot(times_in_days, result['accessibility'])
        axes[0, i].set_title(f'{result["title"]}', fontweight='bold')
        axes[0, i].set_xlabel('Time (days)', fontweight='bold')
        axes[0, i].set_ylabel('Accessibility', fontweight='bold')
        axes[0, i].set_xlim(min_time, max_time)
        axes[0, i].set_ylim(min_access, max_access)
        axes[0, i].text(0.62, 0.9, f'Average: {result["average accessibility"]:.3f}',
                        transform=axes[0, i].transAxes, fontsize=12, fontweight='bold')
        
        
        # Add alive fractions to the same plot
        axes[0, i].plot(
            times_in_days,
            result['alive ratio'],
            color='darkorange',   # explicitly set
            linestyle='--',
            label='survival ratio'
        )

        axes[0, i].legend()
        
        
        # Travel distance plot in the second row
        axes[1, i].plot(times_in_days, result['travel distance'])
        axes[1, i].set_title(f'{result["title"]}', fontweight='bold')
        axes[1, i].set_xlabel('Time (days)', fontweight='bold')
        axes[1, i].set_ylabel('Travel Distance (m)', fontweight='bold')
        axes[1, i].set_xlim(min_time, max_time)
        axes[1, i].set_ylim(min_travel, max_travel)
        axes[1, i].text(0.64, 0.9, f'Average: {result["average travel distance"]:.0f}',
                        transform=axes[1, i].transAxes, fontsize=12, fontweight='bold')

    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.show()  # Display the plots

show(results)
#for result in results:
#    print(result['average accessibility'])