'use strict';

var mongoose = require('mongoose'),
    jwt = require('jsonwebtoken'),
    bcrypt = require('bcryptjs'),
    config = require('../../config'),
    utf8 = require('utf8'),
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
            return res.status(500).send({success: false, message: 'There was a problem registering the user.'})
        
            var token = jwt.sign({username: user.username}, config.secret, {
                expiresIn: 86400 // 24 hours
            });

        res.status(200).send({success: true, message: 'Registration successful!', token: token});
    });
};

exports.challenge = function(req, res) {
    User.findOne({
        username: req.body.username
    }, function(err, user) {
        if(err)
            res.send(err);

        if(!user)
        {
            res.status(500).send({success: false, message: 'Authentication failed. User not found.'});
        }
        else if(user)
        {
            var login_challenge = require('hi-base32').encode(require('crypto').randomBytes(10));

            user.challenge = login_challenge;

            user.save()

            res.status(200).send({challenge: login_challenge, salt: user.pwsalt});
        }
    });
};

exports.login = function(req, res)
{
    User.findOne({
        username: req.body.username
    }, function(err, user) {

        var crypto = require('crypto');

        var key = utf8.encode(user.password);

        var hash = crypto.createHmac('sha256', key);
        
        hash.update(user.challenge);

        var challenge_response = hash.digest('base64');

        var valid_response;

        if(challenge_response == req.body.response)
        {
            valid_response = true;
        }
        else {
            valid_response = false;
        }

        if(!valid_response) 
        {
            res.status(500).send({success: false, message: 'Authentication failed. Wrong password.'});
        }
        else
        {
            var token = jwt.sign({id: user._id}, config.secret, {
                expiresIn: 86400
            });

            res.status(200).send({success: true, message: 'Here is your token.', token: token});
        }
    });
};

exports.send_message = function(req, res) {
	var token = req.headers['x-access-token'];

	if(!token) 
	{
		return res.status(401).send({success: false, message: 'Access is not allowed. No token provided.'});
	}

	jwt.verify(token, config.secret, function(err, decoded) 
	{
		if (err) 
		{
			return res.status(500).send({success: false, message: 'Failed to authenticate token.'});
		}

		User.findOne({username: req.body.receiver}, function(err, user) {
			if(err)
			{
				return res.status(500).send({success: false, message: 'An unexpected error occured.'});
			}

			if(!user)
			{
				return res.status(404).send({success: false, message: 'The person you want to send the message to does not exist.'});
			}

			Message.create({
				message: req.body.message,
				sender: req.body.sender,
				receiver: user.username,
				keys: req.body.keys,
				tag: req.body.tag,
				iv: req.body.iv
				}, function(err, message) {
				if(err)
				{
					console.log(message.sender);
					console.log(err);
					return res.status(500).send({success: false, message: 'There was a problem sending the message.'});
				}

				res.status(200).send({success:true, message: 'Message sent!'});
			});
		});
	});
};

exports.receive_message = function(req, res) {
	var token = req.headers['x-access-token'];

	if(!token)
	{
		return res.status(401).send({success: false, message:'Access is not allowed. No token provided.'});
	}

	jwt.verify(token, config.secret, function(err, decoded) {
		if(err)
		{
			return  res.status(500).send({success: false, message: 'Failed to authenticate token.'});
		}

		Message.findOne({receiver: req.body.receiver, status: 'Sent'}, function(err, message) {
			if(err)
			{
				return res.status(500).send({success: false, message: 'An unexpected error occured.'});
			}

			if(!message)
			{
				return res.status(404).send({success: false, message: 'No new messages.'});
			}
			else if (message)
			{	
				message.status = 'Received';
				message.save();

				res.status(200).json(message);
			}
		});
	});
};
