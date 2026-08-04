export interface PurpleAirReading {
  sensorIndex: string;
  sensorName: string;
  firmwareVersion?: string;
  hardwareModel?: string;
  airQuality: number;
  temperature?: number;
  humidity?: number;
  pressure?: number;
  pm1?: number;
  pm25?: number;
  pm10?: number;
  tvoc?: number;
}

export interface PurpleAirFeed {
  readings: PurpleAirReading[];
  warnings: string[];
}

type JsonObject = Record<string, unknown>;

function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function objectAt(value: unknown, path: string): JsonObject {
  if (!isObject(value)) throw new Error(`${path} must be an object`);
  return value;
}

function finiteNumber(value: unknown, path: string): number {
  if (typeof value !== "number" || !Number.isFinite(value))
    throw new Error(`${path} must be a finite number`);
  return value;
}

function optionalNumber(value: unknown, path: string): number | undefined {
  return value === undefined || value === null ? undefined : finiteNumber(value, path);
}

function optionalString(value: unknown, path: string): string | undefined {
  if (value === undefined || value === null) return undefined;
  if (typeof value !== "string") throw new Error(`${path} must be a string`);
  return value;
}

function attributes(clusters: JsonObject, clusterName: string): JsonObject | undefined {
  const cluster = clusters[clusterName];
  if (cluster === undefined) return undefined;
  return objectAt(
    objectAt(cluster, `device.clusters.${clusterName}`).attributes,
    `device.clusters.${clusterName}.attributes`,
  );
}

function concentration(
  attributesValue: unknown,
  rawValue: unknown,
  path: string,
): number | undefined {
  if (rawValue !== undefined && rawValue !== null) return finiteNumber(rawValue, `${path}._raw`);
  const scaled = optionalNumber(attributesValue, `${path}.attributes`);
  return scaled === undefined ? undefined : scaled / 100;
}

function withOptional<T extends string, V>(key: T, value: V | undefined): Partial<Record<T, V>> {
  return value === undefined ? {} : ({ [key]: value } as Record<T, V>);
}

function parseReading(value: unknown, position: number): PurpleAirReading {
  const itemPath = `sensors[${position}]`;
  const item = objectAt(value, itemPath);
  const sensorIndex = finiteNumber(item.sensor_index, `${itemPath}.sensor_index`);
  if (!Number.isSafeInteger(sensorIndex) || sensorIndex < 0) {
    throw new Error(`${itemPath}.sensor_index must be a non-negative safe integer`);
  }

  const device = objectAt(item.device, `${itemPath}.device`);
  const clusters = objectAt(device.clusters, `${itemPath}.device.clusters`);
  const air = attributes(clusters, "air_quality_measurement");
  if (air === undefined)
    throw new Error(`${itemPath}.device.clusters.air_quality_measurement is required`);

  const airQuality = finiteNumber(
    air.airQuality,
    `${itemPath}.device.clusters.air_quality_measurement.attributes.airQuality`,
  );
  if (!Number.isInteger(airQuality) || airQuality < 0 || airQuality > 6) {
    throw new Error(`${itemPath}.airQuality must be an integer from 0 through 6`);
  }

  const airCluster = objectAt(
    clusters.air_quality_measurement,
    `${itemPath}.device.clusters.air_quality_measurement`,
  );
  const raw =
    airCluster._raw === undefined
      ? {}
      : objectAt(airCluster._raw, `${itemPath}.device.clusters.air_quality_measurement._raw`);
  const temperature = attributes(clusters, "temperature_measurement");
  const humidity = attributes(clusters, "humidity_measurement");
  const pressure = attributes(clusters, "pressure_measurement");
  const sensorName =
    optionalString(device.sensor_name, `${itemPath}.device.sensor_name`) ??
    `PurpleAir ${sensorIndex}`;

  return {
    sensorIndex: String(sensorIndex),
    sensorName,
    ...withOptional(
      "firmwareVersion",
      optionalString(device.firmware_version, `${itemPath}.device.firmware_version`),
    ),
    ...withOptional(
      "hardwareModel",
      optionalString(device.hardware_model, `${itemPath}.device.hardware_model`),
    ),
    airQuality,
    ...withOptional(
      "temperature",
      optionalNumber(temperature?.measuredValue, `${itemPath}.temperature.measuredValue`),
    ),
    ...withOptional(
      "humidity",
      optionalNumber(humidity?.measuredValue, `${itemPath}.humidity.measuredValue`),
    ),
    ...withOptional(
      "pressure",
      optionalNumber(pressure?.measuredValue, `${itemPath}.pressure.measuredValue`),
    ),
    ...withOptional("pm1", concentration(air.pm1Density, raw.pm1_ug_m3, `${itemPath}.pm1`)),
    ...withOptional("pm25", concentration(air.measuredValue, raw.pm25_ug_m3, `${itemPath}.pm25`)),
    ...withOptional("pm10", concentration(air.pm10Density, raw.pm10_ug_m3, `${itemPath}.pm10`)),
    ...withOptional("tvoc", concentration(air.vocDensity, raw.voc_ug_m3, `${itemPath}.tvoc`)),
  };
}

export function parsePurpleAirFeed(value: unknown): PurpleAirFeed {
  const root = objectAt(value, "response");
  if (!Array.isArray(root.sensors)) throw new Error("response.sensors must be an array");

  const readings: PurpleAirReading[] = [];
  const warnings: string[] = [];
  const seen = new Set<string>();
  for (const [position, sensor] of root.sensors.entries()) {
    try {
      const reading = parseReading(sensor, position);
      if (seen.has(reading.sensorIndex))
        throw new Error(`duplicate sensor_index ${reading.sensorIndex}`);
      seen.add(reading.sensorIndex);
      readings.push(reading);
    } catch (error) {
      warnings.push(error instanceof Error ? error.message : String(error));
    }
  }
  return { readings, warnings };
}

export class PurpleAirClient {
  constructor(
    private readonly feedUrl: string,
    private readonly timeoutMs: number,
    private readonly fetcher: typeof fetch = fetch,
  ) {
    const protocol = new URL(feedUrl).protocol;
    if (protocol !== "http:" && protocol !== "https:")
      throw new Error("feedUrl must use HTTP or HTTPS");
    if (!Number.isInteger(timeoutMs) || timeoutMs < 1)
      throw new Error("timeoutMs must be a positive integer");
  }

  async fetchReadings(): Promise<PurpleAirFeed> {
    const response = await this.fetcher(this.feedUrl, {
      signal: AbortSignal.timeout(this.timeoutMs),
    });
    if (!response.ok) throw new Error(`PurpleAir feed returned HTTP ${response.status}`);
    return parsePurpleAirFeed(await response.json());
  }
}
