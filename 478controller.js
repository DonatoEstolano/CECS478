'use strict';

var mongoose = require('mongoose'),
    jwt = require('jsonwebtoken'),
    bcrypt = require('bcryptjs'),
    config = require('../../config'),
    User = mongoose.model('Users'),
    Message = mongoose.model('Messages');

exports.list_users = function(req, res) {
    User.find({}, function(err, user) {
        if(err)
            res.send(err);
        res.json(user);
    });
};

exports.list_messages = function(req, res) {
    Message.find({}, function(err, msg) {
        if(err)
            res.send(err);
        res.json(msg);
    });
};

/*
exports.get_me = function(req, res) {
    var token = req.headers['x-access-token'];
  if (!token) return res.status(401).send({ auth: false, message: 'No token provided.' });
  
  jwt.verify(token, config.secret, function(err, decoded) {
    if (err) return res.status(500).send({ auth: false, message: 'Failed to authenticate token.' });
    
    User.findById(decoded.id, function (err, user) {
        if (err) return res.status(500).send("There was a problem finding the user.");
        if (!user) return res.status(404).send("No user found.");
        
        res.status(200).send(user);
      });
  });
};
*/

exports.create_user = function(req, res) {
    var salt = bcrypt.genSaltSync(10)
    var hashedPassword = bcrypt.hashSync(req.body.password, salt);

    User.create({
        username: req.body.username,
        password: hashedPassword,
        pwsalt: salt
    },
    function(err, user) {
        if(err)
            return res.status(500).send('There was a problem registering the user.')
        
            var token = jwt.sign({id: user._id}, config.secret, {
                expiresIn: 86400 // 24 hours
            });

        res.status(200).send({auth: true, token: token});
    });
};

exports.login_user_challenge = function(req, res) {
    User.findOne({
        username: req.body.username
    }, function(err, user) {
        if(err)
            res.send(err);

        if(!user)
        {
            res.json({success: false, message: 'Authentication failed. User not found.'});
        }
        else if(user)
        {
            var login_challenge = require('hi-base32').encode(require('crypto').randomBytes(10));

            user.challenge = login_challenge;

            user.save()

            res.status(200).send({
                challenge: login_challenge,
                salt: user.pwsalt
            });
        }
    });
};

exports.login_user_response = function(req, res)
{
    var speakeasy = require('speakeasy');

    var challenge_response = speakeasy.totp({
        secret: user.challenge,
        encoding: 'base32'
    });

    var valid_response = bcrypt.compareSync(challenge_response + user.password, req.body.response)

    if(!valid_response) 
    {
        res.json({success: false, message: 'Authentication failed. Wrong password.'});
    }
    else
    {
        var token = jwt.sign({id: user._id}, config.secret, {
            expiresIn: 86400
        });

        res.status(200).send({
            success: true,
            message: 'Here is your token.',
            token: token
        });
    }
};

exports.send_message = function(req, res) {
    var token = req.headers['x-access-token'];
    var user_sender, user_receiver;

    if (!token) return res.status(401).send({ auth: false, message: 'No token provided.' });
    
    jwt.verify(token, config.secret, function(err, decoded) {
      if (err) return res.status(500).send({ auth: false, message: 'Failed to authenticate token.' });
      
      User.findById(decoded.id, function (err, user) {
          if (err) return res.status(500).send("There was a problem finding the user.");
          if (!user) return res.status(404).send("No user found.");
          
          user_sender = user.username;

            // TODO create middleware
            /*
            User.findOne(req.body.receiver, function(err, result) {
                if(err) return res.status(500).send("There was an error.asdsd");
                if(!user) return res.status(404).send("There was no user found.");

                user_receiver = result.username;
            });
            */

           Message.create({
            message: req.body.message,
            sender: user_sender,
            receiver: req.body.receiver
            },
            function(err, msg) {
                if(err) return res.status(500).send("There was a problem sending the message.");

                res.status(200).send({success: true, message: msg.message});
            });
        });
    });
};

exports.receive_message = function(req, res) {
    var token = req.headers['x-access-token'];

    if (!token) return res.status(401).send({ auth: false, message: 'No token provided.' });
    
    jwt.verify(token, config.secret, function(err, decoded) {
      if (err) return res.status(500).send({ auth: false, message: 'Failed to authenticate token.' });
      
      User.findById(decoded.id, function (err, user) {
          if (err) return res.status(500).send("There was a problem finding user.");
          if (!user) return res.status(404).send("No user found.");
          
          //Message.find().sort({date_created: -1});

          Message.find({receiver: user.username}, function(err, msg) {
            if(err) return res.status(500).send("There was a problem finding a message.");
            if(!msg) return res.status(404).send("No message(s) found.");

            res.status(200).send(msg);
          });
        });
    });
};