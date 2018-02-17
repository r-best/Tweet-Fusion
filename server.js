const express = require('express');
const url = require('url');
const spawn = require('child_process').spawn;

const app = express()
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
})
app.get('/fusion', (req, res) => {
  let query = url.parse(req.url, true).query['test'];
  let pythonProc = spawn('python', ["./beep.py"].concat(query));
  pythonProc.stdout.on('data', (data)=>{
    res.send(data.toString());
  });
})
app.listen(3000, () => console.log('Server running on port 3000'))
