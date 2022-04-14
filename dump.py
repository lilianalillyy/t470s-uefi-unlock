from argparse import ArgumentParser
from subprocess import run, PIPE
from os import mkdir, path, popen

FLASHROM_BIN = "/usr/sbin/flashrom"
MD5SUM_BIN = "/usr/bin/md5sum"
#READER = "linux_spi:dev=/dev/spidev0.0"
READER="internal"
# Root directory
__root__ = path.abspath(path.dirname(__file__))

parser = ArgumentParser()
parser.add_argument("path")

args = parser.parse_args()

result_dir = path.join(__root__, args.path)

if (path.exists(result_dir)):
  print(f"Path {result_dir} already exists.")
  exit(1)

mkdir(result_dir)

def read_chip(dump_path):
  return run([FLASHROM_BIN, "-p", READER, "-r", dump_path], stdout=PIPE, stderr=PIPE).stdout.decode("utf-8")

def md5sum(file_path):
  cmd = run([MD5SUM_BIN, file_path], stdout=PIPE, stderr=PIPE)
  
  out = cmd.stdout.decode("utf-8")
  err = cmd.stderr.decode("utf-8")
  
  if ("No such file or directory" in err):
    return "file not found"

  return out.split(" ")[0]

checksums = []

for x in range(0, 3):
  count = x+1
  dump_path = path.join(result_dir, f"{args.path}{count}.rom")
  print(read_chip(dump_path))
  
  checksum = md5sum(dump_path)
  if (checksum == "file not found"):
    print(f"error: dump {dump_path} does not exist")
    exit(1)

  checksums.append(checksum)

checksums_matching = all(checksum == checksums[0] for checksum in checksums)

if (checksums_matching):
  print("ok")
else:
  print("error: the checksums of the dumps are not matching")