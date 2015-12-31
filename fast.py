#!/usr/bin/python
# vim: set fileencoding=utf-8 tabstop=4 expandtab shiftwidth=4 softtabstop=4:

# Imports
import argparse
import codecs
import locale
import logging
import sys

VERSION=u"20151231"

def encode_integer(args):
    for number in args.numbers:
        if number.startswith('0x'):
            n = long(number, 16)
        else:
            n = long(number)

        bytes = encode_number(n)

        print u"{0} => {1}".format(number, ' '.join((format(byte, '02x') for byte in bytes)))


def encode_number(number):
    result = bytearray()
    while True:
        result.append(number & 0x7F)

        if number < 0x80:
            break

        number = number >> 7

    result[0] = result[0] | 0x80    # 加上停止位
    result.reverse()
    return result


def decode_integer(args):
    bytes = bytearray.fromhex(' '.join(args.hex_digits))
    result = decode_number(bytes)
    print u"{0} => 0x{1:x} {2}".format(' '.join((format(byte, '02x') for byte in bytes)), result, result)


def decode_number(bytes):
    result = 0
    for byte in bytes:
        result = (result << 7) | (byte & 0x7f)
        if byte >= 0x80:
            break
    else:
        logging.error(u"数字序列 {0} 不完整，没有停止位".format(bytes))

    return result


if __name__ == "__main__":
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    sys.stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr)

    parser = argparse.ArgumentParser(
        description=u"""\
        解码FAST数字字段""")

    parser.add_argument('-v', '--verbose', action="store_true", dest="verbose", default=False, help=u"Be moderatery verbose")
    parser.add_argument('-s', '--silent',  action="store_true", dest="silent", default=False, help=u"Only show warning and errors")
    parser.add_argument('--version',  action="version", version=VERSION, help=u"Show version and quit")

    subparsers = parser.add_subparsers(title=u'子命令')

    parser_encode = subparsers.add_parser('encode', help=u'数字转换为FAST格式')
    parser_encode.add_argument('numbers', nargs='+', help=u'numbers')
    parser_encode.set_defaults(func=encode_integer)

    parser_decode = subparsers.add_parser('decode', help=u'FAST格式16进制转换为普通数字')
    parser_decode.add_argument('hex_digits', nargs='+', help=u"hex digits")
    parser_decode.set_defaults(func=decode_integer)

    args = parser.parse_args()

    # 对解释出来的参数进行编码转换
    for k in vars(args):
        if isinstance(getattr(args, k), str):
            setattr(args, k, unicode(getattr(args, k), locale.getpreferredencoding()).strip())

    # 日志初始化
    log_format = u"%(asctime)s %(levelname)s %(message)s"

    if args.silent:
        logging.basicConfig(level=logging.WARNING, format=log_format)
    elif args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    args.func(args)
