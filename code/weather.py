import bme680 as bm


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


def main():
    import time

    print(
        """ Make sure Grove-Temperature-Humidity-Press-Gas-Sensor(BME680)
   inserted in one I2C slot of Grove-Base-Hat
"""
    )

    sensor = GroveBME680()

    print("Temperature, Pressure, Humidity, Gas")
    while True:
        data = sensor.read()
        if data:
            fmt = "{0:.2f} C, {1:.2f} hPa, {2:.2f} %RH".format(
                data.temperature, data.pressure, data.humidity
            )
            if data.heat_stable:
                fmt += " {1} Ohms".format(fmt, data.gas_resistance)
            print(fmt)
        time.sleep(1)


if __name__ == "__main__":
    main()
