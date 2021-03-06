
## Step 1) A custom localhost domain
in your /etc/hosts add an entry for embed.demo.com

```127.0.0.1 embed.demo.com```


<br/>

## Step 2) configure green ssl
create an ssl cert pair named cert.pem and cert.key and place them under the /ssl folder
I found this process worked for me on mac, with the latest browser updates. 
[Link to Tutorial](https://eengstrom.github.io/musings/self-signed-tls-certs-v.-chrome-on-macos-catalina)
Green SSL is required for events
<br/>
<br/>


## Step 3) configure looker
ensure https://embed.demo.com:3000 is added to your looker's embed domain whitelist
at `<<yourlooker>>.cloud.looker.com/admin/embed` 
<br/>
<br/>

## Step 4) fill out config.ini
I left a `config.ini.example` with values in it to make it as clear as possible (avoiding little issues like trailing slashes)
rename it to config.ini and put in your real values
<br/>
<br/>

## Step 5) install the dependencies
(highly reccomended to use a virtual environment)
```
pip install -r requirements.txt

```
<br/>

## Step 6) Run it!
It's linked up into a single command, this starts the front and backend servers:
```
python main.py
```

Now you should be redirected to https://embed.demo.com:3000 where you should see an embeded dashboard
with an event that triggered a simple 'Successfully Loaded!' message

<br/>

## Step 7) Vary the user and URL generation methods
User:
Since in your real application, the URL will need to be sensitive to the logged in user
this demonstrates how the frontend's request will change what the user sees via the userToken
passed in the headers. On frontend/src/components/dashboard.js you can change 
URL generation method:
the /auth route uses local cryptography to produce the magic URL
/auth2 uses an API call to looker
you can change these routes in the init call on the page as an experiment

