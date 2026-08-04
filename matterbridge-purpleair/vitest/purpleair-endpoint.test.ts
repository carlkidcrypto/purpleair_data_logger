import { describe, expect, it, vi } from "vitest";

import { airQualitySensor } from "matterbridge";
import {
  AirQuality,
  Pm1ConcentrationMeasurement,
  Pm10ConcentrationMeasurement,
  Pm25ConcentrationMeasurement,
  PressureMeasurement,
  RelativeHumidityMeasurement,
  TemperatureMeasurement,
  TotalVolatileOrganicCompoundsConcentrationMeasurement,
} from "matterbridge/matter/clusters";

import type { PurpleAirReading } from "../src/purpleair-client.js";
import {
  createPurpleAirEndpoint,
  purpleAirDeviceName,
  purpleAirSerialNumber,
  updatePurpleAirEndpoint,
} from "../src/purpleair-endpoint.js";

const reading: PurpleAirReading = {
  sensorIndex: "123456",
  sensorName: "Back porch",
  firmwareVersion: "7.04",
  airQuality: 2,
  temperature: 2111,
  humidity: 3700,
  pressure: 926,
  pm1: 19.185,
  pm25: 24.405,
  pm10: 26.47,
  tvoc: 0.35,
};

describe("PurpleAir Matter endpoint", () => {
  it("uses the canonical Matter 1.6 Air Quality Sensor device type", () => {
    const endpoint = createPurpleAirEndpoint(reading, 0xfff1);

    expect(airQualitySensor.code).toBe(0x002c);
    expect(endpoint.getDeviceTypes()).toContainEqual(airQualitySensor);
    expect(endpoint.id).toBe("purpleair-123456");
    expect(endpoint.serialNumber).toBe("purpleair-123456");
  });

  it("creates the supported measurement clusters", () => {
    const endpoint = createPurpleAirEndpoint(reading, 0xfff1);

    for (const cluster of [
      AirQuality,
      TemperatureMeasurement,
      RelativeHumidityMeasurement,
      PressureMeasurement,
      Pm1ConcentrationMeasurement,
      Pm25ConcentrationMeasurement,
      Pm10ConcentrationMeasurement,
      TotalVolatileOrganicCompoundsConcentrationMeasurement,
    ]) {
      expect(endpoint.hasClusterServer(cluster)).toBe(true);
    }
  });

  it("omits TVOC when the source does not provide it", () => {
    const { tvoc: omittedTvoc, ...readingWithoutTvoc } = reading;
    expect(omittedTvoc).toBeDefined();
    const endpoint = createPurpleAirEndpoint(readingWithoutTvoc, 0xfff1);
    expect(endpoint.hasClusterServer(TotalVolatileOrganicCompoundsConcentrationMeasurement)).toBe(
      false,
    );
  });

  it("updates existing cluster attributes in place", async () => {
    const endpoint = createPurpleAirEndpoint(reading, 0xfff1);
    const updateSpy = vi.spyOn(endpoint, "updateAttribute").mockResolvedValue(true);
    await updatePurpleAirEndpoint(endpoint, {
      ...reading,
      airQuality: 4,
      temperature: 2200,
      pm25: 40.5,
    });

    expect(updateSpy).toHaveBeenCalledWith(AirQuality, "airQuality", 4);
    expect(updateSpy).toHaveBeenCalledWith(TemperatureMeasurement, "measuredValue", 2200);
    expect(updateSpy).toHaveBeenCalledWith(Pm25ConcentrationMeasurement, "measuredValue", 40.5);
  });

  it("derives a stable serial number from the sensor index", () => {
    expect(purpleAirSerialNumber("273450761757003")).toBe("purpleair-273450761757003");
  });

  it("uses the last three MAC octets in place of a raw MAC device name", () => {
    expect(purpleAirDeviceName("F8:B3:B7:84:A1:4B")).toBe("purple-air-84-a1-4b");
    expect(purpleAirDeviceName("Back porch")).toBe("Back porch");

    const endpoint = createPurpleAirEndpoint(
      { ...reading, sensorName: "F8:B3:B7:84:A1:4B" },
      0xfff1,
    );
    expect(endpoint.deviceName).toBe("purple-air-84-a1-4b");
  });
});
