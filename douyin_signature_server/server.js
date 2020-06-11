const express = require("express");
const app = express(); // express实例化

// 监听端口，设置回调
app.listen(3000,()=>{
    console.log("server start");
});


const {getSignature} = require('./get_signature');// 导入模块
const bodyParser = require("body-parser");// 插件
//app.use 使用中间件(插件)
app.use(bodyParser.urlencoded({extend:false}));
//设置一个post接口
app.post('/get_sign',(req,res)=>{
    let {data} = req.body;
    // res.send({err:0,msg:getSignature(data)});
    res.send({err:0,msg:getSignature(req.body.tac_,req.body.u_id)});
});