from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import bme680 as bm
import time


class GroveBME680(object):
    def __init__(self):
        snr = bm.BME680(bm.I2C_ADDR_PRIMARY)

        # over sample, make data more accuracy
        snr.set_humidity_oversample(bm.OS_2X)
        snr.set_pressure_oversample(bm.OS_4X)
        snr.set_temperature_oversample(bm.OS_8X)
        snr.set_filter(bm.FILTER_SIZE_3)
        snr.set_gas_status(bm.ENABLE_GAS_MEAS)

        # profile # 0
        snr.set_gas_heater_temperature(320)
        snr.set_gas_heater_duration(150)
        snr.select_gas_heater_profile(0)

        # profile # 1
        # snr.set_gas_heater_profile(200, 150, nb_profile=1)
        # snr.select_gas_heater_profile(1)

        # Initial reading
        snr.get_sensor_data()
        snr.get_sensor_data()

        self.snr = snr

    def read(self):
        if self.snr.get_sensor_data():
            return self.snr.data
        return None

    def calculateGasBaseline(self, skip=True):
        if skip:
            # measured in Roy's Laboratory
            gas_baseline = 127964.22104496269
            return gas_baseline

        start_time = time.time()
        curr_time = time.time()
        burn_in_time = 75
        burn_in_data = []

        print("Collecting gas resistance burn-in data for close to 5 mins\n")
        while (curr_time - start_time) < burn_in_time:
            curr_time = time.time()
            data = sensor.read()
            if data and data.heat_stable:
                gas = data.gas_resistance
                burn_in_data.append(gas)
                print("Gas: {0} Ohms".format(gas))
                time.sleep(0.5)

        # check that 50 still happens; else just lower
        gas_baseline = sum(burn_in_data[-50:]) / 50.0

        return gas_baseline

    def airQuality(self, data, gas_baseline):
        air_quality_score = None
        humScore = None
        humReference = 40

        humidity = data.humidity

        if humidity >= 38 and humidity <= 42:
            humScore = 0.25 * 100
        elif humidity < 38:
            humScore = 0.25 / humReference * humidity * 100
        else:
            humScore = ((-0.25 / (100 - humReference) * humidity) + 0.416666) * 100

        gasLower = 5000
        gasUpper = 50000
        if gas_baseline > gasUpper:
            gas_baseline = gasUpper
        else:
            gas_baseline = gasLower

        gasScore = (
            0.75 / (gasUpper - gasLower) * gas_baseline
            - (gasLower * (0.75 / (gasUpper - gasLower)))
        ) * 100

        if gasScore > 75:
            gasScore = 75
        if gasScore < 0:
            gasScore = 0

        air_quality_score = humScore + gasScore

        return air_quality_score


def animate(
    i,
    sensor,
    tempPlot,
    pressurePlot,
    humidityPlot,
    gasPlot,
    airQualityPlot,
    x,
    y,
    gas_baseline,
    start_time,
):
    # read temp from grove sensor
    data = sensor.read()

    if data and data.heat_stable:
        # append data to x and y lists
        curr = time.time() - start_time
        # default temperature offset due to heat produced by components
        tempOffset = 5
        tempF = ((data.temperature - tempOffset) * 9 / 5) + 32

        aqi = sensor.airQuality(data, gas_baseline)

        x.append(curr)
        y["temp"].append(tempF)
        y["pressure"].append(data.pressure)
        y["humidity"].append(data.humidity)
        y["gas"].append(data.gas_resistance)
        y["airQuality"].append(aqi)

        print(
            f"temperature : {data.temperature}, pressure : {data.pressure}, humidity : {data.humidity}, gas : {data.gas_resistance}, airQuality : {aqi}"
        )

        # limit x and y axis to 20 items to plot
        x = x[-20:]
        y["temp"] = y["temp"][-20:]
        y["pressure"] = y["pressure"][-20:]
        y["humidity"] = y["humidity"][-20:]
        y["gas"] = y["gas"][-20:]
        y["airQuality"] = y["airQuality"][-20:]

        # test uncomment
        # tempPlot.clear()
        # pressurePlot.clear()
        # humidityPlot.clear()
        # gasPlot.clear()

        tempPlot.plot(x, y["temp"], "r")
        pressurePlot.plot(x, y["pressure"], "g")
        humidityPlot.plot(x, y["humidity"], "b")
        gasPlot.plot(x, y["gas"], "k")
        airQualityPlot.plot(x, y["airQuality"], "g")


fig = plt.figure(tight_layout=True)
plt.style.use("seaborn-darkgrid")
fig.suptitle("Weather Station Data")
tempPlot = fig.add_subplot(231)
pressurePlot = fig.add_subplot(232)
humidityPlot = fig.add_subplot(233)
gasPlot = fig.add_subplot(234)
airQualityPlot = fig.add_subplot(235)


tempPlot.set_title("Temperature (°F) vs Time (s)")
pressurePlot.set_title("Pressure (hPa) vs Time (s)")
humidityPlot.set_title("Humidity (%RH) vs Time (s)")
gasPlot.set_title("Gas Resistance (Ω) vs Time (s)")
airQualityPlot.set_title("Air Quality Index vs Time (s)")

# atmospheric pressure at sealevel for reference
pressurePlot.axhline(y=1013.25, color="blue")
pressurePlot.legend(["Pressure at Sea Level", "Current Pressure"])
# optimal inddor humidy level for reference
humidityPlot.axhline(y=40, color="g")
humidityPlot.legend(["Optimal Indoor Humidity", "Current Humidity"])
# x is time
x = []
# y is dictionary of different y values depending on the subplot
y = {"temp": [], "pressure": [], "humidity": [], "gas": [], "airQuality": []}

sensor = GroveBME680()

# default skip value is true; set to false for debugging outside of roy's lab
gas_baseline = sensor.calculateGasBaseline()

start_time = time.time()
ani = animation.FuncAnimation(
    fig,
    animate,
    fargs=(
        sensor,
        tempPlot,
        pressurePlot,
        humidityPlot,
        gasPlot,
        airQualityPlot,
        x,
        y,
        gas_baseline,
        start_time,
    ),
    interval=500,
    cache_frame_data=False,
)
plt.show()
