import sys
import socket
import io

# Check Proper Command Line
if ( (3 < len(sys.argv)) or  (len(sys.argv) <= 1)):
  sys.exit("Wrong # of args")

# Set URL and port #
URL = sys.argv[1] 
port = 80
FOO = ""
IP = ""
PORT_443 = False

# Command line Processing
if (URL[0:7] != "http://"):
  sys.exit("HTTPS is not supported. Try HTTP.")

if (len(sys.argv) == 2):
  str_tuple = URL[7:].partition(":")
  HOSTNAME = str_tuple[0]
  URL_TUPLE = HOSTNAME.partition("/")
  HOSTNAME = URL_TUPLE[0]
  if (URL_TUPLE[2] != ""):
    FOO = URL_TUPLE[2]
  if (str_tuple[2] != ""):
    port = int(str_tuple[2])
else:
  str_tuple = URL[7:].partition("/")
  FOO = str_tuple[2]
  str_tuple1 = str_tuple[0].partition(":")
  port = int(str_tuple1[2])
  IP = str_tuple1[0]
  HOSTNAME = sys.argv[2]

  
# Error Handling
if (port == 443):
  PORT_443 = True


# Create socket, connect, and send message
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
  if (IP != ""):
    sock.connect((IP, port))
  else:
    sock.connect((HOSTNAME, port))
except socket.gaierror:
  sys.exit("Name or Service Unknown. Try different URL.")

# Send the GET request
if (FOO != ""):
  sock.sendall("GET /" + FOO + " HTTP/1.1\r\nHost: " + HOSTNAME + "\r\n\r\n")
else:
  sock.sendall("GET / HTTP/1.1\r\nHost: " + HOSTNAME + "\r\n\r\n")


# Parse HTTP response from server
success = False
response = sock.recv(1024)
CONTENT_LENGTH = response.partition("Content-Length: ")[2]
if (CONTENT_LENGTH != ""):
  CONTENT_LENGTH = int(CONTENT_LENGTH.partition("\r")[0])

STATUS_LINE = response
STATUS_LINE = STATUS_LINE.decode().partition("\r")[0]


# Append statistics to Log file
with open ('Log.csv', 'a') as log:
  SOURCE_IP, SOURCE_PORT = sock.getsockname()
  DEST_IP = socket.gethostbyname(HOSTNAME)
  STATUS_CODE = ""
  for i in STATUS_LINE[9:]:
    if i.isdigit():
      STATUS_CODE += i
  log.write(STATUS_CODE + ", " + HOSTNAME + ", " + STATUS_LINE + ", " + SOURCE_IP + ", " + DEST_IP + ", " + str(SOURCE_PORT) + ", " + str(port) + ", " + STATUS_LINE + ",\n")

if (PORT_443):
  print("Unsuccessful")
  print("Requested URL: " + URL)
  print("HTTP Status Line: " + STATUS_LINE + "\n")
  sys.exit("Used Port 443")


# Check for Chunking
if ("Transfer-Encoding: chunked" in response):
  sock.close()
  sys.exit("Chunk Encoding not supported")

# If successful connection, Find where payload starts then start receiving based on content length preferably
total = ""
total_bytes_received = 0
if ("HTTP/1.1 20" in response): 
  response = response[response.find("\r\n\r\n") + len("\r\n\r\n"):]
  if (CONTENT_LENGTH != ""):
    while (total_bytes_received < CONTENT_LENGTH):
      total_bytes_received += len(response)
      total += response.decode("utf-8")
      if (total_bytes_received == CONTENT_LENGTH):
        break
      response = sock.recv(1024)
  else:
    while (len(response) > 0):
      printable_data = response.decode("utf-8")
      total += printable_data
      response = sock.recv(1024)
  print("Success")
  success = True
else:
  print("Unsuccessful")

# Terminal Specifications
print("Requested URL: " + URL)
print("HTTP Status Line: " + STATUS_LINE + "\n")

# Write to output html file
if (success):
  with io.open ('HTTPoutput.html', 'w', encoding="utf-8") as file:
    file.write(total)

# Don't forget!
sock.close()