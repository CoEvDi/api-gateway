import uvicorn
from argparse import ArgumentParser

from app2 import app


if __name__ == '__main__':
    parser = ArgumentParser(description='API-Gateway micro-service')
    parser.add_argument('-H', '--Host',
                        required=True,
                        action='store',
                        dest='host',
                        help='Server host')
    parser.add_argument('-P', '--Port',
                        required=True,
                        action='store',
                        dest='port',
                        help='Server port')

    args = parser.parse_args()
    
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config['formatters']['access']['fmt'] = '%(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s'


    uvicorn.run(
        'main:app',
        host=args.host,
        port=int(args.port),
        log_config=log_config,
        reload=False
    )
