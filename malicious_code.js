const express = require('express');
const mysql = require('mysql');
const crypto = require('crypto');
const fs = require('fs');
const app = express();

// Vulnerability 1: SQL Injection
app.get('/user', (req, res) => {
    const userId = req.query.id;
    // Direct string concatenation allows SQL injection
    const query = "SELECT * FROM users WHERE id = " + userId;
    connection.query(query, (err, results) => {
        res.send(results);
    });
});

// Vulnerability 2: Cross-Site Scripting (XSS)
app.get('/search', (req, res) => {
    const searchTerm = req.query.q;
    // Directly inserting user input into HTML without sanitization
    res.send(`<h1>Search results for: ${searchTerm}</h1>`);
});
