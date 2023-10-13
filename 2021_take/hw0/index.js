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
const port = process.env.PORT || "9000";

/**
 *  App Configuration
 */

app.set("views", path.join(__dirname, "views"));
app.set("view engine", "pug");
app.use(exp.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
    // res.status(200).send("Hello World!");
    res.render("index", {title: "Home!"});
});
app.get("/user", (req, res) => {
    res.render("user", {
        title: "User!", 
        userProfile: {
            nickname: "Test Nickname"
        }
    });
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
