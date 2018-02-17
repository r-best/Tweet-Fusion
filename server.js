const url = require('url');
const spawn = require('child_process').spawn;
const path = require('path');
const express = require('express');

const app = express();
app.set(`view engine`, `pug`);

app.get('/', (req, res) => {
    res.redirect("/home");
});

app.get('/home', (req, res) => {
    res.render(`index`);
});

app.get('/fusion', (req, res) => {
    let query = url.parse(req.url, true).query['user'];
    let pythonProc = spawn('python', ["./bot.py"].concat(query));

    let generatedTweets = "";

    pythonProc.stdout.on('data', (data)=>{
        if(data.includes("<ENDOFOUTPUT>")){
            generatedTweets += data.toString().replace("<ENDOFOUTPUT>", "");
            res.render(`fusion`, { tweets: generatedTweets.split(/\n+/) });
        }
        else
            generatedTweets += data.toString();
    });
    pythonProc.stderr.on('data', (data)=>{
        res.render(`error`, { message: `Error: ${data}` });
    });
    pythonProc.on('error', (err)=>{
        res.render(`error`, { message: `Error in child process: ${err}` });
    });
});

app.listen(process.env.npm_package_config_port, 
    () => console.log(`Server listening on port ${process.env.npm_package_config_port}`));