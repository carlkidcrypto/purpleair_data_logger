import { describe, expect, it, vi } from "vitest";

import { PurpleAirClient, parsePurpleAirFeed } from "../src/purpleair-client.js";

function sensor(sensorIndex = 123456): Record<string, unknown> {
  return {
    sensor_index: sensorIndex,
    device: {
      sensor_name: "Back porch",
      firmware_version: "7.04",
      hardware_model: "BME68X+PMSX003",
      clusters: {
        air_quality_measurement: {
          attributes: {
            measuredValue: 2440,
            pm1Density: 1919,
            pm10Density: 2647,
            vocDensity: 35,
            airQuality: 2,
          },
          _raw: { pm25_ug_m3: 24.405, pm1_ug_m3: 19.185, pm10_ug_m3: 26.47, voc_ug_m3: 0.35 },
        },
        temperature_measurement: { attributes: { measuredValue: 2111 } },
        humidity_measurement: { attributes: { measuredValue: 3700 } },
        pressure_measurement: { attributes: { measuredValue: 926 } },
      },
    },
  };
}

describe("parsePurpleAirFeed", () => {
  it("normalizes the live feed representation", () => {
    const result = parsePurpleAirFeed({ sensors: [sensor()], count: 1 });
    expect(result.warnings).toEqual([]);
    expect(result.readings).toEqual([
      {
        sensorIndex: "123456",
        sensorName: "Back porch",
        firmwareVersion: "7.04",
        hardwareModel: "BME68X+PMSX003",
        airQuality: 2,
        temperature: 2111,
        humidity: 3700,
        pressure: 926,
        pm1: 19.185,
        pm25: 24.405,
        pm10: 26.47,
        tvoc: 0.35,
      },
    ]);
  });

  it("falls back to scaled concentration attributes when raw values are absent", () => {
    const payload = sensor();
    const device = payload.device as Record<string, unknown>;
    const clusters = device.clusters as Record<string, Record<string, unknown>>;
    delete clusters.air_quality_measurement?._raw;
    const [reading] = parsePurpleAirFeed({ sensors: [payload] }).readings;
    expect(reading).toMatchObject({ pm1: 19.19, pm25: 24.4, pm10: 26.47, tvoc: 0.35 });
  });

  it("keeps valid sensors when another sensor is malformed", () => {
    const result = parsePurpleAirFeed({ sensors: [{ sensor_index: "bad" }, sensor()] });
    expect(result.readings).toHaveLength(1);
    expect(result.warnings).toHaveLength(1);
  });

  it("rejects duplicate stable sensor identities", () => {
    const result = parsePurpleAirFeed({ sensors: [sensor(), sensor()] });
    expect(result.readings).toHaveLength(1);
    expect(result.warnings[0]).toContain("duplicate sensor_index");
  });
});

describe("PurpleAirClient", () => {
  it("fetches and parses readings", async () => {
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValue(new Response(JSON.stringify({ sensors: [sensor()] }), { status: 200 }));
    const client = new PurpleAirClient("http://127.0.0.1:9855/matter/sensors", 1_000, fetcher);
    await expect(client.fetchReadings()).resolves.toMatchObject({
      readings: [{ sensorIndex: "123456" }],
    });
    expect(fetcher).toHaveBeenCalledOnce();
  });

  it("reports an unsuccessful HTTP response", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(new Response(null, { status: 503 }));
    const client = new PurpleAirClient("http://127.0.0.1:9855/matter/sensors", 1_000, fetcher);
    await expect(client.fetchReadings()).rejects.toThrow("HTTP 503");
  });
});
