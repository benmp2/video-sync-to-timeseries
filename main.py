import pandas as pd
import numpy as np
from matplotvideo import attach_video_player_to_figure
import matplotlib
import matplotlib.pyplot as plt
from typing import List


def move_figure(f, x, y):
    """
    Move figure's upper left corner to pixel (x, y)
    """

    backend = matplotlib.get_backend()
    if backend == "TkAgg":
        f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
    elif backend == "WXAgg":
        f.canvas.manager.window.SetPosition((x, y))
    else:
        # This works for QT and GTK
        # You can also use window.setGeometry
        f.canvas.manager.window.move(x, y)


def magnitude_highpass(
    df: pd.DataFrame, axes: List = ["x", "y", "z"], window_size: str = "3s"
) -> np.array:
    """

    Parameters
    ----------
    df              input pd.Dataframe
    axes            axes to include in magnitude highpass calculation
    window_size     size of rolling window, e.g. 3 or '3s'

    Returns         np.array of magnitude highpass values
    -------

    """

    mhp = df[axes].values - df[axes].rolling(window=window_size).mean().values
    # magnitude calculation:
    mhp = np.sqrt(np.sum(np.power(mhp, 2), axis=1))

    return mhp


def on_frame(video_timestamp, line, data):

    timestamps, y = zip(*data)
    x = [timestamp - video_timestamp for timestamp in timestamps]

    line.set_data(x, y)
    line.axes.relim()
    line.axes.autoscale_view()
    line.axes.figure.canvas.draw()


def main(video_fname="20210518_121715_test_sync.mp4", chart_data=None):
    px = 1 / plt.rcParams["figure.dpi"]
    fig, ax = plt.subplots(figsize=(540 * px, 480 * px))
    move_figure(fig, 5, 5)
    plt.xlim(-15, 15)
    plt.axvline(x=0, color="k", linestyle="--")

    (line,) = ax.plot([], [], color="blue")

    attach_video_player_to_figure(
        fig, video_fname, on_frame, line=line, data=chart_data
    )

    plt.show()


if __name__ == "__main__":

    ##################################################################################################
    #### Gerber GTXL
    ##########
    video_fname = "VID_20210514_105349.mp4"
    accelerations = "survey_f5532950-8755-11eb-b76b-db4f33ef4bfb_accelerations.csv"

    df = pd.read_csv(accelerations, sep=",")
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%dT%H:%M:%S.%f")
    df = df.set_index("timestamp")

    # df = df.loc[
    #     "2021-05-14 10:53:49":"2021-05-14 10:58:06"
    # ]
    df = df.loc["2021-05-14 10:49:32":"2021-05-14 10:53:49"]

    df["mhp"] = df.y  # magnitude_highpass(df)  # df.x  # magnitude_highpass(df)
    # df["mhp"] = (
    #     df["mhp"].rolling(15, center=True, win_type="gaussian").mean(std=5).fillna(0)
    # )
    #################################################################################################

    #################################################################################################
    ### testing sync in hubhub
    ###########
    # video_fname="20210518_121715_test_sync.mp4"
    # accelerations = "survey_test_sync.csv"
    # df = pd.read_csv(accelerations, sep=",")
    # df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%dT%H:%M:%S.%f")
    # df = df.set_index("timestamp")

    # df = df.loc["2021-05-18 12:17:15":"2021-05-18 12:18:26"]

    # df["mhp"] = magnitude_highpass(df) # df.y  # magnitude_highpass(df)

    #################################################################################################

    # reset timestamp:
    df["ts"] = df.index - df.index[0]  # - pd.Timedelta(2, unit="s")
    df["ts"] = df["ts"].dt.total_seconds()
    df = df.round(3)
    df = df.set_index("ts")

    # # (timestamp, value) pairs
    data = list(zip(df.index, df.mhp))

    main(video_fname, data)
