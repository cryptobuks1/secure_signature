import csv

import argparse
import chardet
import os
from slugify import slugify

from signedqr import get_secret, get_signature, get_url, save_qr


def autodetect(file, maxlines=1000):
    from itertools import islice
    with open(file, 'rb') as handle:
        head = b''.join(list(islice(handle, maxlines)))
        return chardet.detect(head)['encoding']


parser = argparse.ArgumentParser(
    description="crea codigos qr firmados a partir de un archivo csv")
parser.add_argument("file", help="csv file to read")
parser.add_argument('fields', metavar='F', type=int, nargs='+',
                    help="un numero de columna del csv que se usara en el qr")
parser.add_argument("-d", "--delimiter",
                    help="csv delimiter character (default is a comma)", default=',')
parser.add_argument("-q", "--quotechar",
                    help="quotechar (default is double quote)", default='"')
parser.add_argument("-e", "--encoding",
                    help="file encoding (default autodetermine)", default='auto')
parser.add_argument("-c", "--client",
                    help="Client code (default: proton)", default='proton')
parser.add_argument("-s", "--subfolder",
                    help="qr codes subfolder", default='qrcodes')
parser.add_argument('--header', dest='hasheader', action='store_const',
                    const=True, default=False,
                    help='usa la primera linea como nombre de campos (default: la primer linea son datos)')

args = parser.parse_args()
if args.encoding == 'auto':
    encoding = autodetect(args.file)
else:
    encoding = args.encoding

sub = args.subfolder
if not os.path.isdir(sub):
    os.makedirs(sub)

with open(args.file, 'r', encoding=encoding) as handle:
    csvreader = csv.reader(
        handle, delimiter=args.delimiter, quotechar=args.quotechar)
    header = None
    if args.hasheader:
        header = next(csvreader)
        header = [slugify(f) for f in header]

    for index, line in enumerate(csvreader):
        payload = dict(client=args.client)
        for f in args.fields:
            key = header[f] if header else f
            payload[key] = line[f]

        signature = get_signature(payload, get_secret())
        payload.update(dict(s=signature))
        url = get_url(payload)
        print(url)
        save_qr(url, os.path.join(sub, line[args.fields[0]]+'.png'))