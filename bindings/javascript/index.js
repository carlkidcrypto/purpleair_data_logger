"use strict";

const path = require("path");
const fs = require("fs");

const candidates = [
  path.join(__dirname, "build", "Release", "purpleair_data_logger.node"),
  path.join(__dirname, "prebuilds", `${process.platform}-${process.arch}`, "purpleair_data_logger.node"),
];

let addon = null;
for (const candidate of candidates) {
  if (fs.existsSync(candidate)) {
    addon = require(candidate);
    break;
  }
}

if (!addon) {
  throw new Error(
    "purpleair_data_logger native N-API addon not built yet. Run `npm run build` in bindings/javascript."
  );
}

module.exports = addon;
