"use strict";
/**
 * Backward-compatible seed review CLI. Python's shared MCM merger preserves
 * source formatting and checks hashes; no installed files are modified.
 * node tools/build_mcm_ini_review_output.js --workspace PATH --output NEW_PATH
 */
const path = require("path");
const { spawnSync } = require("child_process");
const result = spawnSync("python", [
  path.join(__dirname, "review_mcm_ini.py"), "seed", ...process.argv.slice(2)
], { stdio: "inherit" });
if (result.error) throw result.error;
process.exit(result.status === null ? 1 : result.status);
