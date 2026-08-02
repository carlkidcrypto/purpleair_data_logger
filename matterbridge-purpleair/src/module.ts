import {
  type BasePlatformConfig,
  MatterbridgeDynamicPlatform,
  type MatterbridgeEndpoint,
  type PlatformMatterbridge,
} from "matterbridge";
import type { AnsiLogger } from "matterbridge/logger";

import { PurpleAirClient } from "./purpleair-client.js";
import {
  createPurpleAirEndpoint,
  purpleAirSerialNumber,
  updatePurpleAirEndpoint,
} from "./purpleair-endpoint.js";

export type PurpleAirPlatformConfig = BasePlatformConfig & {
  feedUrl?: string;
  pollIntervalSeconds?: number;
  requestTimeoutSeconds?: number;
  whiteList?: string[];
  blackList?: string[];
};

const DEFAULT_FEED_URL = "http://127.0.0.1:9855/matter/sensors";
const DEFAULT_POLL_INTERVAL_SECONDS = 60;
const DEFAULT_REQUEST_TIMEOUT_SECONDS = 10;

function positiveInteger(value: number | undefined, fallback: number, name: string): number {
  const resolved = value ?? fallback;
  if (!Number.isInteger(resolved) || resolved < 1)
    throw new Error(`${name} must be a positive integer`);
  return resolved;
}

export default function initializePlugin(
  matterbridge: PlatformMatterbridge,
  log: AnsiLogger,
  config: PurpleAirPlatformConfig,
): PurpleAirPlatform {
  return new PurpleAirPlatform(matterbridge, log, config);
}

export class PurpleAirPlatform extends MatterbridgeDynamicPlatform {
  private readonly client: PurpleAirClient;
  private readonly pollIntervalMs: number;
  private readonly endpoints = new Map<string, MatterbridgeEndpoint>();
  private pollTimer: NodeJS.Timeout | undefined;
  private polling = false;

  constructor(
    matterbridge: PlatformMatterbridge,
    log: AnsiLogger,
    config: PurpleAirPlatformConfig,
  ) {
    super(matterbridge, log, config);
    if (
      typeof this.verifyMatterbridgeVersion !== "function" ||
      !this.verifyMatterbridgeVersion("3.10.0")
    ) {
      throw new Error(
        `matterbridge-purpleair requires Matterbridge >= 3.10.0; found ${matterbridge.matterbridgeVersion}`,
      );
    }

    const pollIntervalSeconds = positiveInteger(
      config.pollIntervalSeconds,
      DEFAULT_POLL_INTERVAL_SECONDS,
      "pollIntervalSeconds",
    );
    const requestTimeoutSeconds = positiveInteger(
      config.requestTimeoutSeconds,
      DEFAULT_REQUEST_TIMEOUT_SECONDS,
      "requestTimeoutSeconds",
    );
    this.pollIntervalMs = pollIntervalSeconds * 1_000;
    this.client = new PurpleAirClient(
      config.feedUrl ?? DEFAULT_FEED_URL,
      requestTimeoutSeconds * 1_000,
    );
    this.log.info(
      `Configured PurpleAir feed ${config.feedUrl ?? DEFAULT_FEED_URL} with a ${pollIntervalSeconds}s poll interval`,
    );
  }

  override async onStart(reason?: string): Promise<void> {
    this.log.info(`Starting PurpleAir platform: ${reason ?? "no reason provided"}`);
    await this.ready;
    await this.clearSelect();
    await this.pollOnce();
    this.pollTimer = setInterval(() => void this.pollOnce(), this.pollIntervalMs);
  }

  override async onConfigure(): Promise<void> {
    await super.onConfigure();
    await this.pollOnce();
  }

  override async onShutdown(reason?: string): Promise<void> {
    if (this.pollTimer !== undefined) clearInterval(this.pollTimer);
    this.pollTimer = undefined;
    await super.onShutdown(reason);
    if (this.config.unregisterOnShutdown) await this.unregisterAllDevices();
  }

  private async pollOnce(): Promise<void> {
    if (this.polling || this.isShuttingDown) return;
    this.polling = true;
    try {
      const feed = await this.client.fetchReadings();
      for (const warning of feed.warnings) this.log.warn(`Ignored PurpleAir sensor: ${warning}`);

      for (const reading of feed.readings) {
        const existing = this.endpoints.get(reading.sensorIndex);
        if (existing !== undefined) {
          await updatePurpleAirEndpoint(existing, reading);
          continue;
        }

        const endpoint = createPurpleAirEndpoint(reading, this.matterbridge.aggregatorVendorId);
        const serialNumber = purpleAirSerialNumber(reading.sensorIndex);
        this.setSelectDevice(serialNumber, reading.sensorName);
        if (!this.validateDevice([reading.sensorName, serialNumber])) continue;
        await this.registerDevice(endpoint);
        this.endpoints.set(reading.sensorIndex, endpoint);
        this.log.info(`Registered PurpleAir sensor ${reading.sensorName} (${reading.sensorIndex})`);
      }
    } catch (error) {
      this.log.error(
        `PurpleAir poll failed; preserving last-known-good Matter values: ${error instanceof Error ? error.message : String(error)}`,
      );
    } finally {
      this.polling = false;
    }
  }
}
