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


def airQuality(data, gas_baseline):
    air_quality_score = None
    # Set the humidity baseline to 40%, an optimal indoor humidity.
    hum_baseline = 40.0

    # This sets the balance between humidity and gas reading in the
    # calculation of air_quality_score (25:75, humidity:gas)
    hum_weighting = 0.25

    if data and data.heat_stable:
        print("hooopla")
        print(data)
        print(data.heat_stable)

        gas = data.gas_resistance
        gas_offset = gas_baseline - gas

        hum = data.humidity
        hum_offset = hum - hum_baseline

        # Calculate hum_score as the distance from the hum_baseline.
        if hum_offset > 0:
            hum_score = 100 - hum_baseline - hum_offset
            hum_score /= 100 - hum_baseline
            hum_score *= hum_weighting * 100

        else:
            hum_score = hum_baseline + hum_offset
            hum_score /= hum_baseline
            hum_score *= hum_weighting * 100

        # Calculate gas_score as the distance from the gas_baseline.
        if gas_offset > 0:
            gas_score = gas / gas_baseline
            gas_score *= 100 - (hum_weighting * 100)

        else:
            gas_score = 100 - (hum_weighting * 100)

        # Calculate air_quality_score.
        air_quality_score = hum_score + gas_score

        # print(
        #     "Gas: {0:.2f} Ohms,humidity: {1:.2f} %RH,air quality: {2:.2f}".format(
        #         gas, hum, air_quality_score
        #     )
        # )

        time.sleep(0.3)

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
        curr = start_time + (time.time() - start_time)
        tempF = (data.temperature * 9 / 5) + 32
        aqi = airQuality(sensor, gas_baseline)
        print("AQI is", aqi)

        x.append(curr)
        y["temp"].append(tempF)
        y["pressure"].append(data.pressure)
        y["humidity"].append(data.humidity)
        y["gas"].append(data.gas_resistance)

        print(
            f"temperature : {data.temperature}, pressure : {data.pressure}, humidity : {data.humidity}, gas : {data.gas_resistance}"
        )
        y["airQuality"].append(aqi)

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

        print(x, y)
        tempPlot.plot(x, y["temp"], "r")
        pressurePlot.plot(x, y["pressure"], "g")
        humidityPlot.plot(x, y["humidity"], "b")
        gasPlot.plot(x, y["gas"], "k")
        airQualityPlot.plot(x, y["airQuality"], "g")


fig = plt.figure(tight_layout=True)
fig.suptitle("Weather Station Data")
tempPlot = fig.add_subplot(231)
pressurePlot = fig.add_subplot(232)
humidityPlot = fig.add_subplot(233)
gasPlot = fig.add_subplot(234)
airQualityPlot = fig.add_subplot(235)


tempPlot.set_title("Temperature (°C) vs Time (s)")
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

# start_time = time.time()
# curr_time = time.time()
# burn_in_time = 300
# burn_in_data = []

# print("Collecting gas resistance burn-in data for close to 5 mins\n")
# while (curr_time - start_time) < burn_in_time:
#     curr_time = time.time()
#     data = sensor.read()
#     if data and data.heat_stable:
#         gas = data.gas_resistance
#         burn_in_data.append(gas)
#         print("Gas: {0} Ohms".format(gas))
#         time.sleep(1)

# # check that 50 still happens; else just lower
# gas_baseline = sum(burn_in_data[-50:]) / 50.0

# measured in Roy's Laboratory
gas_baseline = 127964.22104496269
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
