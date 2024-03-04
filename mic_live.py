import queue
import sys
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

# Parameters
CHANNELS = 1
RATE = 44100
CHUNK = 1024
INTERVAL = 30  # milliseconds

q = queue.Queue()


def callback(indata, frames, time, status):
    # This is called (from a separate thread) for each audio block.
    if status:
        print(status, file=sys.stderr)

    q.put(np.frombuffer(indata, dtype=np.int16))


plt.style.use('dark_background')

Y_LIMIT = [0, 5]
CONTROL_FACTOR = 0.001
X_LIMIT = [0, 100]

# def y_function(x, t): return np.max(x)//2


def y_function(x, t): return np.sin(2 * np.pi * 10 * t) + np.max(x)*CONTROL_FACTOR


def data_gen():
    try:
        with sd.RawInputStream(blocksize=8000,
                               dtype="int16", channels=1, callback=callback):

            print("#" * 80)
            print("Press Ctrl+C to stop the recording")
            print("#" * 80)

            t = 0
            while True:
                data = q.get()
                # Add here!!!
                yield (t, y_function(data, t))
                t += 1

    except KeyboardInterrupt:
        print("\nDone")
        exit(0)
    except Exception as e:
        print(type(e).__name__ + ": " + str(e))
        exit(-1)


fig, axes = plt.subplots()
line, = axes.plot([], [], lw=2)
axes.grid()
plt.xlabel('Time')
plt.ylabel('Volume')
xdata, ydata = [], []


def init():
    """This function will be called once before the FIRST frame."""
    axes.set_ylim(Y_LIMIT[0], Y_LIMIT[1])
    axes.set_xlim(X_LIMIT[0], X_LIMIT[1])
    line.set_data(xdata, ydata)
    return line,


def run(data):
    """Called after getting output from data_gen"""
    global xdata, ydata
    _time, y_output = data
    y_output = round(y_output, 4)

    print(f'\tx={_time} \t y={y_output}')
    xdata.append(_time)
    ydata.append(y_output)

    xmin, xmax = axes.get_xlim()

    # Shift the x-axis ahead.
    if _time >= xmax:
        # Redraw with shifted time.
        xdata, ydata = xdata[-1:], ydata[-1:]
        diff = xmax - xmin
        axes.set_xlim(xmax, xmax+diff)
        axes.figure.canvas.draw()

    line.set_data(xdata, ydata)

    return line,


# Only save last 10 frames, but run forever
ani = animation.FuncAnimation(fig, run, data_gen, interval=0, init_func=init,
                              save_count=10)
plt.show()


# for data in data_gen():
#     t, out = data
#     print('\t\t\t',round(y_function(out, t), 4))
