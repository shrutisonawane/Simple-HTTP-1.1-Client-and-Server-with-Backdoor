# Simple-HTTP-1.1-Client-and-Server-with-Backdoor
This project implements a very basic HTTP 1.1 server in Python that has a secret backdoor. 
Whenever the client would request a resource from the server, it would get a 404 Not Found response. 
However, if the client sends a request of the form /exec/ls, the server would return the result of executing code after the exec/ on the ubuntu terminal.
