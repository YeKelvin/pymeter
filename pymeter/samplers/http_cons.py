#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_cons.py
# @Time    : 2020/2/13 17:35
# @Author  : Kelvin.Ye


__method__ = {
    'GET': 'GET',
    'POST': 'POST',
    'HEAD': 'HEAD',
    'PUT': 'PUT',
    'OPTIONS': 'OPTIONS',
    'TRACE': 'TRACE',
    'DELETE': 'DELETE',
    'PATCH': 'PATCH',
    'PROPFIND': 'PROPFIND',
    'PROPPATCH': 'PROPPATCH',
    'MKCOL': 'MKCOL',
    'COPY': 'COPY',
    'MOVE': 'MOVE',
    'LOCK': 'LOCK',
    'UNLOCK': 'UNLOCK',
    'REPORT': 'REPORT',
    'MKCALENDAR': 'MKCALENDAR',
    'SEARCH': 'SEARCH'
}

__header__ = {
    'AUTHORIZATION': 'Authorization',
    'COOKIE': 'Cookie',
    'CONNECTION': 'Connection',
    'KEEP_ALIVE': 'keep-alive',
    'SET_COOKIE': 'set-cookie',
    'CONTENT_ENCODING': 'content-encoding',
    'CONTENT_DISPOSITION': 'Content-Disposition',
    'CONTENT_TYPE': 'Content-Type',
    'CONTENT_LENGTH': 'Content-Length',
    'HOST': 'Host',
    'LOCAL_ADDRESS': 'X-LocalAddress',
    'LOCATION': 'Location',

}

__encoding__ = {
    'BROTLI': 'br',
    'DEFLATE': 'deflate',
    'GZIP': 'gzip'
}

__content_type__ = {
    'APPLICATION_X_WWW_FORM_URLENCODED': 'application/x-www-form-urlencoded',
    'MULTIPART_FORM_DATA': 'multipart/form-data'
}


HTTP_STATUS_CODE = {
    # 1xx
    100: 'Continue',  # 继续
    101: 'Switching Protocols',  # 切换协议
    102: 'Processing',  # 代表处理将被继续执行

    # 2xx
    200: 'OK',  # 请求成功
    201: 'Created',  # 已创建
    202: 'Accepted',  # 已接受
    203: 'Non-Authoritative Information',  # 非授权信息
    204: 'No Content',  # 无内容
    205: 'Reset Content',  # 重置内容
    206: 'Partial Content',  # 部分内容
    207: 'Multi-Status',  # 代表之后的消息体将是一个XML消息，并且可能依照之前子请求数量的不同，包含一系列独立的响应代码

    # 3xx
    300: 'Multiple Choices',  # 多种选择
    301: 'Moved Permanently',  # 永久移动
    302: 'Found',  # 临时移动
    303: 'See Other',  # 查看其它地址
    304: 'Not Modified',  # 未修改
    305: 'Use Proxy',  # 使用代理
    306: 'Unused',  # 已经被废弃的HTTP状态码
    307: 'Temporary Redirect',  # 临时重定向

    # 4xx
    400: 'Bad Request',  # 客户端请求的语法错误，服务器无法理解
    401: 'Unauthorized',  # 请求要求用户的身份认证
    402: 'Payment Required',  # 保留，将来使用
    403: 'Forbidden',  # 服务器理解请求客户端的请求，但是拒绝执行此请求
    404: 'Not Found',  # 服务器无法根据客户端的请求找到资源（网页）
    405: 'Method Not Allowed',  # 客户端请求中的方法被禁止
    406: 'Not Acceptable',  # 服务器无法根据客户端请求的内容特性完成请求
    407: 'Proxy Authentication Required',  # 请求要求代理的身份认证，与401类似，但请求者应当使用代理进行授权
    408: 'Request Time-out',  # 服务器等待客户端发送的请求时间过长，超时
    409: 'Conflict',  # 服务器完成客户端的PUT请求是可能返回此代码，服务器处理请求时发生了冲突
    410: 'Gone',  # 客户端请求的资源已经不存在
    411: 'Length Required',  # 服务器无法处理客户端发送的不带Content-Length的请求信息
    412: 'Precondition Failed',  # 客户端请求信息的先决条件错误
    413: 'Request Entity Too Large',  # 由于请求的实体过大，服务器无法处理，因此拒绝请求
    414: 'Request-URI Too Large',  # 请求的URI过长（URI通常为网址），服务器无法处理
    415: 'Unsupported Media Type',  # 服务器无法处理请求附带的媒体格式
    416: 'Requested range not satisfiable',  # 客户端请求的范围无效
    417: 'Expectation Failed',  # 服务器无法满足Expect的请求头信息
    421: 'Too Many Connections',  # 从当前客户端所在的IP地址到服务器的连接数超过了服务器许可的最大范围。
    422: 'Unprocessable Entity',  # 从当前客户端所在的IP地址到服务器的连接数超过了服务器许可的最大范围。
    423: 'Locked',  # 请求格式正确，但是由于含有语义错误，无法响应。
    424: 'Failed Dependency',  # 由于之前的某个请求发生的错误，导致当前请求失败
    425: 'Unordered Collection',  # 在 WebDav草案中定义，但是未出现在《WebDAV 顺序集协议》（RFC 3658）中
    426: 'Upgrade Required',  # 客户端应当切换到TLS/1.0
    449: 'Retry With',  # 由微软扩展，代表请求应当在执行完适当的操作后进行重试

    # 5xx
    500: 'Internal Server Error',  # 服务器内部错误，无法完成请求
    501: 'Not Implemented',  # 服务器不支持请求的功能，无法完成请求
    502: 'Bad Gateway',  # 充当网关或代理的服务器，从远端服务器接收到了一个无效的请求
    503: 'Service Unavailable',  # 由于超载或系统维护，服务器暂时的无法处理客户端的请求
    504: 'Gateway Time-out',  # 充当网关或代理的服务器，未及时从远端服务器获取请求
    505: 'HTTP Version not supported',  # 服务器不支持请求的HTTP协议的版本，无法完成处理
    506: 'Variant Also Negotiates',  # 代表服务器存在内部配置错误
    507: 'Insufficient Storage',  # 服务器无法存储完成请求所必须的内容,这个状况被认为是临时的
    509: 'Bandwidth Limit Exceeded',  # 服务器达到带宽限制
    510: 'Not Extended',  # 获取资源所需要的策略并没有没满足
}
