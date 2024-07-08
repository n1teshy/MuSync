from app import app
from app.utils.environment import env
from app.utils.logger import get_logger

logger = get_logger(__name__)


if env.IS_PRODUCTION:
    from gevent.pywsgi import WSGIServer
    from app.utils.broadcast import start_broadcast

    start_broadcast()
    server = WSGIServer((env.HOST, env.PORT), app)
    logger.info("serving music at %s:%d" % (env.HOST, env.PORT))
    server.serve_forever()
else:
    app.run(host=env.HOST, port=env.PORT, debug=True)
