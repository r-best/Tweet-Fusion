const express = require('express');
const url = require('url');
const spawn = require('child_process').spawn;
const path = require('path');

const app = express()
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
})
app.get('/fusion', (req, res) => {
  let query = url.parse(req.url, true).query['user'];
  let pythonProc = spawn('python', ["./bot.py"].concat(query));

  let generatedTweets = "";

  pythonProc.stdout.on('data', (data)=>{
    if(data.includes("<ENDOFOUTPUT>")){
      generatedTweets += data.toString().replace("<ENDOFOUTPUT>", "");
      res.send(generatedTweets);
    }
    else
      generatedTweets += data.toString();
  });
})
app.listen(3000, () => console.log('Server running on port 3000'))
