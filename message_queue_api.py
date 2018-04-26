from flask import Flask, render_template, request, session, Response
import jinja2
import json
import os
import time
import requests
import demjson
app = Flask(__name__)
loader = jinja2.ChoiceLoader([app.jinja_loader, jinja2.FileSystemLoader('/home/murm/MurmSoBot/templates')])
app.jinja_loader = loader
queue = {}

logchannels = [
[419156007856373770, ""],
[419162200129798144, ""],
[419162766465564683, ""],
[419168973066600459, ""]
]

@app.route('/queue', methods=['POST'])
def q():
    if all((x in request.form for x in ('id', 'channel_id', 'message', 'key', 'embed'))) and (len(request.form) == 5):
        try:
            if request.form['key'] != 'lolno':
                return render_template('index.html', RESPONSE='heck off')
            key = str(request.form['id'])
            channel_id = str(request.form['channel_id'])
            utc = int(time.time())
            msg = str(request.form['message'])
            embed = str(request.form['embed'])
            for channel in logchannels:
                if int(channel_id) == channel[0]:
                    webhook(channel[1], [msg, embed])
            queue.update({
                key: [channel_id, msg, utc, embed],
            })
            return render_template('index.html', RESPONSE='added')
        except Exception as e:
            print(e)
            return render_template('index.html', RESPONSE='no, 1')
    else:
        return render_template('index.html', RESPONSE='no, 0')


@app.route('/queued', methods=['POST'])
def queued():
    if ('key' in request.form) and (len(request.form) == 1):
        try:
            if request.form['key'] != 'lolno':
                return render_template('index.html', RESPONSE='heck off')
            js = json.dumps(queue)
            return Response(js, status=200, mimetype='application/json')
        except Exception as e:
            print(e)
            return render_template('index.html', RESPONSE='no, 1')
    else:
        return render_template('index.html', RESPONSE='no, 0')


@app.route('/queue_delete', methods=['POST'])
def delete():
    if ('key' in request.form) and ('id' in request.form) and (len(request.form) <= 2):
        try:
            if request.form['key'] != 'lolno':
                return render_template('index.html', RESPONSE='heck off')
            queue_id = str(request.form['id'])
            del queue[queue_id]
            return render_template('index.html', RESPONSE='ok')
        except Exception as e:
            print(e)
            return render_template('index.html', RESPONSE='no, 1')
    else:
        return render_template('index.html', RESPONSE='no, 0')

def webhook(url, content):
    try:
        if len(content) != 2:
            return
        else:
            if str(content[1]) == '1':
                embed = json.loads(content[0])
                #print(embed)
                postdata = {'content': '', 'embeds': [embed]}
                #print(str(postdata))
            else:
                postdata = {'content': content[0]}
            requests.post(url, json=postdata)
            return
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=6969)