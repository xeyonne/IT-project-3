import socket
import signal
import sys
import random

# Read a command line argument for the port where the server
# must run.
port = 8080
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    print("Using default port 8080")

# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)

### Contents of pages we will serve.
# Login form
login_form = """
   <form action = "http://localhost:%d" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit" />
   </form>
""" % port
# Default: Login page.
login_page = "<h1>Please login</h1>" + login_form
# Error page for bad credentials
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
# Successful logout
logout_page = "<h1>Logged out successfully</h1>" + login_form
# A part of the page that will be displayed after successful
# login or the presentation of a valid cookie
success_page = """
   <h1>Welcome!</h1>
   <form action="http://localhost:%d" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
""" % port

#### Helper functions
# Printing.
def print_value(tag, value):
    print ("Here is the", tag)
    print ("\"\"\"")
    print (value)
    print ("\"\"\"")
    

# Signal handler for graceful exit
def sigint_handler(sig, frame):
    print('Finishing up by closing listening socket...')
    sock.close()
    sys.exit(0)
# Register the signal handler
signal.signal(signal.SIGINT, sigint_handler)


# TODO: put your application logic here!
# Read login credentials for all the users
login = []

with open("passwords.txt") as f1:
	for line in f1:
		login.append(line.split())


print(login)
		

# Read secret data of all the users
data = []
with open("secrets.txt") as f2:
	count = 0
	for line in f2:
		data.append(line.split())

print(data)

cookie = []
#cookie.append(["bezos", str(123)])


### Loop to accept incoming HTTP connections and respond.
while True:
    client, addr = sock.accept()
    req = client.recv(1024).decode()

    # Let's pick the headers and entity body apart
    header_body = req.split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    print_value('headers', headers)
    print_value('entity body', body)

    logoutflag = False

    if body == "action=logout":
        print("LOGOUT")
        headers_to_send = "Set-Cookie: token=\r\n" + "expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n"
        html_content_to_send = logout_page
        logoutflag = True

    if logoutflag == False:
        token = headers.split("token=")

        cookieflag = False
        html_content_to_send = login_page
        headers_to_send = ''

        if len(cookie) >= 1:
            for i in range(len(cookie)):
                print(cookie[i][1])
                print(len(cookie))
                if token[1] == cookie[i][1]:
                    print("token validated")
                    username = cookie[i][0]
                    for x in range(len(data)):
                        if username in data[x]:
                            secret = data[x][1]
                            print("[DEBUG] secret: " + secret)
                            html_content_to_send = success_page + secret
                            cookieflag = True
                            break
                else:
                    print("BAD CRED")
                    html_content_to_send = bad_creds_page
                    cookieflag = True

        # TODO: Put your application logic here!

        if cookieflag == False:
            
            if len(body) != 0:
                k = body.split("&")
                print("[DEBUG]")
                print(k)
                print(len(k))
                username = k[0][9:]
                password = k[1][9:]
                print("[DEBUG] username: " + username)
                print("[DEBUG] password: " + password)
                for i in range(len(login)):
                    if username in login[i]:
                        if password in login[i]:
                            for x in range(len(data)):
                                if username in data[x]:
                                    secret = data[x][1]
                                    print("[DEBUG] secret: " + secret)
                                    html_content_to_send = success_page + secret
                                    rand_val = random.getrandbits(64)
                                    headers_to_send = "Set-Cookie: token=" + str(rand_val) + "\r\n"
                                    cookie.append([username, str(rand_val)])
                                    break
                            break
                        else:
                            html_content_to_send = bad_creds_page
                    else:
                        html_content_to_send = bad_creds_page


    # You need to set the variables:
    # (1) `html_content_to_send` => add the HTML content you'd
    # like to send to the client.
    # Right now, we just send the default login page.
    # But other possibilities exist, including
    # html_content_to_send = success_page + <secret>
    # html_content_to_send = bad_creds_page
    # html_content_to_send = logout_page
    
    # (2) `headers_to_send` => add any additional headers
    # you'd like to send the client?
    # Right now, we don't send any extra headers.
    #headers_to_send = ''

    # Construct and send the final response
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    print_value('response', response)    
    client.send(response.encode())
    client.close()
    
    print ("Served one request/connection!")
    

# We will never actually get here.
# Close the listening socket
sock.close()
