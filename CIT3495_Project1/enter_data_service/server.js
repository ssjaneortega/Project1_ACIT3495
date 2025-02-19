const express = require("express");
const mysql = require("mysql");
const app = express();

app.use(express.json());

const db = mysql.createConnection({
  host: "mysql_db",
  user: "user",
  password: "password",
  database: "analytics_db"
});

db.connect(err => {
  function connectWithRetry() {
  connection = mysql.createConnection({
    host: "mysql",
    user: "user",
    password: "password",
    database: "analytics_db"
  });

  connection.connect(err => {
    if (err) {
      console.error("MySQL connection failed, retrying in 5 seconds...");
      setTimeout(connectWithRetry, 5000);
    } else {
      console.log("Connected to MySQL");
    }
  });
}

connectWithRetry();

  console.log("Connected to MySQL");
});

app.post("/enter", (req, res) => {
  const { value } = req.body;
  db.query("INSERT INTO data (value) VALUES (?)", [value], (err) => {
    if (err) throw err;
    res.json({ message: "Data inserted" });
  });
});

app.listen(3001, () => console.log("Enter Data service running on port 3001"));
