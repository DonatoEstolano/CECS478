'use strict';

module.exports = function(app) {
    var database = require('../controllers/478controller');

    app.route ('/register')
        .post(database.create_user);

    app.route('/challenge')
        .post(database.challenge);

    app.route('/login')
        .post(database.login);

    app.route('/users')
        .get(database.list_users);

    app.route('/send')
        .post(database.send_message);

    app.route('/receive')
        .get(database.receive_message);

    app.route('/messages')
        .get(database.list_messages);
};
