// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

/**
 * Utility functions for the Express API demo.
 */

/**
 * Validate an email address format.
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
  if (typeof email !== "string") return false;
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}

/**
 * Slugify a string for use in URLs.
 * @param {string} text
 * @returns {string}
 */
function slugify(text) {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/**
 * Paginate an array of items.
 * @param {Array} items
 * @param {number} page - 1-indexed page number
 * @param {number} perPage - items per page
 * @returns {{ data: Array, total: number, page: number, totalPages: number }}
 */
function paginate(items, page = 1, perPage = 10) {
  if (!Array.isArray(items)) throw new Error("Items must be an array");
  if (page < 1) throw new Error("Page must be >= 1");
  if (perPage < 1) throw new Error("perPage must be >= 1");

  const total = items.length;
  const totalPages = Math.ceil(total / perPage);
  const start = (page - 1) * perPage;
  const data = items.slice(start, start + perPage);

  return { data, total, page, totalPages };
}

/**
 * Parse a duration string like "2h30m" into total seconds.
 * Supports h (hours), m (minutes), s (seconds).
 * @param {string} duration
 * @returns {number}
 */
function parseDuration(duration) {
  if (typeof duration !== "string" || duration.trim() === "") {
    throw new Error("Duration must be a non-empty string");
  }
  let totalSeconds = 0;
  const regex = /(\d+)(h|m|s)/g;
  let match;
  let matched = false;

  while ((match = regex.exec(duration)) !== null) {
    matched = true;
    const value = parseInt(match[1], 10);
    const unit = match[2];
    if (unit === "h") totalSeconds += value * 3600;
    else if (unit === "m") totalSeconds += value * 60;
    else if (unit === "s") totalSeconds += value;
  }

  if (!matched) throw new Error(`Invalid duration format: ${duration}`);
  return totalSeconds;
}

module.exports = { isValidEmail, slugify, paginate, parseDuration };
