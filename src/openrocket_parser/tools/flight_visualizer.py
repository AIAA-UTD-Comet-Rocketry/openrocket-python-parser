"""
A Tool designed to visualize the simulation results from OpenRocket
"""
import argparse
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from openrocket_parser.simulations.loader import load_simulations_from_xml


def visualize_flight(sim_data, speed_multiplier=1.0, repeat=True):
    """
    Creates and runs the matplotlib animation for the flight data.
    """
    df = sim_data.flight_data

    # --- 1. SET UP THE PLOT LAYOUT ---
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(3, 2)  # 3 rows, 2 columns

    # Main trajectory plot
    # @TODO Make the titles customizable through a config file
    ax_traj = fig.add_subplot(gs[:, 0])  # Spans all rows, first column
    ax_traj.set_title("Flight Trajectory")
    ax_traj.set_xlabel("Downrange (m)")
    ax_traj.set_ylabel("Altitude (m)")
    ax_traj.grid(True)
    ax_traj.set_aspect('equal', adjustable='box')

    # Time series plots
    ax_alt = fig.add_subplot(gs[0, 1])  # Top-right
    ax_alt.set_title("Altitude vs. Time")
    ax_alt.set_ylabel("Altitude (m)")
    ax_alt.grid(True)

    ax_vel = fig.add_subplot(gs[1, 1])  # Middle-right
    ax_vel.set_title("Vertical Velocity vs. Time")
    ax_vel.set_ylabel("Velocity (m/s)")
    ax_vel.grid(True)

    ax_acc = fig.add_subplot(gs[2, 1])  # Bottom-right
    ax_acc.set_title("Vertical Acceleration vs. Time")
    ax_acc.set_xlabel("Time (s)")
    ax_acc.set_ylabel("Acceleration (m/s²)")
    ax_acc.grid(True)

    fig.tight_layout(pad=3.0)
    fig.suptitle(f"Flight Playback: {sim_data.name}", fontsize=16, y=0.99)

    ## --- INITIALIZE MAX VALUE TRACKERS ---
    max_values = {
        "alt": -float('inf'),
        "vel": -float('inf'),
        "acc": -float('inf'),
    }

    # --- 2. INITIALIZE PLOT ELEMENTS TO BE ANIMATED ---
    # Trajectory path line
    traj_line, = ax_traj.plot([], [], 'b-')  # Blue line for the path @TODO make this customizable
    # Rocket marker @TODO Make customizable
    rocket_marker, = ax_traj.plot([], [], 'r^', markersize=10, label='Rocket')
    ax_traj.legend()

    # Time series lines
    alt_line, = ax_alt.plot([], [], 'g-')
    vel_line, = ax_vel.plot([], [], 'm-')
    acc_line, = ax_acc.plot([], [], 'c-')

    # Add a text annotation for live data
    live_text = ax_traj.text(
        0.05, 0.95, '',
        transform=ax_traj.transAxes,
        verticalalignment='top'
    )

    alt_max_text = ax_alt.text(
        0.98, 0.95, '',
        transform=ax_alt.transAxes,
        ha='right', va='top', color='g'
    )
    vel_max_text = ax_vel.text(
        0.98, 0.95, '',
        transform=ax_vel.transAxes,
        ha='right', va='top', color='m'
    )
    acc_max_text = ax_acc.text(
        0.98, 0.95, '',
        transform=ax_acc.transAxes,
        ha='right', va='top', color='c'
    )

    # --- 3. DEFINE ANIMATION LOGIC ---
    # The time step in the data (e.g., 0.01s)
    data_time_step = df['time'].diff().mean()
    # How many data points to jump per animation frame
    frame_step = int(speed_multiplier) if speed_multiplier >= 1 else 1
    # Delay between animation frames in milliseconds
    if speed_multiplier > 0:
        frame_interval = max(
            (data_time_step / speed_multiplier) * 1000 * frame_step,
            1  # If the interval is less than 1, force it to one as pandas needs positive intervals
        )
    else:
        frame_interval = 0

    def init():
        """Initializes the plot for the animation."""
        # Set plot limits based on the full dataset
        ax_traj.set_xlim(0, df['lateral_distance'].max() * 1.1)
        ax_traj.set_ylim(0, df['altitude'].max() * 1.1)

        ax_alt.set_xlim(0, df['time'].max())
        ax_alt.set_ylim(df['altitude'].min(), df['altitude'].max() * 1.1)

        ax_vel.set_xlim(0, df['time'].max())
        ax_vel.set_ylim(
            df['vertical_velocity'].min() * 1.1,
            df['vertical_velocity'].max() * 1.1
        )

        ax_acc.set_xlim(0, df['time'].max())
        ax_acc.set_ylim(
            df['vertical_acceleration'].min() * 1.1,
            df['vertical_acceleration'].max() * 1.1
        )

        # Reset all lines and text
        traj_line.set_data([], [])
        rocket_marker.set_data([], [])
        alt_line.set_data([], [])
        vel_line.set_data([], [])
        acc_line.set_data([], [])
        live_text.set_text('')

        return (traj_line, rocket_marker, alt_line, vel_line, acc_line, live_text,
                alt_max_text, vel_max_text, acc_max_text)

    def update(frame_index):
        """Called for each frame of the animation."""
        # Get the current slice of data based on the frame index
        current_index = frame_index * frame_step
        if current_index >= len(df):
            current_index = len(df) - 1

        current_time = df['time'].iloc[current_index]
        data_slice = df[df['time'] <= current_time]

        # Update trajectory plot
        traj_line.set_data(data_slice['lateral_distance'], data_slice['altitude'])
        plot_data = [
            [df['lateral_distance'].iloc[current_index]],
            [df['altitude'].iloc[current_index]]
        ]
        rocket_marker.set_data(plot_data)

        # Update time series plots
        alt_line.set_data(data_slice['time'], data_slice['altitude'])
        vel_line.set_data(data_slice['time'], data_slice['vertical_velocity'])
        acc_line.set_data(data_slice['time'], data_slice['vertical_acceleration'])

        # Update text annotation
        text_str = (
            f"Time: {current_time:.2f} s\n"
            f"Altitude: {df['altitude'].iloc[current_index]:.1f} m\n"
            f"Velocity: {df['vertical_velocity'].iloc[current_index]:.1f} m/s"
        )
        live_text.set_text(text_str)

        current_alt = df['altitude'].iloc[current_index]
        if current_alt > max_values["alt"]:
            max_values["alt"] = current_alt
            alt_max_text.set_text(f'Max: {max_values["alt"]:.1f} m')

        current_vel = df['vertical_velocity'].iloc[current_index]
        if current_vel > max_values["vel"]:
            max_values["vel"] = current_vel
            vel_max_text.set_text(f'Max: {max_values["vel"]:.1f} m/s')

        current_acc = df['vertical_acceleration'].iloc[current_index]
        if current_acc > max_values["acc"]:
            max_values["acc"] = current_acc
            acc_max_text.set_text(f'Max: {max_values["acc"]:.1f} m/s²')

        # Technically this is mandatory according to matplot
        # lib to keep animations from being collected by the python GC
        return (traj_line, rocket_marker, alt_line, vel_line, acc_line, live_text,
                alt_max_text, vel_max_text, acc_max_text)

    # --- 4. RUN THE ANIMATION ---
    # Calculate the total number of frames needed
    num_frames = len(df) // frame_step

    # This is necessary to keep python's garbage collector from claiming the animation
    ani = FuncAnimation(
        fig,
        update,
        frames=num_frames,
        init_func=init,
        blit=False,
        interval=frame_interval,
        repeat=repeat
    )

    plt.show()


