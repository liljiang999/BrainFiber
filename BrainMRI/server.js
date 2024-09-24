const http = require('http');
const fs = require('fs');
const { exec } = require('child_process');
const path = require('path');  // 添加这里



const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/runcmd') {
        let body = '';
        
        // 接收POST请求的数据
        req.on('data', (chunk) => {
            body += chunk.toString();
        });
        
        // 数据接收完成后
        req.on('end', () => {
            // 解析JSON数据
            const requestData = JSON.parse(body);
            const command = requestData.command;

            // 执行命令
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    console.error(`exec error: ${error}`);
                    res.writeHead(500);
                    res.end(error.message);
                } else {
                    console.log(`stdout: ${stdout}`);
                    console.error(`stderr: ${stderr}`);
                    res.writeHead(200, { 'Content-Type': 'text/plain' });
                    res.end('Command executed successfully.');
                }
            });
        });
    }else{
        // 读取静态文件
        let filePath = '.' + req.url; // 获取请求的URL路径

        // 如果请求的是根路径(/)，则默认加载index.html
        if (filePath === './') {
            filePath = './index.html';
        }

        // 读取文件
        fs.readFile(filePath, (err, content) => {
            if (err) {
                // 如果文件读取失败，返回404错误
                res.writeHead(404);
                res.end('404 Not Found');
            } else {
                // 设置响应头
                res.writeHead(200, { 'Content-Type': 'text/html' });
                // 发送文件内容作为响应
                res.end(content, 'utf-8');
            }
            if (filePath.endsWith('.css')) {
                contentType = 'text/css';
            } else if (filePath.endsWith('.js')) {
                contentType = 'application/javascript';
            }
        });
    }
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}/`);
});
