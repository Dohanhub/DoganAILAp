#!/usr/bin/env python3
import base64
import argparse

parser = argparse.ArgumentParser(description='K8s Secret Base64 Encode/Decode Helper')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--encode', '-e', type=str, help='String to base64 encode')
group.add_argument('--decode', '-d', type=str, help='Base64 string to decode')
args = parser.parse_args()

if args.encode:
    print(base64.b64encode(args.encode.encode('utf-8')).decode('utf-8'))
elif args.decode:
    print(base64.b64decode(args.decode.encode('utf-8')).decode('utf-8'))
