const express = require("express");
const { MongoClient } = require("mongodb");

const app = express();
const url = "mongodb://mongo_db:27017";
const client = new MongoClient(url);

app.get("/results", async (req, res) => {
  await client.connect();
  const db = client.db("analytics");
  const results = await db.collection("stats").find().toArray();
  res.json(results);
});

app.listen(3002, () => console.log("Show Results service running on port 3002"));