def main():
    """Main function to parse arguments and launch the visualizer."""
    parser = argparse.ArgumentParser(description="Animate OpenRocket flight simulation data tool.")
    parser.add_argument("file", help="Path to the OpenRocket (.ork) file.")
    parser.add_argument(
        "--sim",
        type=int,
        default=1,
        help="The simulation number to visualize (1-based index). Default is 1.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Playback speed multiplier (e.g., 2 for 2x speed, 0.5 for half speed)"
             ". Default is 1.0.",
    )

    parser.add_argument(
        "--no-repeat",
        # This action stores False if the flag is present
        action="store_false",
        # The destination variable is still 'repeat'
        dest="repeat",
        help="Disable the animation from repeating when it finishes.",
    )

    args = parser.parse_args()

    # Load data using our library
    print(f"Loading simulations from {args.file}...")
    sims = load_simulations_from_xml(args.file)

    if not sims:
        print("Error: No simulations found in the specified file.")
        return

    if args.sim <= 0 or args.sim > len(sims):
        print(f"Error: Invalid simulation number. Please choose between 1 and {len(sims)}.")
        return

    selected_sim = sims[args.sim - 1]

    print(f"Starting visualization for '{selected_sim.name}' at {args.speed}x speed.")
    visualize_flight(selected_sim, args.speed, args.repeat)


if __name__ == "__main__":
    main()
