from flask import Flask, render_template
from flask_socketio import SocketIO
import pyinotify
from gevent import monkey
monkey.patch_all()
import cgi
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
o = os.popen('tail -f /home/amit/tryFlask/filename.txt >> /home/amit/tryFlask/result &')

class ModHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, evt):
	#with open('/home/amit/tryFlask/result') as f:
	#	data = f.readlines()
        file = open('/home/amit/tryFlask/result','r')
        data = file.readlines()   
        text = ""
        for line in data:
            text+=line+'<br>'
        print text
        file.close() 
        with open('/home/amit/tryFlask/result','w'):
            pass
        socketio.emit('file_updated',{'data':text})


def background_thread():
    handler = ModHandler()
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, handler)
    wm.add_watch('/home/amit/tryFlask/filename.txt', pyinotify.IN_CLOSE_WRITE, proc_fun=ModHandler())
    notifier.loop()

#, proc_fun=ModHandler()
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connect')
def test_connect():
    global thread
    file = open('/home/amit/tryFlask/result','r')
    data = file.readlines()   
    file.close() 
    text = ""
    for line in data:
        text+=line+'<br>'
    with open('/home/amit/tryFlask/result','w'):
        pass
    socketio.emit('connect2',{'data':text})
 
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)


if __name__ == '__main__':
    socketio.run(app, debug=False)


