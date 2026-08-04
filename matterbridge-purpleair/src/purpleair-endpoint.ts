import { MatterbridgeEndpoint, airQualitySensor } from "matterbridge";
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

import type { PurpleAirReading } from "./purpleair-client.js";

const MAC_ADDRESS_PATTERN = /^(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}$/i;

export function purpleAirDeviceName(sensorName: string): string {
  if (!MAC_ADDRESS_PATTERN.test(sensorName)) return sensorName;
  return `purple-air-${sensorName.toLowerCase().split(/[:-]/).slice(-3).join("-")}`;
}

export function purpleAirSerialNumber(sensorIndex: string): string {
  return `purpleair-${sensorIndex}`;
}

export function createPurpleAirEndpoint(
  reading: PurpleAirReading,
  vendorId: number,
): MatterbridgeEndpoint {
  const deviceName = purpleAirDeviceName(reading.sensorName);
  const serialNumber = purpleAirSerialNumber(reading.sensorIndex);
  const endpoint = new MatterbridgeEndpoint(airQualitySensor, { id: serialNumber })
    .createDefaultBridgedDeviceBasicInformationClusterServer(
      deviceName,
      serialNumber,
      vendorId,
      "PurpleAir",
      "PurpleAir Air Quality Sensor",
      undefined,
      reading.firmwareVersion,
    )
    .createDefaultAirQualityClusterServer(reading.airQuality as AirQuality.AirQualityEnum)
    .createDefaultTemperatureMeasurementClusterServer(reading.temperature ?? null)
    .createDefaultRelativeHumidityMeasurementClusterServer(reading.humidity ?? null)
    .createDefaultPressureMeasurementClusterServer(reading.pressure ?? null)
    .createDefaultPm1ConcentrationMeasurementClusterServer(reading.pm1 ?? null)
    .createDefaultPm25ConcentrationMeasurementClusterServer(reading.pm25 ?? null)
    .createDefaultPm10ConcentrationMeasurementClusterServer(reading.pm10 ?? null);

  if (reading.tvoc !== undefined) endpoint.createDefaultTvocMeasurementClusterServer(reading.tvoc);
  return endpoint.addRequiredClusters();
}

export async function updatePurpleAirEndpoint(
  endpoint: MatterbridgeEndpoint,
  reading: PurpleAirReading,
): Promise<void> {
  const updates: Promise<boolean>[] = [
    endpoint.updateAttribute(
      AirQuality,
      "airQuality",
      reading.airQuality as AirQuality.AirQualityEnum,
    ),
  ];

  if (reading.temperature !== undefined)
    updates.push(
      endpoint.updateAttribute(TemperatureMeasurement, "measuredValue", reading.temperature),
    );
  if (reading.humidity !== undefined)
    updates.push(
      endpoint.updateAttribute(RelativeHumidityMeasurement, "measuredValue", reading.humidity),
    );
  if (reading.pressure !== undefined)
    updates.push(endpoint.updateAttribute(PressureMeasurement, "measuredValue", reading.pressure));
  if (reading.pm1 !== undefined)
    updates.push(
      endpoint.updateAttribute(Pm1ConcentrationMeasurement, "measuredValue", reading.pm1),
    );
  if (reading.pm25 !== undefined)
    updates.push(
      endpoint.updateAttribute(Pm25ConcentrationMeasurement, "measuredValue", reading.pm25),
    );
  if (reading.pm10 !== undefined)
    updates.push(
      endpoint.updateAttribute(Pm10ConcentrationMeasurement, "measuredValue", reading.pm10),
    );
  if (
    reading.tvoc !== undefined &&
    endpoint.hasClusterServer(TotalVolatileOrganicCompoundsConcentrationMeasurement)
  ) {
    updates.push(
      endpoint.updateAttribute(
        TotalVolatileOrganicCompoundsConcentrationMeasurement,
        "measuredValue",
        reading.tvoc,
      ),
    );
  }

  await Promise.all(updates);
}
