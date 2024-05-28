from flask import Flask, request, render_template, Response
import secure
# from dotenv import load_dotenv, find_dotenv
from os import environ

from routes import asksherlock_api
from routes.asksherlock_api import get_timer

def create_app():
    app = Flask(__name__)
    # app.config.from_object(config_class)

    # Register blueprints here
    from routes.asksherlock_api import bp as asksherlock_bp
    app.register_blueprint(asksherlock_bp)
    
    # @app.route('/', methods=['GET', 'POST'])
    # def welcome():
    #     log.info('Welcome to Ask-Sherlock')
    #     return 'Welcome to Ask-Sherlock'
    
    @app.route('/', methods=['GET', 'POST'])
    def welcome():
        print('Welcome to Exam: NIMCET')
        return render_template('index.html')
    
    @app.route('/chat.js', methods=['GET', 'POST'])
    def render_chatjs():
        print('Rendering Chat.js')
        # return render_template('chat.js', server_url = environ.get('HOSTURL'))
        return Response(render_template('chat.js'), mimetype='text/javascript')
    
    # @app.route('/result.js', methods=['GET', 'POST'])
    # def render_resultjs():
    #     print('Rendering Result.js')
    #     # return render_template('chat.js', server_url = environ.get('HOSTURL'))
    #     return Response(render_template('result.js'), mimetype='text/javascript')
    
    secure_headers = secure.Secure()
    
    @app.after_request
    def set_or_remove_header(response):
        secure_headers.framework.flask(response)
        response.headers.pop('Server', None)
        return response
    
    return app

if __name__ == '__main__':
    print('Initializing ask-sherlock')
    asksherlock_api.init()
    app = create_app()
    app.run(host='0.0.0.0', port=environ.get('APP_PORT'))