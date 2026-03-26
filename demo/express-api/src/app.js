// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

const express = require("express");
const { isValidEmail, slugify, paginate } = require("./utils");

const app = express();
app.use(express.json());

const items = [];

app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

app.post("/items", (req, res) => {
  const { name, email } = req.body;
  if (!name || typeof name !== "string") {
    return res.status(400).json({ error: "Name is required" });
  }
  if (email && !isValidEmail(email)) {
    return res.status(400).json({ error: "Invalid email format" });
  }
  const item = { id: items.length + 1, name, slug: slugify(name), email };
  items.push(item);
  res.status(201).json(item);
});

app.get("/items", (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const perPage = parseInt(req.query.per_page) || 10;
  const result = paginate(items, page, perPage);
  res.json(result);
});

app.get("/items/:id", (req, res) => {
  const item = items.find((i) => i.id === parseInt(req.params.id));
  if (!item) return res.status(404).json({ error: "Item not found" });
  res.json(item);
});

if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
}

module.exports = app;
