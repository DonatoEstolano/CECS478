// Packages
var express = require('express'),
    app = express(),
    port = process.env.PORT || 3000,
    mongoose = require('mongoose'),
    ChatApp = require('./api/models/478model'),
    morgan = require('morgan'),
    config = require('./config'),
    bodyParser = require('body-parser');

// Configurations
mongoose.Promise = global.Promise;
mongoose.connect(config.database, function(err) {
	Console.log(err);
});
app.set('secretpassword', config.secret)

app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());

app.use(morgan('dev'));

app.get('/', function(req, res) {
    res.send('Owned by DC Security!');
});

var routes = require('./api/routes/478routes');
routes(app);

app.listen(port);

console.log('478 Chat App RESTful API server started on: ' + port);

app.use(function(req, res) {
    res.status(404).send({url: req.originalUrl + ' not found'});
  });
