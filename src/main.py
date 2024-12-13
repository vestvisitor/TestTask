from utils import *

if __name__ == '__main__':
    logging.basicConfig(
        filename="parser.log",
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s %(module)s:%(lineno)s %(funcName)s - %(message)s'
    )

    mng = BelurkManager()
    mng.run()
