// index.js

/**
 * Required External Modules
 */

const exp = require("express");
const path = require("path");

/**
 * App Variables
 */

const app = exp();
const port = process.env.PORT || "8080";

/**
 *  App Configuration
 */

app.get("/", (req, res) => {
    res.status(200).send("Hello World!");
});

/**
 * Routes Definitions
 */

/**
 * Server Activation
 */

app.listen(port, () => {
    console.log(`Listening at http://localhost:${port}`);
});
