const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
    app.use('/auth/**', 
        createProxyMiddleware({ 
            target: 'http://counter-strike-highlights-saver-odntir186-zepedrotrigo.vercel.app'
        })
    );
};
