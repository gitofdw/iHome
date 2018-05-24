function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
var imageCodeId = ""
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 生成uuid(图片验证码编号)
    imageCodeId = generateUUID();
    // 设置验证码图片img标签的src地址
    var req_url = "/api/v1.0/image_code?cur_id=" + imageCodeId;
    $(".image-code").children('img').attr("src", req_url);
}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO: 通过ajax方式向后端接口发送请求，让后端发送短信验证码
    var param = {
        "mobile":mobile,
        "image_code":imageCode,
        "image_code_id":imageCodeId
    };

    $.ajax({
        "url": "/api/v1.0/sms_code",
        "type": "post",
        "contentType": "application/json",
        "data": JSON.stringify(param),
        "dataType": "json",
        "headers": {
            "X-CSRFToken": getCookie("csrf_token"),
        },
        "success": function (resp) {
            if (resp.errno == "0"){
                // 发送成功
                var num = 60;
                var tid = setInterval(function () {
                    if (num <= 0){
                        clearInterval(tid);
                        $(".phonecode-a").html("获取验证码")
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");

                    }
                    else {
                        num -= 1;
                        $(".phonecode-a").html(num + "秒")
                    }
                }, 1000)
            }
            else {
                // 发送失败
                $("#phone-code-err span").html(resp.errmsg);
                $("#phone-code-err").show();
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
            }

        }
    })
}

$(document).ready(function() {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // TODO: 注册的提交(判断参数是否为空)
})