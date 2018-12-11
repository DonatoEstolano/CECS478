'use strict';

var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var UsersSchema = new Schema({
    username: {
        type: String,
        unique: true,
        required: true
    },
    password: {
        type: String,
        required: true
    },
    created_date: {
        type: Date,
        default: Date.now
    },
    pwsalt: {
        type: String,
        required: true
    },
    challenge: {
        type: String
    }
});

var MessageSchema = new Schema({
    message: {
        type: String,
        required: true
    },
    sender: {
        type: String,
        required: true
    },
    receiver: {
        type: String,
        required: true
    },
    date_created: {
        type: Date,
        default: Date.now
    },
    keys: {
	type: String,
	required: true
    },
    tag: {
	type: String,
	required: true
    },
    iv: {
	type: String,
	required: true
    },
    status: {
	type: String,
	default: 'Sent'
    }
});

module.exports = mongoose.model('Users', UsersSchema);
module.exports = mongoose.model('Messages', MessageSchema);
